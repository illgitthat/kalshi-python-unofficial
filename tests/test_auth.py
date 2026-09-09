import base64

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa

from fastkalshi.auth import Auth


def test_request_headers_sign_uppercase_path_without_query(tmp_path):
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    key_path = tmp_path / "kalshi-key.pem"
    key_path.write_bytes(
        private_key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption(),
        )
    )
    auth = Auth()
    auth.set_key("key-id", str(key_path))

    headers = auth.request_headers(
        "get",
        "https://external-api.kalshi.com/trade-api/v2/portfolio/balance?subaccount=1",
    )

    signed_text = (
        headers["KALSHI-ACCESS-TIMESTAMP"] + "GET" + "/trade-api/v2/portfolio/balance"
    )
    private_key.public_key().verify(
        base64.b64decode(headers["KALSHI-ACCESS-SIGNATURE"]),
        signed_text.encode(),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.DIGEST_LENGTH,
        ),
        hashes.SHA256(),
    )
    assert headers["KALSHI-ACCESS-KEY"] == "key-id"
