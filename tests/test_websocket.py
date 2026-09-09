import asyncio
import json

from kalshi.websocket import Client, KalshiWebSocketError


class FakeWebSocket:
    def __init__(self):
        self.messages = []
        self.closed = None

    async def send(self, message):
        self.messages.append(json.loads(message))

    async def close(self, code=None, reason=None):
        self.closed = (code, reason)


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


def test_non_orderbook_subscription_omits_orderbook_price_option():
    async def run():
        client = Client()
        client.ws = FakeWebSocket()

        await client.subscribe(["market_lifecycle_v2"])

        assert client.ws.messages[0]["params"] == {"channels": ["market_lifecycle_v2"]}

    asyncio.run(run())


def test_protocol_reports_sequence_gaps_and_structured_errors():
    async def run():
        client = RecordingClient()

        await client._handle_protocol_message(
            {"type": "orderbook_delta", "sid": 3, "seq": 10, "msg": {}}
        )
        await client._handle_protocol_message(
            {"type": "orderbook_delta", "sid": 3, "seq": 12, "msg": {}}
        )
        await client._handle_protocol_message(
            {"type": "orderbook_delta", "sid": 3, "seq": 13, "msg": {}}
        )
        await client._handle_protocol_message(
            {"type": "orderbook_snapshot", "sid": 3, "seq": 20, "msg": {}}
        )
        await client._handle_protocol_message(
            {"type": "orderbook_delta", "sid": 3, "seq": 21, "msg": {}}
        )
        await client._handle_protocol_message(
            {
                "type": "error",
                "id": 7,
                "sid": 3,
                "msg": {"code": 25, "msg": "buffer overflow"},
            }
        )

        assert client.gaps[0][1] == 11
        assert len(client.gaps) == 1
        assert [message["seq"] for message in client.messages] == [10, 20, 21]
        assert isinstance(client.errors[0], KalshiWebSocketError)
        assert client.errors[0].code == 25

    asyncio.run(run())


def test_default_orderbook_gap_handler_requests_a_snapshot():
    async def run():
        client = Client()
        client.ws = FakeWebSocket()

        await client.on_sequence_gap(
            {"type": "orderbook_delta", "sid": 7, "seq": 12},
            expected_sequence=11,
        )

        assert client.ws.messages == [
            {
                "id": 1,
                "cmd": "update_subscription",
                "params": {"sid": 7, "action": "get_snapshot"},
            }
        ]

    asyncio.run(run())
