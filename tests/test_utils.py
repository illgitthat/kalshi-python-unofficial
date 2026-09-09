from unittest.mock import Mock

import pandas as pd
import pytest

from kalshi import utils
from kalshi.rest import portfolio
from kalshi.utils import (
    calculate_volume_stats,
    calculate_vwap,
    cancel_all_resting_orders,
)


def test_analytics_accept_current_fixed_point_trade_fields():
    trades = pd.DataFrame(
        {
            "count_fp": ["2.50", "1.50"],
            "yes_price_dollars": ["0.2500", "0.6000"],
            "taker_outcome_side": ["yes", "no"],
            "count": [99, 99],
            "yes_price": [99, 99],
            "taker_side": ["no", "yes"],
        }
    )

    assert calculate_vwap(trades) == pytest.approx(38.125)
    stats = calculate_volume_stats(trades)
    assert stats["yes_taker_volume"] == pytest.approx(2.5)
    assert stats["no_taker_volume"] == pytest.approx(1.5)
    assert stats["yes_taker_dollar_volume"] == pytest.approx(0.625)
    assert stats["no_taker_dollar_volume"] == pytest.approx(0.6)


def test_analytics_preserve_legacy_trade_columns():
    trades = pd.DataFrame(
        {
            "count": [2, 1],
            "yes_price": [25, 60],
            "taker_side": ["yes", "no"],
        }
    )

    assert calculate_vwap(trades) == pytest.approx(110 / 3)


def test_cancel_orders_preserves_explicit_scope_for_nullable_metadata(monkeypatch):
    monkeypatch.setattr(
        utils,
        "get_all_orders",
        lambda **kwargs: [
            {
                "order_id": "order-1",
                "ticker": "KXTEST",
                "subaccount_number": None,
                "exchange_index": None,
            }
        ],
    )
    cancel = Mock(return_value={})
    monkeypatch.setattr(portfolio, "CancelOrder", cancel)

    cancel_all_resting_orders(subaccount=2, exchange_index=0)

    cancel.assert_called_once_with(
        order_id="order-1",
        market_ticker="KXTEST",
        subaccount=2,
        exchange_index=0,
    )
