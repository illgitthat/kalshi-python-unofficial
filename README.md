# kalshi-python-unofficial

A small, dictionary-based Python client for Kalshi REST and WebSocket APIs.
It follows Kalshi OpenAPI 3.30.0 and the AsyncAPI specification dated
September 9, 2026.

## Install

```bash
python -m pip install kalshi-python-unofficial
```

Python 3.10 or newer is required. Demo is the default environment.

```python
import kalshi

kalshi.constants.use_prod()
kalshi.auth.set_key("API_KEY_ID", "path/to/private-key.pem")
```

Demo and production credentials are not interchangeable.

## Discover markets and events

```python
from kalshi.rest import market

live_markets = market.GetLiveMarkets(limit=100)
upcoming_events = market.GetUpcomingEvents(with_milestones=True)
```

Event status is derived from its child markets. Use `GetLiveMarkets()` or
`GetUpcomingMarkets()` when exact market status matters. Paginated responses
include the next Kalshi cursor.

## Trade with V2 orders

V2 orders use fixed-point strings. `bid` buys YES and `ask` sells YES.

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
```

The client never retries failed requests. A caller must reconcile an
uncertain write by `client_order_id` before it sends another order.
HTTP failures raise `kalshi.rest.KalshiAPIError` with the API status and
structured fields plus the raw payload. Transport failures raise
`KalshiTransportError`; its `outcome_unknown` flag is true for mutations that
may have reached Kalshi.

Always provide a unique `client_order_id`. Validate prices against the
market's `price_ranges`, and inspect every result in a batch response.

## Subaccounts and milestones

```python
from kalshi.rest import milestone, portfolio

balances = portfolio.GetSubaccountBalances()
milestones = milestone.GetMilestones(limit=100)
live_data = milestone.GetLiveData(milestones["milestones"][0]["id"])
```

Subaccounts require a supported Direct account and API tier.

## WebSocket

```python
import asyncio
import kalshi


class Feed(kalshi.websocket.Client):
    async def on_open(self):
        await self.subscribe(
            ["orderbook_delta"],
            ["KXEXAMPLE-26-T1"],
            use_yes_price=True,
        )

    async def on_message(self, message):
        print(message)


kalshi.constants.use_prod()
asyncio.run(Feed().run_forever())
```

`run_forever()` reconnects and calls `on_open()` after each connection, so
the same subscription code restores the feed. On an orderbook sequence gap,
the default handler drops deltas until a new snapshot arrives. Other sequence
gaps close the socket so `run_forever()` can reconnect.

## Compatibility

This release replaces legacy order writes with `/portfolio/events/orders`.
Old `action`, `type`, `yes_price`, and `no_price` arguments are not accepted.
`GetExchangeAnnouncements()` is retained only to report that Kalshi removed
the endpoint from the current specification.

The recommended `external-api` hosts are used by default. The older hosts
remain available through `use_legacy_demo()` and `use_legacy_prod()`.

## References

- [OpenAPI](https://docs.kalshi.com/openapi.yaml)
- [AsyncAPI](https://docs.kalshi.com/asyncapi.yaml)
- [API changelog](https://docs.kalshi.com/changelog)
- [API environments](https://docs.kalshi.com/getting_started/api_environments)
- [Fixed-point migration](https://docs.kalshi.com/getting_started/fixed_point_migration)
