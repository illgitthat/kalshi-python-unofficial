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


def get(url, headers=None, **kwargs):
    _rate_limit_read()
    for i in kwargs:
        if isinstance(kwargs[i], bool):
            kwargs[i] = str(kwargs[i]).lower()
    response = SESSION.get(url, params=kwargs, headers=headers)
    if response.status_code != 200:
        raise Exception(response.content.decode())
    return json.loads(response.content)


def post(url, headers=None, body=None):
    _rate_limit_write()
    response = SESSION.post(url, headers=headers, json=body)
    if response.status_code != 201:
        raise Exception(response.content.decode())
    return json.loads(response.content)


def delete(url, headers=None, body=None):
    _rate_limit_write()
    response = SESSION.delete(url, headers=headers, json=body)
    if response.status_code != 200:
        raise Exception(response.content.decode())
    return json.loads(response.content)
