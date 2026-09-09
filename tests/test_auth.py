from kalshi.auth import Auth


class FakeSigner:
    def __init__(self):
        self.text = None

    def sign(self, text):
        self.text = text
        return "signature"


def test_request_headers_sign_uppercase_path_without_query():
    auth = Auth()
    auth.API_ACCESS_KEY = "key-id"
    auth.signer = FakeSigner()

    headers = auth.request_headers(
        "get",
        "https://external-api.kalshi.com/trade-api/v2/portfolio/balance?subaccount=1",
    )

    assert auth.signer.text.endswith("GET/trade-api/v2/portfolio/balance")
    assert "?subaccount" not in auth.signer.text
    assert headers["KALSHI-ACCESS-KEY"] == "key-id"
    assert headers["KALSHI-ACCESS-SIGNATURE"] == "signature"
