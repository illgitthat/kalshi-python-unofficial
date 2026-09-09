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


def test_amend_order_splits_subaccount_query_and_exchange_body(recorded_request):
    Portfolio().AmendOrder(
        "order-1",
        ticker="KXTEST",
        side="bid",
        price="0.5000",
        count="2.00",
        subaccount=3,
        exchange_index=1,
    )

    call = recorded_request.call_args
    assert call.kwargs["params"] == {"subaccount": 3}
    assert call.kwargs["json"] == {
        "ticker": "KXTEST",
        "side": "bid",
        "price": "0.5000",
        "count": "2.00",
        "exchange_index": 1,
    }


def test_decrease_order_splits_subaccount_query_and_routing_body(recorded_request):
    Portfolio().DecreaseOrder(
        "order-1",
        reduce_by="1.00",
        subaccount=3,
        exchange_index=1,
        market_ticker="KXTEST",
    )

    call = recorded_request.call_args
    assert call.kwargs["params"] == {"subaccount": 3}
    assert call.kwargs["json"] == {
        "reduce_by": "1.00",
        "exchange_index": 1,
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


def test_positions_send_current_filters(recorded_request):
    Portfolio().GetPositions(
        ticker="KXTEST",
        event_ticker="KXEVENT",
    )

    assert recorded_request.call_args.kwargs["params"] == {
        "limit": 100,
        "ticker": "KXTEST",
        "event_ticker": "KXEVENT",
    }


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


def test_milestones_supply_required_default_limit(recorded_request):
    Milestone().GetMilestones()

    assert recorded_request.call_args.kwargs["params"] == {"limit": 100}


def test_event_live_data_uses_event_endpoint(recorded_request):
    Market().GetEventLiveData("KXEVENT", range="game")

    call = recorded_request.call_args
    assert call.args[:2] == (
        "GET",
        "https://external-api.demo.kalshi.co/trade-api/v2/live_data/events/KXEVENT",
    )
    assert call.kwargs["params"] == {"range": "game"}


def test_event_metadata_uses_native_endpoint(recorded_request):
    Market().GetEventMetadata("KXEVENT")

    assert recorded_request.call_args.args[:2] == (
        "GET",
        "https://external-api.demo.kalshi.co/trade-api/v2/events/KXEVENT/metadata",
    )


def test_user_data_timestamp_uses_exchange_endpoint(recorded_request):
    Exchange().GetUserDataTimestamp()

    assert recorded_request.call_args.args[:2] == (
        "GET",
        "https://external-api.demo.kalshi.co/trade-api/v2/exchange/user_data_timestamp",
    )


def test_queue_positions_preserve_filters(recorded_request):
    Portfolio().GetOrderQueuePositions(
        market_tickers=["KXONE", "KXTWO"],
        event_ticker="KXEVENT",
        subaccount=2,
    )

    assert recorded_request.call_args.kwargs["params"] == {
        "market_tickers": "KXONE,KXTWO",
        "event_ticker": "KXEVENT",
        "subaccount": 2,
    }


def test_queue_positions_require_a_market_or_event():
    with pytest.raises(
        ValueError,
        match="market_tickers or event_ticker is required",
    ):
        Portfolio().GetOrderQueuePositions()


def test_order_group_create_and_limit_update_use_current_fields(recorded_request):
    portfolio = Portfolio()
    portfolio.CreateOrderGroup(
        contracts_limit_fp="10.00",
        subaccount=2,
        exchange_index=1,
    )
    create_call = recorded_request.call_args

    portfolio.UpdateOrderGroupLimit(
        "group-1",
        contracts_limit_fp="20.00",
        subaccount=2,
        exchange_index=1,
    )
    update_call = recorded_request.call_args

    assert create_call.args[0] == "POST"
    assert create_call.kwargs["json"] == {
        "contracts_limit_fp": "10.00",
        "subaccount": 2,
        "exchange_index": 1,
    }
    assert update_call.args[0] == "PUT"
    assert update_call.kwargs["json"] == {"contracts_limit_fp": "20.00"}
    assert update_call.kwargs["params"] == {
        "subaccount": 2,
        "exchange_index": 1,
    }


def test_order_group_control_request_shapes(recorded_request):
    portfolio = Portfolio()

    portfolio.GetOrderGroups(subaccount=2)
    list_call = recorded_request.call_args
    portfolio.GetOrderGroup("group-1", subaccount=2)
    get_call = recorded_request.call_args
    portfolio.DeleteOrderGroup("group-1", subaccount=2, exchange_index=1)
    delete_call = recorded_request.call_args
    portfolio.ResetOrderGroup("group-1", subaccount=2, exchange_index=1)
    reset_call = recorded_request.call_args
    portfolio.TriggerOrderGroup("group-1", subaccount=2, exchange_index=1)
    trigger_call = recorded_request.call_args

    assert list_call.args[0] == "GET"
    assert list_call.kwargs["params"] == {"subaccount": 2}
    assert get_call.args[0] == "GET"
    assert get_call.kwargs["params"] == {"subaccount": 2}
    assert delete_call.args[0] == "DELETE"
    assert delete_call.kwargs["params"] == {
        "subaccount": 2,
        "exchange_index": 1,
    }
    for call in (reset_call, trigger_call):
        assert call.args[0] == "PUT"
        assert call.kwargs["json"] == {}
        assert call.kwargs["params"] == {
            "subaccount": 2,
            "exchange_index": 1,
        }


def test_cancel_all_orders_uses_subaccount_scope(recorded_request):
    Portfolio().CancelAllOrders(subaccount=4)

    call = recorded_request.call_args
    assert call.args[:2] == (
        "DELETE",
        "https://external-api.demo.kalshi.co/trade-api/v2/portfolio/events/orders",
    )
    assert call.kwargs["params"] == {"subaccount": 4}


def test_cancel_all_orders_accepts_empty_204_response(monkeypatch):
    response = Mock(status_code=204, content=b"")
    monkeypatch.setattr(rest.WRITE_SESSION, "request", Mock(return_value=response))
    module = importlib.import_module("kalshi.rest.portfolio")
    monkeypatch.setattr(module, "request_headers", lambda method, url: {})

    assert Portfolio().CancelAllOrders(subaccount=4) is None


def test_batch_order_item_errors_remain_visible(recorded_request):
    response = recorded_request.return_value
    response.content = (
        b'{"orders":[{"client_order_id":"one","order_id":null,'
        b'"error":{"code":"rejected","message":"rejected"}}]}'
    )

    result = Portfolio().BatchCreateOrders([{"client_order_id": "one"}])

    assert result["orders"][0]["error"]["code"] == "rejected"
