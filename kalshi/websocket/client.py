import json
import logging

import websockets

import kalshi.auth

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Client:
    """
    A WebSocket client for connecting to the Kalshi trade API.
    """

    def __init__(self):
        """
        Initialize the Client with a message ID counter.
        """
        self.message_id = 0
        self.ws = None

    async def connect(self, url="wss://api.elections.kalshi.com/trade-api/ws/v2"):
        """
        Connect to the WebSocket server.

        :param url: The WebSocket endpoint to connect to (default = wss://api.elections.kalshi.com/trade-api/ws/v2).
        """
        logger.info("Attempting to connect to WebSocket: %s", url)
        async with websockets.connect(
            url,
            extra_headers=kalshi.auth.request_headers("GET", url),
        ) as websocket:
            self.ws = websocket
            logger.info("Connected to WebSocket: %s", url)
            await self.on_open()
            await self.handler()

    async def on_open(self):
        """
        Called immediately after a successful WebSocket connection.
        Override this method to implement custom logic upon opening.
        """
        logger.debug("WebSocket connection opened.")

    async def on_message(self, message: dict):
        """
        Called whenever a new message is received.
        Override this method to implement custom processing logic.

        :param message: The message payload received from the server as a dict.
        """
        logger.debug("Received message: %s", str(message))

    async def on_error(self, error):
        """
        Called when an exception occurs during WebSocket communication.
        Override this method to implement custom error handling.

        :param error: The exception caught during WebSocket operation.
        """
        logger.error("An error occurred: %s", error)

    async def on_close(self, close_status_code, close_msg):
        """
        Called when the WebSocket connection is closed.
        Override this method for custom close/cleanup logic.

        :param close_status_code: The WebSocket close status code (if provided).
        :param close_msg: The reason provided for closing (if any).
        """
        logger.warning(
            "WebSocket connection closed with code=%s, message=%s",
            close_status_code,
            close_msg,
        )

    async def subscribe(self, channels: list[str], tickers: list[str] = []):
        """
        Subscribe to one or more channels, optionally specifying market tickers.

        :param channels: A list of channel names to subscribe to.
        :param tickers: An optional list of market ticker strings.
        """
        subscription_message = {
            "id": self.message_id,
            "cmd": "subscribe",
            "params": {"channels": channels},
        }
        if tickers:
            subscription_message["params"]["market_tickers"] = tickers

        logger.info(
            "Subscribing with message_id=%s to channels=%s, tickers=%s",
            self.message_id,
            channels,
            tickers,
        )

        await self.ws.send(json.dumps(subscription_message))
        self.message_id += 1
        logger.debug(
            "Subscription message sent. Incremented message_id to %s",
            self.message_id,
        )

    async def handler(self):
        """
        Main loop that listens for messages on the WebSocket.
        It calls `on_message` for each received message and handles errors and closure.
        """
        try:
            async for message in self.ws:
                await self.on_message(json.loads(message))
        except websockets.ConnectionClosed as e:
            await self.on_close(e.code, e.reason)
        except Exception as e:
            await self.on_error(e)
