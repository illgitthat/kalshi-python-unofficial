import inspect
import json
import time
from typing import Any

import requests

SESSION = requests.Session()
DEFAULT_TIMEOUT = 10.0
READ_RETRIES = 2
BACKOFF_FACTOR = 0.25
RETRYABLE_READ_STATUSES = {429, 502, 503, 504}


class KalshiAPIError(requests.HTTPError):
    def __init__(
        self,
        status_code: int,
        message: str,
        *,
        code: str | None = None,
        details: Any = None,
        response: requests.Response | None = None,
    ):
        super().__init__(
            f"Kalshi API error {status_code}: {message}", response=response
        )
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details


def configure(
    *,
    timeout: float | None = None,
    read_retries: int | None = None,
    backoff_factor: float | None = None,
) -> None:
    global DEFAULT_TIMEOUT, READ_RETRIES, BACKOFF_FACTOR
    if timeout is not None:
        if timeout <= 0:
            raise ValueError("timeout must be greater than zero")
        DEFAULT_TIMEOUT = timeout
    if read_retries is not None:
        if read_retries < 0:
            raise ValueError("read_retries cannot be negative")
        READ_RETRIES = read_retries
    if backoff_factor is not None:
        if backoff_factor < 0:
            raise ValueError("backoff_factor cannot be negative")
        BACKOFF_FACTOR = backoff_factor


def get_kwargs():
    frame = inspect.currentframe().f_back
    keys, _, _, values = inspect.getargvalues(frame)
    return {key: values[key] for key in keys if key != "self"}


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
    message = error.get("message") or response.text or response.reason
    return KalshiAPIError(
        response.status_code,
        message,
        code=error.get("code"),
        details=error.get("details"),
        response=response,
    )


def request(
    method: str,
    url: str,
    *,
    headers: dict | None = None,
    params: dict | None = None,
    body: dict | list | None = None,
    timeout: float | None = None,
):
    method = method.upper()
    query = {
        key: _query_value(value)
        for key, value in (params or {}).items()
        if value is not None
    }
    retries = READ_RETRIES if method == "GET" else 0

    for attempt in range(retries + 1):
        response = SESSION.request(
            method,
            url,
            params=query or None,
            headers=headers,
            json=body,
            timeout=DEFAULT_TIMEOUT if timeout is None else timeout,
        )
        if response.status_code in RETRYABLE_READ_STATUSES and attempt < retries:
            time.sleep(BACKOFF_FACTOR * (2**attempt))
            continue
        if not 200 <= response.status_code < 300:
            raise _parse_error(response)
        if response.status_code == 204 or not response.content:
            return None
        return response.json()

    raise RuntimeError("unreachable")


def get(url, headers=None, **kwargs):
    return request("GET", url, headers=headers, params=kwargs)


def post(url, headers=None, body=None, **kwargs):
    return request("POST", url, headers=headers, params=kwargs, body=body)


def put(url, headers=None, body=None, **kwargs):
    return request("PUT", url, headers=headers, params=kwargs, body=body)


def delete(url, headers=None, body=None, **kwargs):
    return request("DELETE", url, headers=headers, params=kwargs, body=body)
