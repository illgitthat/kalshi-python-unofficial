import asyncio
import inspect
import json
import logging

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
        self._subscriptions = []
        self._pending_subscription_commands = {}
        self._sequence_by_subscription = {}

    async def connect(self, url: str | None = None, *, resubscribe: bool = False):
        url = url or constants.WEBSOCKET_URL
        logger.info("Attempting to connect to WebSocket: %s", url)
        headers = request_headers("GET", url)
        connect_kwargs = {}
        signature = inspect.signature(websockets.connect)
        if "additional_headers" in signature.parameters:
            connect_kwargs["additional_headers"] = headers
        else:
            connect_kwargs["extra_headers"] = headers

        try:
            async with websockets.connect(url, **connect_kwargs) as websocket:
                self.ws = websocket
                self._sequence_by_subscription.clear()
                logger.info("Connected to WebSocket: %s", url)
                if resubscribe:
                    await self.resubscribe()
                    await self.on_reconnect()
                else:
                    await self.on_open()
                await self.handler()
        finally:
            self.ws = None

    async def run_forever(
        self,
        url: str | None = None,
        *,
        initial_delay: float = 1.0,
        max_delay: float = 30.0,
    ):
        delay = initial_delay
        reconnecting = False
        while True:
            try:
                await self.connect(url, resubscribe=reconnecting)
                reconnecting = True
                delay = initial_delay
            except asyncio.CancelledError:
                raise
            except (OSError, WebSocketException) as error:
                await self.on_error(error)
                reconnecting = True
            await asyncio.sleep(delay)
            delay = min(delay * 2, max_delay)

    async def on_open(self):
        logger.debug("WebSocket connection opened.")

    async def on_reconnect(self):
        logger.debug("WebSocket connection restored.")

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

    async def _send_command(self, command: str, params: dict | None = None):
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
        market_ticker: str | None = None,
        market_ids: list[str] | None = None,
        market_id: str | None = None,
        send_initial_snapshot: bool | None = None,
        skip_ticker_ack: bool | None = None,
        use_yes_price: bool = True,
        shard_factor: int | None = None,
        shard_key: int | None = None,
        index_ids: list[str] | None = None,
        underlying_tickers: list[str] | None = None,
        remember: bool = True,
    ):
        market_selectors = [
            bool(tickers),
            market_ticker is not None,
            bool(market_ids),
            market_id is not None,
        ]
        if sum(market_selectors) > 1:
            raise ValueError("provide only one market selector")
        if shard_key is not None and shard_factor is None:
            raise ValueError("shard_factor is required with shard_key")

        params = {"channels": channels}
        optional = {
            "market_tickers": tickers,
            "market_ticker": market_ticker,
            "market_ids": market_ids,
            "market_id": market_id,
            "shard_factor": shard_factor,
            "shard_key": shard_key,
            "index_ids": index_ids,
            "underlying_tickers": underlying_tickers,
            "send_initial_snapshot": send_initial_snapshot,
            "skip_ticker_ack": skip_ticker_ack,
        }
        params.update(
            {key: value for key, value in optional.items() if value is not None}
        )
        if "orderbook_delta" in channels:
            params["use_yes_price"] = use_yes_price
        command_id = await self._send_command("subscribe", params)
        if remember:
            subscription = {"params": params.copy(), "sid": None}
            self._subscriptions.append(subscription)
            self._pending_subscription_commands[command_id] = subscription
        return command_id

    async def resubscribe(self):
        self._pending_subscription_commands.clear()
        for subscription in self._subscriptions:
            subscription["sid"] = None
            command_id = await self._send_command(
                "subscribe",
                subscription["params"],
            )
            self._pending_subscription_commands[command_id] = subscription

    async def unsubscribe(self, subscription_ids: list[int]):
        command_id = await self._send_command(
            "unsubscribe",
            {"sids": subscription_ids},
        )
        subscription_ids = set(subscription_ids)
        self._subscriptions = [
            subscription
            for subscription in self._subscriptions
            if subscription["sid"] not in subscription_ids
        ]
        return command_id

    async def list_subscriptions(self):
        return await self._send_command("list_subscriptions")

    async def update_subscription(
        self,
        subscription_id: int,
        action: str,
        *,
        market_ticker: str | None = None,
        market_tickers: list[str] | None = None,
        market_id: str | None = None,
        market_ids: list[str] | None = None,
        send_initial_snapshot: bool = False,
    ):
        params = {
            "sid": subscription_id,
            "action": action,
            "send_initial_snapshot": send_initial_snapshot,
        }
        optional = {
            "market_ticker": market_ticker,
            "market_tickers": market_tickers,
            "market_id": market_id,
            "market_ids": market_ids,
        }
        params.update(
            {key: value for key, value in optional.items() if value is not None}
        )
        command_id = await self._send_command("update_subscription", params)
        if action in {"add_markets", "delete_markets"}:
            self._update_remembered_subscription(
                subscription_id,
                action,
                market_ticker=market_ticker,
                market_tickers=market_tickers,
                market_id=market_id,
                market_ids=market_ids,
            )
        return command_id

    def _update_remembered_subscription(
        self,
        subscription_id: int,
        action: str,
        **selectors,
    ):
        subscription = next(
            (item for item in self._subscriptions if item["sid"] == subscription_id),
            None,
        )
        if subscription is None:
            return

        params = subscription["params"]
        for key, value in selectors.items():
            if value is None:
                continue
            values = value if isinstance(value, list) else [value]
            plural_key = key if key.endswith("s") else f"{key}s"
            remembered = list(params.get(plural_key, []))
            if action == "add_markets":
                remembered.extend(item for item in values if item not in remembered)
            else:
                remembered = [item for item in remembered if item not in values]
            params.pop(key, None)
            if remembered:
                params[plural_key] = remembered
            else:
                params.pop(plural_key, None)

    async def handler(self):
        try:
            async for raw_message in self.ws:
                message = json.loads(raw_message)
                await self._handle_protocol_message(message)
        except websockets.ConnectionClosed as error:
            await self.on_close(error.code, error.reason)

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

        if message.get("type") == "subscribed":
            subscription = self._pending_subscription_commands.pop(
                message.get("id"),
                None,
            )
            if subscription is not None:
                subscription["sid"] = (message.get("msg") or {}).get("sid")

        subscription_id = message.get("sid")
        sequence = message.get("seq")
        if subscription_id is not None and sequence is not None:
            previous = self._sequence_by_subscription.get(subscription_id)
            if previous is not None and sequence != previous + 1:
                await self.on_sequence_gap(message, previous + 1)
            self._sequence_by_subscription[subscription_id] = sequence

        await self.on_message(message)
