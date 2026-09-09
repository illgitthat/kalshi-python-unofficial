from fastkalshi import constants


def test_environment_switches_rest_and_websocket_hosts():
    constants.use_prod()
    assert constants.BASE_URL == "https://external-api.kalshi.com"
    assert constants.WEBSOCKET_URL == "wss://external-api-ws.kalshi.com/trade-api/ws/v2"

    constants.use_legacy_demo()
    assert constants.BASE_URL == "https://demo-api.kalshi.co"
    assert constants.WEBSOCKET_URL == "wss://demo-api.kalshi.co/trade-api/ws/v2"

    constants.use_demo()
