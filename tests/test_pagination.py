import pytest

from fastkalshi.rest.market import Market
from fastkalshi.rest.milestone import Milestone
from fastkalshi.rest.pagination import KalshiPaginationError, paginate
from fastkalshi.rest.portfolio import Portfolio
from fastkalshi.rest.structured_target import StructuredTarget


def test_paginate_preserves_filters_and_stops_on_empty_cursor():
    calls = []

    def fetch_page(cursor=None, status=None):
        calls.append((cursor, status))
        if cursor is None:
            return {"markets": [{"ticker": "A"}], "cursor": "next"}
        return {"markets": [{"ticker": "B"}], "cursor": ""}

    assert list(paginate(fetch_page, "markets", status="open")) == [
        {"ticker": "A"},
        {"ticker": "B"},
    ]
    assert calls == [(None, "open"), ("next", "open")]


def test_paginate_enforces_page_limit_and_detects_cursor_cycles():
    calls = 0

    def fetch_page(cursor=None):
        nonlocal calls
        calls += 1
        return {"items": [{"page": calls}], "cursor": "same"}

    assert list(paginate(fetch_page, "items", max_pages=1)) == [{"page": 1}]

    with pytest.raises(KalshiPaginationError, match="repeated cursor"):
        list(paginate(fetch_page, "items"))


def test_paginate_rejects_invalid_page_limit_eagerly():
    with pytest.raises(ValueError, match="max_pages must be at least 1"):
        paginate(lambda cursor=None: {"items": []}, "items", max_pages=0)


@pytest.mark.parametrize(
    ("owner", "iterator_name", "fetch_name", "item_key"),
    [
        (Market(), "IterMarkets", "GetMarkets", "markets"),
        (Market(), "IterEvents", "GetEvents", "events"),
        (Milestone(), "IterMilestones", "GetMilestones", "milestones"),
        (
            StructuredTarget(),
            "IterStructuredTargets",
            "GetStructuredTargets",
            "structured_targets",
        ),
        (Portfolio(), "IterOrders", "GetOrders", "orders"),
        (Portfolio(), "IterFills", "GetFills", "fills"),
        (
            Portfolio(),
            "IterSubaccountTransfers",
            "GetSubaccountTransfers",
            "transfers",
        ),
        (
            Portfolio(),
            "IterIntraExchangeInstanceTransfers",
            "GetIntraExchangeInstanceTransfers",
            "transfers",
        ),
    ],
)
def test_endpoint_iterators_use_bounded_pagination(
    monkeypatch,
    owner,
    iterator_name,
    fetch_name,
    item_key,
):
    fetch = lambda cursor=None, **params: {
        item_key: [{"cursor": cursor, **params}],
        "cursor": "next",
    }
    monkeypatch.setattr(owner, fetch_name, fetch)

    assert list(getattr(owner, iterator_name)(max_pages=1, limit=25)) == [
        {"cursor": None, "limit": 25}
    ]
