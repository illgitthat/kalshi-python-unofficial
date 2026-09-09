import asyncio
import logging
from typing import Any

import orjson
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
        self._sequence_by_subscription = {}

    async def connect(self, url: str | None = None):
        url = url or constants.WEBSOCKET_URL
        headers = request_headers("GET", url)
        try:
            async with websockets.connect(
                url,
                additional_headers=headers,
                compression=None,
            ) as websocket:
                self.ws = websocket
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

    async def send_command(self, command: str, params: dict | None = None):
        if self.ws is None:
            raise RuntimeError("WebSocket is not connected")
        command_id = self.message_id
        self.message_id += 1
        message = {"id": command_id, "cmd": command}
        if params is not None:
            message["params"] = params
        await self.ws.send(orjson.dumps(message).decode())
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
            try:
                message = orjson.loads(raw_message)
            except orjson.JSONDecodeError:
                await self.on_error(
                    KalshiWebSocketError("Invalid JSON received from Kalshi")
                )
                await websocket.close(
                    code=1002,
                    reason="Invalid JSON",
                )
                return
            if not isinstance(message, dict):
                await self.on_error(
                    KalshiWebSocketError("Invalid message received from Kalshi")
                )
                await websocket.close(
                    code=1002,
                    reason="Invalid message",
                )
                return
            await self._handle_protocol_message(message)

    async def _handle_protocol_message(self, message: dict):
        subscription_id = message.get("sid")
        sequence = message.get("seq")
        if subscription_id is not None and sequence is not None:
            previous = self._sequence_by_subscription.get(subscription_id)
            if previous is not None and sequence != previous + 1:
                await self.on_sequence_gap(message, previous + 1)
                if self.ws is not None:
                    await self.ws.close(
                        code=1011,
                        reason="WebSocket sequence gap",
                    )
                return
            self._sequence_by_subscription[subscription_id] = sequence

        if message.get("type") == "error":
            payload = message.get("msg") or {}
            await self.on_error(
                KalshiWebSocketError(
                    payload.get("msg", "Kalshi WebSocket error"),
                    code=payload.get("code"),
                    command_id=message.get("id"),
                    subscription_id=subscription_id,
                )
            )
            if payload.get("code") == 25 and self.ws is not None:
                await self.ws.close(
                    code=1011,
                    reason="WebSocket subscription buffer overflow",
                )
            return

        await self.on_message(message)
