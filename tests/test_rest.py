from unittest.mock import Mock

import pytest
import requests

from kalshi.rest import rest


def response(status, payload=None, *, text="", reason=""):
    result = Mock()
    result.status_code = status
    result.content = b"" if payload is None else b"json"
    result.text = text
    result.reason = reason
    result.json.return_value = payload
    return result


def test_request_accepts_empty_success(monkeypatch):
    monkeypatch.setattr(
        rest.SESSION,
        "request",
        Mock(return_value=response(204)),
    )

    assert rest.request("DELETE", "https://example.test/orders") is None


def test_request_raises_structured_api_error(monkeypatch):
    monkeypatch.setattr(
        rest.SESSION,
        "request",
        Mock(
            return_value=response(
                400,
                {
                    "error": {
                        "code": "invalid_request",
                        "message": "Bad request",
                        "details": {"field": "price"},
                    }
                },
            )
        ),
    )

    with pytest.raises(rest.KalshiAPIError) as caught:
        rest.request("POST", "https://example.test/orders", body={})

    assert caught.value.status_code == 400
    assert caught.value.code == "invalid_request"
    assert caught.value.details == {"field": "price"}
    assert caught.value.payload["error"]["message"] == "Bad request"


def test_request_does_not_retry_failures(monkeypatch):
    request = Mock(
        return_value=response(
            503,
            {"error": {"message": "unavailable"}},
        )
    )
    monkeypatch.setattr(rest.SESSION, "request", request)

    with pytest.raises(rest.KalshiAPIError):
        rest.request("GET", "https://example.test/markets")
    assert request.call_count == 1


@pytest.mark.parametrize(
    ("method", "outcome_unknown"),
    [("GET", False), ("POST", True), ("DELETE", True)],
)
def test_transport_errors_mark_uncertain_mutations(
    monkeypatch,
    method,
    outcome_unknown,
):
    request = Mock(side_effect=requests.Timeout("timed out"))
    monkeypatch.setattr(rest.SESSION, "request", request)

    with pytest.raises(rest.KalshiTransportError) as caught:
        rest.request(method, "https://example.test/orders")

    assert caught.value.outcome_unknown is outcome_unknown
    assert request.call_count == 1


def test_boolean_query_values_are_lowercase(monkeypatch):
    request = Mock(return_value=response(200, {}))
    monkeypatch.setattr(rest.SESSION, "request", request)

    rest.get("https://example.test/events", with_nested_markets=True)

    assert request.call_args.kwargs["params"] == {"with_nested_markets": "true"}
    assert request.call_args.kwargs["allow_redirects"] is False
