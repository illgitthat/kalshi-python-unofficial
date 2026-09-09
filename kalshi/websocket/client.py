import asyncio
import inspect
import json
import logging
from typing import Any

import websockets
from websockets.exceptions import WebSocketException

from kalshi import constants
from kalshi.auth import request_headers

logger = logging.getLogger(__name__)


class KalshiWebSocketError(RuntimeError):
    def __init__(
        self,
        message: str,
        *,
        code: int | None = None,
        command_id: int | None = None,
        subscription_id: int | None = None,
    ):
        super().__init__(message)
        self.code = code
        self.command_id = command_id
        self.subscription_id = subscription_id


class Client:
    def __init__(self):
        self.message_id = 1
        self.ws = None
        self._resyncing_subscriptions = set()
        self._sequence_by_subscription = {}

    async def connect(self, url: str | None = None):
        url = url or constants.WEBSOCKET_URL
        headers = request_headers("GET", url)
        if "additional_headers" in inspect.signature(websockets.connect).parameters:
            connection = websockets.connect(url, additional_headers=headers)
        else:
            connection = websockets.connect(  # type: ignore[call-arg]
                url,
                extra_headers=headers,
            )

        try:
            async with connection as websocket:
                self.ws = websocket
                self._resyncing_subscriptions.clear()
                self._sequence_by_subscription.clear()
                await self.on_open()
                await self.handler()
        except websockets.ConnectionClosed as error:
            await self.on_close(error.code, error.reason)
        finally:
            self.ws = None

    async def run_forever(
        self,
        url: str | None = None,
        *,
        reconnect_delay: float = 1.0,
    ):
        while True:
            try:
                await self.connect(url)
            except asyncio.CancelledError:
                raise
            except (OSError, WebSocketException) as error:
                await self.on_error(error)
            await asyncio.sleep(reconnect_delay)

    async def on_open(self):
        logger.debug("WebSocket connection opened.")

    async def on_message(self, message: dict):
        logger.debug("Received message: %s", message)

    async def on_error(self, error):
        logger.error("An error occurred: %s", error)

    async def on_close(self, close_status_code, close_msg):
        logger.warning(
            "WebSocket connection closed with code=%s, message=%s",
            close_status_code,
            close_msg,
        )

    async def on_sequence_gap(
        self,
        message: dict,
        expected_sequence: int,
    ):
        logger.warning(
            "WebSocket sequence gap for sid=%s: expected=%s, received=%s",
            message.get("sid"),
            expected_sequence,
            message.get("seq"),
        )
        if message.get("type") == "orderbook_delta":
            await self.send_command(
                "update_subscription",
                {"sid": message["sid"], "action": "get_snapshot"},
            )
        elif self.ws is not None:
            await self.ws.close(
                code=1011,
                reason="WebSocket sequence gap",
            )

    async def send_command(self, command: str, params: dict | None = None):
        if self.ws is None:
            raise RuntimeError("WebSocket is not connected")
        message = {"id": self.message_id, "cmd": command}
        if params is not None:
            message["params"] = params
        await self.ws.send(json.dumps(message))
        command_id = self.message_id
        self.message_id += 1
        return command_id

    async def subscribe(
        self,
        channels: list[str],
        tickers: list[str] | None = None,
        *,
        use_yes_price: bool = True,
        **options: Any,
    ):
        params: dict[str, Any] = {"channels": channels}
        params.update(options)
        if tickers:
            if "market_tickers" in options:
                raise ValueError("provide tickers or market_tickers, not both")
            params["market_tickers"] = tickers
        if "orderbook_delta" in channels:
            params["use_yes_price"] = use_yes_price
        return await self.send_command("subscribe", params)

    async def handler(self):
        websocket = self.ws
        if websocket is None:
            raise RuntimeError("WebSocket is not connected")
        async for raw_message in websocket:
            await self._handle_protocol_message(json.loads(raw_message))

    async def _handle_protocol_message(self, message: dict):
        if message.get("type") == "error":
            payload = message.get("msg") or {}
            await self.on_error(
                KalshiWebSocketError(
                    payload.get("msg", "Kalshi WebSocket error"),
                    code=payload.get("code"),
                    command_id=message.get("id"),
                    subscription_id=message.get("sid"),
                )
            )
            return

        subscription_id = message.get("sid")
        sequence = message.get("seq")
        if subscription_id is not None and sequence is not None:
            if message.get("type") == "orderbook_snapshot":
                self._resyncing_subscriptions.discard(subscription_id)
                self._sequence_by_subscription[subscription_id] = sequence
                await self.on_message(message)
                return
            if subscription_id in self._resyncing_subscriptions:
                return
            previous = self._sequence_by_subscription.get(subscription_id)
            if previous is not None and sequence != previous + 1:
                if message.get("type") == "orderbook_delta":
                    self._resyncing_subscriptions.add(subscription_id)
                await self.on_sequence_gap(message, previous + 1)
                return
            self._sequence_by_subscription[subscription_id] = sequence

        await self.on_message(message)
