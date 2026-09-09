import importlib
from unittest.mock import Mock

import pytest

from kalshi import constants
from kalshi.rest import rest
from kalshi.rest.exchange import Exchange
from kalshi.rest.market import Market
from kalshi.rest.milestone import Milestone
from kalshi.rest.portfolio import Portfolio


@pytest.fixture
def recorded_request(monkeypatch):
    constants.use_demo()
    response = Mock(status_code=200, content=b'{"ok":true}')
    request = Mock(return_value=response)
    monkeypatch.setattr(rest.SESSION, "request", request)
    monkeypatch.setattr(rest.WRITE_SESSION, "request", request)

    portfolio_module = importlib.import_module("kalshi.rest.portfolio")
    market_module = importlib.import_module("kalshi.rest.market")
    for module in (portfolio_module, market_module):
        monkeypatch.setattr(
            module,
            "request_headers",
            lambda method, url: {"X-Test-Auth": f"{method} {url}"},
        )
    return request


def test_live_event_discovery_uses_current_filters(recorded_request):
    assert Market().GetLiveEvents(
        with_nested_markets=True,
        with_milestones=True,
    ) == {"ok": True}

    call = recorded_request.call_args
    assert call.args[:2] == (
        "GET",
        "https://external-api.demo.kalshi.co/trade-api/v2/events",
    )
    assert call.kwargs["params"] == {
        "limit": 200,
        "status": "open",
        "with_nested_markets": "true",
        "with_milestones": "true",
    }


def test_get_markets_preserves_legacy_positional_filters(recorded_request):
    Market().GetMarkets(
        100,
        None,
        None,
        None,
        2_000_000_000,
        1_000_000_000,
        "open",
        ["KXTEST"],
    )

    assert recorded_request.call_args.kwargs["params"] == {
        "limit": 100,
        "max_close_ts": 2_000_000_000,
        "min_close_ts": 1_000_000_000,
        "status": "open",
        "tickers": "KXTEST",
    }


def test_create_order_uses_v2_fixed_point_payload(recorded_request):
    assert Portfolio().CreateOrder(
        ticker="KXTEST",
        side="bid",
        count="10.00",
        price="0.5600",
        time_in_force="good_till_canceled",
        self_trade_prevention_type="taker_at_cross",
        subaccount=2,
        exchange_index=-1,
    ) == {"ok": True}

    call = recorded_request.call_args
    assert call.args[:2] == (
        "POST",
        "https://external-api.demo.kalshi.co/trade-api/v2/portfolio/events/orders",
    )
    assert call.kwargs["params"] is None
    assert call.kwargs["json"] == {
        "ticker": "KXTEST",
        "side": "bid",
        "count": "10.00",
        "price": "0.5600",
        "time_in_force": "good_till_canceled",
        "self_trade_prevention_type": "taker_at_cross",
        "subaccount": 2,
        "exchange_index": -1,
    }


def test_portfolio_warmup_uses_mutation_session(monkeypatch):
    constants.use_demo()
    response = Mock(status_code=200, content=b'{"balance":"0.0000"}')
    read_request = Mock(return_value=response)
    write_request = Mock(return_value=response)
    monkeypatch.setattr(rest.SESSION, "request", read_request)
    monkeypatch.setattr(rest.WRITE_SESSION, "request", write_request)
    portfolio_module = importlib.import_module("kalshi.rest.portfolio")
    monkeypatch.setattr(
        portfolio_module,
        "request_headers",
        lambda method, url: {},
    )

    Portfolio().Warmup()

    assert read_request.call_count == 0
    assert write_request.call_count == 1


def test_orderbook_request_is_authenticated(recorded_request):
    Market().GetMarketOrderbook("KXTEST", depth=1)

    call = recorded_request.call_args
    assert call.args[:2] == (
        "GET",
        "https://external-api.demo.kalshi.co/trade-api/v2/markets/KXTEST/orderbook",
    )
    assert call.kwargs["headers"]["X-Test-Auth"].startswith("GET ")
    assert call.kwargs["params"] == {"depth": 1}


def test_removed_exchange_announcements_endpoint_fails_explicitly():
    with pytest.raises(
        NotImplementedError,
        match="does not expose /exchange/announcements",
    ):
        Exchange().GetExchangeAnnouncements()


def test_cancel_order_preserves_routing_context(recorded_request):
    Portfolio().CancelOrder(
        "1",
        subaccount=2,
        exchange_index=-1,
        market_ticker="KXTEST",
    )

    call = recorded_request.call_args
    assert call.args[:2] == (
        "DELETE",
        "https://external-api.demo.kalshi.co/trade-api/v2/portfolio/events/orders/1",
    )
    assert call.kwargs["params"] == {
        "subaccount": 2,
        "exchange_index": -1,
        "market_ticker": "KXTEST",
    }


@pytest.mark.parametrize(
    "quantities",
    [{}, {"reduce_by": "1.00", "reduce_to": "1.00"}],
)
def test_decrease_order_requires_one_quantity(quantities):
    with pytest.raises(
        ValueError,
        match="provide exactly one of reduce_by or reduce_to",
    ):
        Portfolio().DecreaseOrder("1", **quantities)


def test_positions_preserve_legacy_positional_filters(recorded_request):
    Portfolio().GetPositions(
        None,
        100,
        None,
        None,
        "KXTEST",
        "KXEVENT",
    )

    assert recorded_request.call_args.kwargs["params"] == {
        "limit": 100,
        "ticker": "KXTEST",
        "event_ticker": "KXEVENT",
    }


def test_removed_position_settlement_filter_fails_explicitly():
    with pytest.raises(
        ValueError,
        match="settlement_status is no longer supported",
    ):
        Portfolio().GetPositions(settlement_status="settled")


def test_subaccount_transfer_preserves_id_and_units(recorded_request):
    Portfolio().TransferBetweenSubaccounts(
        client_transfer_id="14f82aa8-bd56-4f98-a5b5-8d7708e9663f",
        from_subaccount=0,
        to_subaccount=4,
        amount_cents=2500,
        exchange_index=1,
    )

    assert recorded_request.call_args.kwargs["json"] == {
        "client_transfer_id": "14f82aa8-bd56-4f98-a5b5-8d7708e9663f",
        "from_subaccount": 0,
        "to_subaccount": 4,
        "amount_cents": 2500,
        "exchange_index": 1,
    }


def test_milestone_live_data_uses_preferred_endpoint(recorded_request):
    Milestone().GetLiveData("milestone-1", include_player_stats=True)

    call = recorded_request.call_args
    assert call.args[:2] == (
        "GET",
        "https://external-api.demo.kalshi.co/trade-api/v2/live_data/milestone/milestone-1",
    )
    assert call.kwargs["params"] == {"include_player_stats": "true"}
