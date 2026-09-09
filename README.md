# kalshi-python-unofficial

A lightweight, dictionary-based Python wrapper for Kalshi's REST and
WebSocket APIs.

This release follows Kalshi OpenAPI 3.30.0 and the current AsyncAPI
specification as of September 9, 2026. It uses fixed-point string order
fields, V2 event-order endpoints, exchange routing, subaccounts, milestones,
and the recommended `external-api` hosts.

## Install

```bash
python -m pip install kalshi-python-unofficial
```

Python 3.10 or newer is required.

## Migration from 0.1

Order writes now use Kalshi's V2 event-order endpoints. `CreateOrder`,
`AmendOrder`, `DecreaseOrder`, `CancelOrder`, and batch methods therefore use
fixed-point `count` and `price` strings, book-side `bid` or `ask`, and explicit
exchange-routing fields. Legacy `action`, `type`, `yes_price`, and `no_price`
arguments are not accepted.

`GetPositions` no longer sends the removed `settlement_status` filter.
`GetExchangeAnnouncements` raises `NotImplementedError` because the endpoint
is absent from the current OpenAPI specification.

## Environment and credentials

The demo environment is selected by default. Demo and production credentials
are separate.

```python
import kalshi

kalshi.constants.use_prod()
kalshi.auth.set_key("API_KEY_ID", "path/to/private-key.pem")
```

Compatibility hosts remain available through
`kalshi.constants.use_legacy_demo()` and `use_legacy_prod()`.

## Market and event discovery

```python
from kalshi.rest import market

live_events = market.GetLiveEvents(with_milestones=True)
upcoming_events = market.GetUpcomingEvents()
live_markets = market.GetLiveMarkets(limit=1000)
upcoming_markets = market.GetUpcomingMarkets(limit=1000)
```

Event status is derived from child markets. When exact market state matters,
inspect and filter nested `event.markets`, or use the market methods directly.
List methods return Kalshi's cursor unchanged for caller-controlled pagination.

## Milestones and live data

```python
from kalshi.rest import milestone

response = milestone.GetMilestones(
    limit=100,
    minimum_start_date="2026-09-09T00:00:00Z",
)
details = milestone.GetMilestone(response["milestones"][0]["id"])
live_data = milestone.GetLiveData(details["milestone"]["id"])
```

## V2 orders

V2 prices and quantities are fixed-point strings. `side` is the book side:
`bid` corresponds to YES and `ask` corresponds to NO.

```python
from kalshi.rest import portfolio

order = portfolio.CreateOrder(
    ticker="KXEXAMPLE-26-T1",
    side="bid",
    count="10.00",
    price="0.5600",
    time_in_force="good_till_canceled",
    self_trade_prevention_type="taker_at_cross",
    client_order_id="example-order-1",
    subaccount=1,
    exchange_index=-1,
)

portfolio.CancelOrder(
    order["order"]["order_id"],
    market_ticker="KXEXAMPLE-26-T1",
    subaccount=1,
    exchange_index=-1,
)
```

Write requests are not retried automatically. This avoids duplicate orders
after ambiguous network failures. Reconcile by `client_order_id` before a
caller retries.

## Subaccounts

```python
import uuid

from kalshi.rest import portfolio

subaccount = portfolio.CreateSubaccount(exchange_index=0)
portfolio.TransferBetweenSubaccounts(
    client_transfer_id=str(uuid.uuid4()),
    from_subaccount=0,
    to_subaccount=subaccount["subaccount_number"],
    amount_cents=10_000,
    exchange_index=0,
)
balances = portfolio.GetSubaccountBalances()
```

Subaccounts require a Direct account and the required API tier.

## WebSocket

```python
import asyncio

import kalshi


class MarketFeed(kalshi.websocket.Client):
    async def on_open(self):
        await self.subscribe(
            ["orderbook_delta", "market_lifecycle_v2"],
            ["KXEXAMPLE-26-T1"],
            use_yes_price=True,
        )

    async def on_message(self, message):
        print(message)

    async def on_sequence_gap(self, message, expected_sequence):
        print("sequence gap", expected_sequence, message)


kalshi.constants.use_prod()
client = MarketFeed()
asyncio.run(client.run_forever())
```

`use_yes_price=True` makes both orderbook sides use the YES-leg price scale.
The client also supports unsubscribe, subscription updates, sequence-gap
callbacks, and reconnect/resubscribe through `run_forever()`.

## Transport behavior

All HTTP `2xx` responses are accepted, including empty `204` responses.
Failures raise `kalshi.rest.rest.KalshiAPIError` with `status_code`, `code`,
`message`, and `details`. Safe GET requests retry `429`, `502`, `503`, and
`504` responses with exponential backoff. Configure transport defaults with:

```python
from kalshi.rest.rest import configure

configure(timeout=5.0, read_retries=2, backoff_factor=0.25)
```

## Primary API references

- [Kalshi OpenAPI specification](https://docs.kalshi.com/openapi.yaml)
- [Kalshi AsyncAPI specification](https://docs.kalshi.com/asyncapi.yaml)
- [API environments](https://docs.kalshi.com/getting_started/api_environments)
- [Fixed-point migration](https://docs.kalshi.com/getting_started/fixed_point_migration)
