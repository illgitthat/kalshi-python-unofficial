import urllib.parse
import requests
import json
import inspect
import time
from datetime import datetime, timedelta

# Rate limiter for advanced access tier: Read 30/sec, Write 30/sec
_last_read_call_time = datetime.now()
_last_write_call_time = datetime.now()
_READ_THRESHOLD_MS = 33  # 1000ms / 30 = 33ms between read calls
_WRITE_THRESHOLD_MS = 33  # 1000ms / 30 = 33ms between write calls

# Reuse a single session so subsequent requests can reuse pooled connections.
SESSION = requests.Session()


def _rate_limit_read():
    global _last_read_call_time
    now = datetime.now()
    threshold_delta = timedelta(milliseconds=_READ_THRESHOLD_MS)
    if now - _last_read_call_time < threshold_delta:
        time.sleep(_READ_THRESHOLD_MS / 1000)
    _last_read_call_time = datetime.now()


def _rate_limit_write():
    global _last_write_call_time
    now = datetime.now()
    threshold_delta = timedelta(milliseconds=_WRITE_THRESHOLD_MS)
    if now - _last_write_call_time < threshold_delta:
        time.sleep(_WRITE_THRESHOLD_MS / 1000)
    _last_write_call_time = datetime.now()


def get_kwargs():
    frame = inspect.currentframe().f_back
    keys, _, _, values = inspect.getargvalues(frame)
    kwargs = {}
    for key in keys:
        if key != "self":
            kwargs[key] = values[key]
    return kwargs


def drop_none(dictionary: dict):
    return {i: dictionary[i] for i in dictionary if dictionary[i] is not None}


def _prepare_params(params: dict):
    for key in params:
        if isinstance(params[key], bool):
            params[key] = str(params[key]).lower()
    return params


def _parse_response(response, expected_status):
    if response.status_code not in expected_status:
        raise Exception(response.content.decode())
    if not response.content:
        return {}
    return json.loads(response.content)


def get(url, headers=None, expected_status=(200,), **kwargs):
    _rate_limit_read()
    response = SESSION.get(
        url, params=_prepare_params(kwargs), headers=headers
    )
    return _parse_response(response, expected_status)


def post(url, headers=None, body=None, expected_status=(200, 201)):
    _rate_limit_write()
    response = SESSION.post(url, headers=headers, json=body)
    return _parse_response(response, expected_status)


def delete(url, headers=None, body=None, expected_status=(200, 204)):
    _rate_limit_write()
    response = SESSION.delete(url, headers=headers, json=body)
    return _parse_response(response, expected_status)


def put(url, headers=None, body=None, expected_status=(200, 204)):
    _rate_limit_write()
    response = SESSION.put(url, headers=headers, json=body)
    return _parse_response(response, expected_status)
