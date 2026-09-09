import importlib
from unittest.mock import Mock

from fastkalshi import constants
from fastkalshi.rest import account, rest


def test_account_limit_and_endpoint_cost_authentication(monkeypatch):
    constants.use_demo()
    response = Mock(status_code=200, content=b"{}")
    request = Mock(return_value=response)
    monkeypatch.setattr(rest.SESSION, "request", request)
    module = importlib.import_module("fastkalshi.rest.account")
    monkeypatch.setattr(
        module,
        "request_headers",
        lambda method, url: {"X-Test-Auth": f"{method} {url}"},
    )

    account.GetLimits()
    limits_call = request.call_args
    account.GetEndpointCosts()
    costs_call = request.call_args

    assert limits_call.args[1].endswith("/trade-api/v2/account/limits")
    assert limits_call.kwargs["headers"]["X-Test-Auth"].startswith("GET ")
    assert costs_call.args[1].endswith("/trade-api/v2/account/endpoint_costs")
    assert costs_call.kwargs["headers"] is None
