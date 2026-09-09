import base64
import datetime
import urllib.parse

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa


class Signer:
    def __init__(self, private_key_file: str, key_password: bytes | None = None):
        self._private_key: rsa.RSAPrivateKey = self._load_private_key_from_file(
            private_key_file, key_password
        )

    def _load_private_key_from_file(
        self, file_path: str, password: bytes | None = None
    ):
        with open(file_path, "rb") as key_file:
            private_key = serialization.load_pem_private_key(
                key_file.read(),
                password=None,
                backend=default_backend(),
            )
        return private_key

    def sign(self, text: str) -> str:
        message = text.encode("utf-8")
        try:
            signature = self._private_key.sign(
                message,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.DIGEST_LENGTH,
                ),
                hashes.SHA256(),
            )
            return base64.b64encode(signature).decode("utf-8")
        except InvalidSignature as e:
            raise ValueError("RSA sign PSS failed") from e


class Auth:
    def __init__(self):
        self.API_PRIVATE_KEY_PATH = None
        self.API_ACCESS_KEY = None
        self.signer = None

    def set_key(self, access_key: str, private_key_path: str) -> None:
        self.API_PRIVATE_KEY_PATH = private_key_path
        self.API_ACCESS_KEY = access_key
        self.signer = Signer(self.API_PRIVATE_KEY_PATH)

    def request_headers(self, method: str, url: str):
        if self.signer is None:
            raise RuntimeError(
                "Kalshi credentials not configured. Call auth.set_key(...) before making requests."
            )
        timestamp = datetime.datetime.now(datetime.timezone.utc).timestamp()
        current_time_milliseconds = int(timestamp * 1000)
        timestamp_str = str(current_time_milliseconds)
        path = urllib.parse.urlparse(url).path
        sig = self.signer.sign(timestamp_str + method.upper() + path)
        headers = {
            "KALSHI-ACCESS-KEY": self.API_ACCESS_KEY,
            "KALSHI-ACCESS-SIGNATURE": sig,
            "KALSHI-ACCESS-TIMESTAMP": timestamp_str,
        }
        return headers


auth = Auth()


def set_key(access_key: str, private_key_path: str) -> None:
    auth.set_key(access_key, private_key_path)


def request_headers(method: str, url: str):
    return auth.request_headers(method, url)
