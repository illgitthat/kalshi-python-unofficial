import urllib.parse
import requests
import json
import inspect
import time
from datetime import datetime, timedelta

# Simple built-in rate limiter (100ms between calls)
_last_call_time = datetime.now()
_THRESHOLD_MS = 100


def _rate_limit():
	global _last_call_time
	now = datetime.now()
	threshold_delta = timedelta(milliseconds=_THRESHOLD_MS)
	if now - _last_call_time < threshold_delta:
		time.sleep(_THRESHOLD_MS / 1000)
	_last_call_time = datetime.now()


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
    _rate_limit()
    for i in kwargs:
        if isinstance(kwargs[i], bool):
            kwargs[i] = str(kwargs[i]).lower()
    response = requests.get(url, params=kwargs, headers=headers)
    if response.status_code != 200:
        raise Exception(response.content.decode())
    return json.loads(response.content)


def post(url, headers=None, json=None):
    _rate_limit()
    response = requests.post(url, headers=headers, json=json)
    if response.status_code != 201:
        raise Exception(response.content.decode())
    return json.loads(response.content)


def delete(url, headers=None, json=None):
    _rate_limit()
    response = requests.delete(url, headers=headers, json=json)
    if response.status_code != 200:
        raise Exception(response.content.decode())
    return json.loads(response.content)
