import pandas as pd
import pytest

from kalshi.utils import calculate_volume_stats, calculate_vwap


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
