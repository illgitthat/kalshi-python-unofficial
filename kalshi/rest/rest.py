from typing import Any

import orjson
import requests

SESSION = requests.Session()
WRITE_SESSION = requests.Session()
DEFAULT_TIMEOUT = 10.0


class KalshiAPIError(requests.HTTPError):
    def __init__(
        self,
        status_code: int,
        message: str,
        *,
        code: str | None = None,
        details: Any = None,
        payload: Any = None,
        response: requests.Response | None = None,
    ):
        super().__init__(
            f"Kalshi API error {status_code}: {message}", response=response
        )
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details
        self.payload = payload


class KalshiTransportError(requests.RequestException):
    def __init__(self, method: str, url: str):
        self.method = method
        self.url = url
        self.outcome_unknown = method not in {"GET", "HEAD", "OPTIONS"}
        super().__init__(f"Kalshi {method} request failed without a response")


def drop_none(dictionary: dict):
    return {key: value for key, value in dictionary.items() if value is not None}


def _query_value(value: Any) -> Any:
    if isinstance(value, bool):
        return str(value).lower()
    return value


def _parse_error(response: requests.Response) -> KalshiAPIError:
    try:
        payload = orjson.loads(response.content)
    except orjson.JSONDecodeError:
        payload = None

    error = payload.get("error", payload) if isinstance(payload, dict) else {}
    if not isinstance(error, dict):
        error = {}
    return KalshiAPIError(
        response.status_code,
        error.get("message") or response.text or response.reason,
        code=error.get("code"),
        details=error.get("details"),
        payload=payload,
        response=response,
    )


def request(
    method: str,
    url: str,
    *,
    headers: dict | None = None,
    params: dict | None = None,
    body: dict | list | None = None,
    timeout: float = DEFAULT_TIMEOUT,
    session: requests.Session | None = None,
):
    query = {
        key: _query_value(value)
        for key, value in (params or {}).items()
        if value is not None
    }
    method = method.upper()
    active_session = session or (
        SESSION if method in {"GET", "HEAD", "OPTIONS"} else WRITE_SESSION
    )
    try:
        response = active_session.request(
            method,
            url,
            params=query or None,
            headers=headers,
            json=body,
            timeout=timeout,
            allow_redirects=False,
        )
    except requests.RequestException as error:
        raise KalshiTransportError(method, url) from error
    if not 200 <= response.status_code < 300:
        raise _parse_error(response)
    if response.status_code == 204 or not response.content:
        return None
    return orjson.loads(response.content)


def get(url, headers=None, session=None, **kwargs):
    return request("GET", url, headers=headers, params=kwargs, session=session)


def post(url, headers=None, body=None, **kwargs):
    return request("POST", url, headers=headers, params=kwargs, body=body)


def delete(url, headers=None, body=None, **kwargs):
    return request("DELETE", url, headers=headers, params=kwargs, body=body)
