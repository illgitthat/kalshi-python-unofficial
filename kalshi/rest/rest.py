import urllib.parse
import requests
import json
import inspect


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
    for i in kwargs:
        if isinstance(kwargs[i], bool):
            kwargs[i] = str(kwargs[i]).lower()
    response = requests.get(url, params=kwargs, headers=headers)
    if response.status_code != 200:
        raise Exception(response.content.decode())
    return json.loads(response.content)


def post(url, headers=None, json=None):
    response = requests.post(url, headers=headers, json=json)
    if response.status_code != 201:
        raise Exception(response.content.decode())
    return json.loads(response.content)


def delete(url, headers=None, json=None):
    response = requests.delete(url, headers=headers, json=json)
    if response.status_code != 200:
        raise Exception(response.content.decode())
    return json.loads(response.content)
