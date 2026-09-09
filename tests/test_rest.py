from unittest.mock import Mock

import orjson
import pytest
import requests

from kalshi.rest import rest


def response(status, payload=None, *, text="", reason=""):
    result = Mock()
    result.status_code = status
    result.content = b"" if payload is None else orjson.dumps(payload)
    result.text = text
    result.reason = reason
    return result


def test_request_accepts_empty_success(monkeypatch):
    monkeypatch.setattr(
        rest.WRITE_SESSION,
        "request",
        Mock(return_value=response(204)),
    )

    assert rest.request("DELETE", "https://example.test/orders") is None


@pytest.mark.parametrize(
    ("method", "content"),
    [
        ("HEAD", b""),
        ("HEAD", b"ignored"),
        ("OPTIONS", b""),
    ],
)
def test_bodyless_read_responses_are_valid(monkeypatch, method, content):
    request = Mock(return_value=Mock(status_code=200, content=content))
    monkeypatch.setattr(rest.SESSION, "request", request)

    assert rest.request(method, "https://example.test/resource") is None


@pytest.mark.parametrize("content", [b"", b"{", b"null", b"[]"])
def test_mutation_success_requires_valid_json(monkeypatch, content):
    response = Mock(status_code=201, content=content)
    monkeypatch.setattr(
        rest.WRITE_SESSION,
        "request",
        Mock(return_value=response),
    )

    with pytest.raises(rest.KalshiResponseError) as caught:
        rest.request("POST", "https://example.test/orders", body={})

    assert caught.value.outcome_unknown is True
    assert caught.value.response is response
    assert "did not contain a JSON object" in str(caught.value)


def test_request_raises_structured_api_error(monkeypatch):
    monkeypatch.setattr(
        rest.WRITE_SESSION,
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
    assert caught.value.outcome_unknown is False
    assert caught.value.code == "invalid_request"
    assert caught.value.details == {"field": "price"}
    assert caught.value.payload["error"]["message"] == "Bad request"


@pytest.mark.parametrize(
    ("method", "status", "outcome_unknown"),
    [
        ("GET", 500, False),
        ("POST", 500, True),
        ("DELETE", 408, True),
        ("POST", 429, False),
    ],
)
def test_api_errors_mark_only_ambiguous_mutations(
    monkeypatch,
    method,
    status,
    outcome_unknown,
):
    response_value = response(
        status,
        {"error": {"message": "request failed"}},
    )
    request = Mock(return_value=response_value)
    monkeypatch.setattr(rest.SESSION, "request", request)
    monkeypatch.setattr(rest.WRITE_SESSION, "request", request)

    with pytest.raises(rest.KalshiAPIError) as caught:
        rest.request(method, "https://example.test/resource")

    assert caught.value.outcome_unknown is outcome_unknown


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


def test_mutations_use_a_separate_session(monkeypatch):
    read_request = Mock(return_value=response(200, {}))
    write_request = Mock(return_value=response(201, {}))
    monkeypatch.setattr(rest.SESSION, "request", read_request)
    monkeypatch.setattr(rest.WRITE_SESSION, "request", write_request)

    rest.request("GET", "https://example.test/markets")
    rest.request("POST", "https://example.test/orders", body={})

    assert read_request.call_count == 1
    assert write_request.call_count == 1


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
    monkeypatch.setattr(rest.WRITE_SESSION, "request", request)

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


@pytest.mark.parametrize("caller", [rest.get, rest.post, rest.put, rest.delete])
def test_timeout_is_applied_and_not_sent_as_a_query_parameter(monkeypatch, caller):
    request = Mock(return_value=response(200, {}))
    monkeypatch.setattr(rest.SESSION, "request", request)
    monkeypatch.setattr(rest.WRITE_SESSION, "request", request)

    caller("https://example.test/orders", timeout=1.5)

    assert request.call_args.kwargs["timeout"] == 1.5
    assert request.call_args.kwargs["params"] is None
