import importlib
from unittest.mock import Mock

from kalshi.rest.market import Market
from kalshi.rest.milestone import Milestone
from kalshi.rest.portfolio import Portfolio


def test_live_event_discovery_uses_current_filters(monkeypatch):
    request = Mock(return_value={"events": []})
    module = importlib.import_module("kalshi.rest.market")
    monkeypatch.setattr(module, "get", request)

    result = Market().GetLiveEvents(with_milestones=True)

    assert result == {"events": []}
    assert request.call_args.args[0].endswith("/trade-api/v2/events")
    assert request.call_args.kwargs["status"] == "open"
    assert request.call_args.kwargs["with_nested_markets"] is True
    assert request.call_args.kwargs["with_milestones"] is True


def test_create_order_uses_v2_fixed_point_payload(monkeypatch):
    portfolio = Portfolio()
    request = Mock(return_value={"order": {"order_id": "1"}})
    monkeypatch.setattr(portfolio, "_authenticated_post_request", request)

    result = portfolio.CreateOrder(
        ticker="KXTEST",
        side="bid",
        count="10.00",
        price="0.5600",
        time_in_force="good_till_canceled",
        self_trade_prevention_type="taker_at_cross",
        subaccount=2,
        exchange_index=-1,
    )

    assert result["order"]["order_id"] == "1"
    url, payload = request.call_args.args
    assert url.endswith("/portfolio/events/orders")
    assert payload == {
        "ticker": "KXTEST",
        "side": "bid",
        "count": "10.00",
        "price": "0.5600",
        "time_in_force": "good_till_canceled",
        "self_trade_prevention_type": "taker_at_cross",
        "subaccount": 2,
        "exchange_index": -1,
    }


def test_cancel_order_preserves_routing_context(monkeypatch):
    portfolio = Portfolio()
    request = Mock(return_value={"order": {"order_id": "1"}})
    monkeypatch.setattr(portfolio, "_authenticated_del_request", request)

    portfolio.CancelOrder(
        "1",
        subaccount=2,
        exchange_index=-1,
        market_ticker="KXTEST",
    )

    assert request.call_args.args[0].endswith("/portfolio/events/orders/1")
    assert request.call_args.kwargs == {
        "subaccount": 2,
        "exchange_index": -1,
        "market_ticker": "KXTEST",
    }


def test_subaccount_transfer_preserves_id_and_units(monkeypatch):
    portfolio = Portfolio()
    request = Mock(return_value={"transfer": {"status": "completed"}})
    monkeypatch.setattr(portfolio, "_authenticated_post_request", request)

    portfolio.TransferBetweenSubaccounts(
        client_transfer_id="14f82aa8-bd56-4f98-a5b5-8d7708e9663f",
        from_subaccount=0,
        to_subaccount=4,
        amount_cents=2500,
        exchange_index=1,
    )

    assert request.call_args.args[1] == {
        "client_transfer_id": "14f82aa8-bd56-4f98-a5b5-8d7708e9663f",
        "from_subaccount": 0,
        "to_subaccount": 4,
        "amount_cents": 2500,
        "exchange_index": 1,
    }


def test_milestone_live_data_uses_preferred_endpoint(monkeypatch):
    request = Mock(return_value={"live_data": {}})
    module = importlib.import_module("kalshi.rest.milestone")
    monkeypatch.setattr(module, "get", request)

    Milestone().GetLiveData("milestone-1", include_player_stats=True)

    assert request.call_args.args[0].endswith("/live_data/milestone/milestone-1")
    assert request.call_args.kwargs == {"include_player_stats": True}
