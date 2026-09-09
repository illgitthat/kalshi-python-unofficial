import asyncio
import importlib
import json

from kalshi.websocket import Client, KalshiWebSocketError


class FakeWebSocket:
    def __init__(self, incoming=None):
        self.incoming = incoming or []
        self.messages = []
        self.closed = None

    async def send(self, message):
        await asyncio.sleep(0)
        self.messages.append(json.loads(message))

    async def close(self, code=None, reason=None):
        self.closed = (code, reason)

    def __aiter__(self):
        return self._messages()

    async def _messages(self):
        for message in self.incoming:
            yield message


class RecordingClient(Client):
    def __init__(self):
        super().__init__()
        self.messages = []
        self.errors = []
        self.gaps = []

    async def on_message(self, message):
        self.messages.append(message)

    async def on_error(self, error):
        self.errors.append(error)

    async def on_sequence_gap(self, message, expected_sequence):
        self.gaps.append((message, expected_sequence))


class FakeConnection:
    def __init__(self, websocket):
        self.websocket = websocket

    async def __aenter__(self):
        return self.websocket

    async def __aexit__(self, *args):
        return False


def test_subscribe_uses_command_ids_and_explicit_yes_price():
    async def run():
        client = Client()
        client.ws = FakeWebSocket()

        command_id = await client.subscribe(
            ["orderbook_delta"],
            ["KXTEST"],
            send_initial_snapshot=True,
        )

        assert command_id == 1
        assert client.ws.messages == [
            {
                "id": 1,
                "cmd": "subscribe",
                "params": {
                    "channels": ["orderbook_delta"],
                    "send_initial_snapshot": True,
                    "use_yes_price": True,
                    "market_tickers": ["KXTEST"],
                },
            }
        ]

    asyncio.run(run())


def test_concurrent_commands_reserve_unique_ids_before_sending():
    async def run():
        client = Client()
        client.ws = FakeWebSocket()

        command_ids = await asyncio.gather(
            client.send_command("list_subscriptions"),
            client.send_command("list_subscriptions"),
        )

        assert set(command_ids) == {1, 2}
        assert {message["id"] for message in client.ws.messages} == {1, 2}

    asyncio.run(run())


def test_sequence_gap_closes_socket_without_delivering_invalid_message():
    async def run():
        client = RecordingClient()
        client.ws = FakeWebSocket()

        await client._handle_protocol_message(
            {
                "type": "orderbook_snapshot",
                "sid": 3,
                "seq": 1,
                "msg": {"market_ticker": "A"},
            }
        )
        await client._handle_protocol_message(
            {
                "type": "orderbook_snapshot",
                "sid": 3,
                "seq": 3,
                "msg": {"market_ticker": "B"},
            }
        )

        assert client.gaps[0][1] == 2
        assert [message["seq"] for message in client.messages] == [1]
        assert client.ws.closed == (1011, "WebSocket sequence gap")

    asyncio.run(run())


def test_sequenced_error_advances_sequence_before_next_delta():
    async def run():
        client = RecordingClient()
        client.ws = FakeWebSocket()

        await client._handle_protocol_message(
            {
                "type": "orderbook_snapshot",
                "sid": 3,
                "seq": 1,
                "msg": {"market_ticker": "A"},
            }
        )
        await client._handle_protocol_message(
            {
                "type": "error",
                "sid": 3,
                "seq": 2,
                "msg": {"code": 27, "msg": "too many requests"},
            }
        )
        await client._handle_protocol_message(
            {
                "type": "orderbook_delta",
                "sid": 3,
                "seq": 3,
                "msg": {"market_ticker": "A"},
            }
        )

        assert client.gaps == []
        assert [message["seq"] for message in client.messages] == [1, 3]
        assert client.errors[0].code == 27
        assert client.ws.closed is None

    asyncio.run(run())


def test_reconnect_waits_for_each_market_snapshot(monkeypatch):
    async def run():
        first = FakeWebSocket(
            incoming=[
                json.dumps(
                    {
                        "type": "orderbook_snapshot",
                        "sid": 1,
                        "seq": 1,
                        "msg": {"market_ticker": "A"},
                    }
                ),
                json.dumps(
                    {
                        "type": "orderbook_delta",
                        "sid": 1,
                        "seq": 2,
                        "msg": {"market_ticker": "A"},
                    }
                ),
            ]
        )
        second = FakeWebSocket(
            incoming=[
                json.dumps(
                    {
                        "type": "orderbook_delta",
                        "sid": 2,
                        "seq": 1,
                        "msg": {"market_ticker": "A"},
                    }
                ),
                json.dumps(
                    {
                        "type": "orderbook_snapshot",
                        "sid": 2,
                        "seq": 2,
                        "msg": {"market_ticker": "A"},
                    }
                ),
                json.dumps(
                    {
                        "type": "orderbook_delta",
                        "sid": 2,
                        "seq": 3,
                        "msg": {"market_ticker": "A"},
                    }
                ),
            ]
        )
        connections = iter([first, second])
        module = importlib.import_module("kalshi.websocket.client")
        monkeypatch.setattr(module, "request_headers", lambda method, url: {})
        monkeypatch.setattr(
            module.websockets,
            "connect",
            lambda *args, **kwargs: FakeConnection(next(connections)),
        )

        class ReconnectClient(RecordingClient):
            async def on_open(self):
                await self.subscribe(["orderbook_delta"], ["A"])

        client = ReconnectClient()
        await client.connect()
        await client.connect()

        assert [message["seq"] for message in client.messages] == [1, 2, 2, 3]
        assert first.messages[0]["cmd"] == "subscribe"
        assert second.messages[0]["cmd"] == "subscribe"

    asyncio.run(run())


def test_buffer_overflow_error_closes_socket():
    async def run():
        client = RecordingClient()
        client.ws = FakeWebSocket()

        await client._handle_protocol_message(
            {
                "type": "error",
                "sid": 3,
                "seq": 1,
                "msg": {"code": 25, "msg": "buffer overflow"},
            }
        )

        assert isinstance(client.errors[0], KalshiWebSocketError)
        assert client.ws.closed == (
            1011,
            "WebSocket subscription buffer overflow",
        )

    asyncio.run(run())


def test_malformed_json_reports_protocol_error_and_closes():
    async def run():
        client = RecordingClient()
        client.ws = FakeWebSocket(incoming=["{"])

        await client.handler()

        assert isinstance(client.errors[0], KalshiWebSocketError)
        assert client.ws.closed == (1002, "Invalid JSON")

    asyncio.run(run())


def test_invalid_message_envelope_reports_protocol_error_and_closes():
    async def run():
        client = RecordingClient()
        client.ws = FakeWebSocket(incoming=["[]"])

        await client.handler()

        assert isinstance(client.errors[0], KalshiWebSocketError)
        assert client.ws.closed == (1002, "Invalid message")

    asyncio.run(run())
