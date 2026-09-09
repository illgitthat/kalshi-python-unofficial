import json
from typing import Any

import requests

SESSION = requests.Session()
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
        payload = response.json()
    except (requests.JSONDecodeError, json.JSONDecodeError, ValueError):
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
):
    query = {
        key: _query_value(value)
        for key, value in (params or {}).items()
        if value is not None
    }
    method = method.upper()
    try:
        response = SESSION.request(
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
    return response.json()


def get(url, headers=None, **kwargs):
    return request("GET", url, headers=headers, params=kwargs)


def post(url, headers=None, body=None, **kwargs):
    return request("POST", url, headers=headers, params=kwargs, body=body)


def delete(url, headers=None, body=None, **kwargs):
    return request("DELETE", url, headers=headers, params=kwargs, body=body)
