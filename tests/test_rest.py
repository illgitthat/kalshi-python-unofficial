from unittest.mock import Mock

import pytest

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


def test_get_retries_retryable_status_without_retrying_writes(monkeypatch):
    get_request = Mock(
        side_effect=[
            response(429, {"error": {"message": "slow down"}}),
            response(200, {"markets": []}),
        ]
    )
    monkeypatch.setattr(rest.SESSION, "request", get_request)
    monkeypatch.setattr(rest.time, "sleep", Mock())

    assert rest.request("GET", "https://example.test/markets") == {"markets": []}
    assert get_request.call_count == 2

    post_request = Mock(
        return_value=response(
            503,
            {"error": {"message": "unavailable"}},
        )
    )
    monkeypatch.setattr(rest.SESSION, "request", post_request)

    with pytest.raises(rest.KalshiAPIError):
        rest.request("POST", "https://example.test/orders", body={})
    assert post_request.call_count == 1


def test_boolean_query_values_are_lowercase(monkeypatch):
    request = Mock(return_value=response(200, {}))
    monkeypatch.setattr(rest.SESSION, "request", request)

    rest.get("https://example.test/events", with_nested_markets=True)

    assert request.call_args.kwargs["params"] == {"with_nested_markets": "true"}
