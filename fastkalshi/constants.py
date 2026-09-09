DEMO_BASE_URL = "https://external-api.demo.kalshi.co"
PROD_BASE_URL = "https://external-api.kalshi.com"
LEGACY_DEMO_BASE_URL = "https://demo-api.kalshi.co"
LEGACY_PROD_BASE_URL = "https://api.elections.kalshi.com"
BASE_PATH = "/trade-api/v2"

DEMO_WEBSOCKET_URL = "wss://external-api-ws.demo.kalshi.co/trade-api/ws/v2"
PROD_WEBSOCKET_URL = "wss://external-api-ws.kalshi.com/trade-api/ws/v2"
LEGACY_PROD_WEBSOCKET_URL = "wss://api.elections.kalshi.com/trade-api/ws/v2"
LEGACY_DEMO_WEBSOCKET_URL = "wss://demo-api.kalshi.co/trade-api/ws/v2"

BASE_URL = DEMO_BASE_URL
WEBSOCKET_URL = DEMO_WEBSOCKET_URL


def use_demo():
    global BASE_URL, WEBSOCKET_URL
    BASE_URL = DEMO_BASE_URL
    WEBSOCKET_URL = DEMO_WEBSOCKET_URL


def use_prod():
    global BASE_URL, WEBSOCKET_URL
    BASE_URL = PROD_BASE_URL
    WEBSOCKET_URL = PROD_WEBSOCKET_URL


def use_legacy_demo():
    global BASE_URL, WEBSOCKET_URL
    BASE_URL = LEGACY_DEMO_BASE_URL
    WEBSOCKET_URL = LEGACY_DEMO_WEBSOCKET_URL


def use_legacy_prod():
    global BASE_URL, WEBSOCKET_URL
    BASE_URL = LEGACY_PROD_BASE_URL
    WEBSOCKET_URL = LEGACY_PROD_WEBSOCKET_URL


def api_url(path: str) -> str:
    return f"{BASE_URL}{BASE_PATH}/{path.lstrip('/')}"
