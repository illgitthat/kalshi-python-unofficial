import asyncio
import json

from kalshi.websocket import Client, KalshiWebSocketError


class FakeWebSocket:
    def __init__(self):
        self.messages = []

    async def send(self, message):
        self.messages.append(json.loads(message))


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
        )

        assert command_id == 1
        assert client.ws.messages == [
            {
                "id": 1,
                "cmd": "subscribe",
                "params": {
                    "channels": ["orderbook_delta"],
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


def test_unsubscribed_channels_are_not_replayed_after_reconnect():
    async def run():
        client = RecordingClient()
        client.ws = FakeWebSocket()

        command_id = await client.subscribe(["trade"], ["KXTEST"])
        await client._handle_protocol_message(
            {
                "id": command_id,
                "type": "subscribed",
                "msg": {"channel": "trade", "sid": 42},
            }
        )
        await client.unsubscribe([42])

        reconnect_socket = FakeWebSocket()
        client.ws = reconnect_socket
        await client.resubscribe()

        assert reconnect_socket.messages == []

    asyncio.run(run())


def test_protocol_reports_sequence_gaps_and_structured_errors():
    async def run():
        client = RecordingClient()

        await client._handle_protocol_message(
            {"type": "trade", "sid": 3, "seq": 10, "msg": {}}
        )
        await client._handle_protocol_message(
            {"type": "trade", "sid": 3, "seq": 12, "msg": {}}
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
        assert len(client.messages) == 2
        assert isinstance(client.errors[0], KalshiWebSocketError)
        assert client.errors[0].code == 25

    asyncio.run(run())
