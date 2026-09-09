from kalshi.auth import request_headers
from kalshi.constants import api_url

from .rest import WRITE_SESSION, delete, drop_none, get, post


class Portfolio:
    def _authenticated_get_request(self, url: str, **kwargs):
        return get(url, headers=request_headers("GET", url), **kwargs)

    def _authenticated_post_request(self, url: str, data: dict, **kwargs):
        return post(
            url,
            headers=request_headers("POST", url),
            body=data,
            **kwargs,
        )

    def _authenticated_del_request(
        self,
        url: str,
        data: dict | None = None,
        **kwargs,
    ):
        return delete(
            url,
            headers=request_headers("DELETE", url),
            body=data,
            **kwargs,
        )

    def GetBalance(
        self,
        subaccount: int | None = None,
        exchange_index: int | None = None,
    ):
        url = api_url("portfolio/balance")
        return self._authenticated_get_request(
            url,
            **drop_none(
                {
                    "subaccount": subaccount,
                    "exchange_index": exchange_index,
                }
            ),
        )

    def Warmup(self):
        url = api_url("portfolio/balance")
        return get(
            url,
            headers=request_headers("GET", url),
            session=WRITE_SESSION,
        )

    def GetFills(
        self,
        ticker: str | None = None,
        order_id: str | None = None,
        min_ts: int | None = None,
        max_ts: int | None = None,
        limit: int = 100,
        cursor: str | None = None,
        subaccount: int | None = None,
        exchange_index: int | None = None,
    ):
        url = api_url("portfolio/fills")
        return self._authenticated_get_request(
            url,
            **drop_none(
                {
                    "ticker": ticker,
                    "order_id": order_id,
                    "min_ts": min_ts,
                    "max_ts": max_ts,
                    "limit": limit,
                    "cursor": cursor,
                    "subaccount": subaccount,
                    "exchange_index": exchange_index,
                }
            ),
        )

    def GetOrders(
        self,
        ticker: str | None = None,
        event_ticker: str | None = None,
        min_ts: int | None = None,
        max_ts: int | None = None,
        status: str | None = None,
        cursor: str | None = None,
        limit: int = 100,
        subaccount: int | None = None,
        exchange_index: int | None = None,
    ):
        url = api_url("portfolio/orders")
        return self._authenticated_get_request(
            url,
            **drop_none(
                {
                    "ticker": ticker,
                    "event_ticker": event_ticker,
                    "min_ts": min_ts,
                    "max_ts": max_ts,
                    "status": status,
                    "cursor": cursor,
                    "limit": limit,
                    "subaccount": subaccount,
                    "exchange_index": exchange_index,
                }
            ),
        )

    def GetOrder(self, order_id: str):
        url = api_url(f"portfolio/orders/{order_id}")
        return self._authenticated_get_request(url)

    def GetPositions(
        self,
        cursor: str | None = None,
        limit: int = 100,
        count_filter: str | None = None,
        ticker: str | None = None,
        event_ticker: str | None = None,
        subaccount: int | None = None,
        exchange_index: int | None = None,
    ):
        url = api_url("portfolio/positions")
        return self._authenticated_get_request(
            url,
            **drop_none(
                {
                    "cursor": cursor,
                    "limit": limit,
                    "count_filter": count_filter,
                    "ticker": ticker,
                    "event_ticker": event_ticker,
                    "subaccount": subaccount,
                    "exchange_index": exchange_index,
                }
            ),
        )

    def GetPortfolioSettlements(
        self,
        limit: int = 100,
        min_ts: int | None = None,
        max_ts: int | None = None,
        cursor: str | None = None,
        ticker: str | None = None,
        event_ticker: str | None = None,
        subaccount: int | None = None,
    ):
        url = api_url("portfolio/settlements")
        return self._authenticated_get_request(
            url,
            **drop_none(
                {
                    "limit": limit,
                    "min_ts": min_ts,
                    "max_ts": max_ts,
                    "cursor": cursor,
                    "ticker": ticker,
                    "event_ticker": event_ticker,
                    "subaccount": subaccount,
                }
            ),
        )

    GetSettlements = GetPortfolioSettlements

    def GetPortfolioRestingOrderTotalValue(self):
        url = api_url("portfolio/summary/total_resting_order_value")
        return self._authenticated_get_request(url)

    def CreateOrder(
        self,
        ticker: str,
        side: str,
        count: str,
        price: str,
        time_in_force: str,
        self_trade_prevention_type: str,
        client_order_id: str | None = None,
        expiration_time: int | None = None,
        post_only: bool | None = None,
        cancel_order_on_pause: bool | None = None,
        reduce_only: bool | None = None,
        subaccount: int | None = None,
        order_group_id: str | None = None,
        exchange_index: int | None = None,
    ):
        url = api_url("portfolio/events/orders")
        return self._authenticated_post_request(
            url,
            drop_none(
                {
                    "ticker": ticker,
                    "client_order_id": client_order_id,
                    "side": side,
                    "count": count,
                    "price": price,
                    "expiration_time": expiration_time,
                    "time_in_force": time_in_force,
                    "post_only": post_only,
                    "self_trade_prevention_type": self_trade_prevention_type,
                    "cancel_order_on_pause": cancel_order_on_pause,
                    "reduce_only": reduce_only,
                    "subaccount": subaccount,
                    "order_group_id": order_group_id,
                    "exchange_index": exchange_index,
                }
            ),
        )

    CreateOrderV2 = CreateOrder

    def BatchCreateOrders(self, orders: list[dict]):
        url = api_url("portfolio/events/orders/batched")
        return self._authenticated_post_request(url, {"orders": orders})

    BatchCreateOrdersV2 = BatchCreateOrders

    def AmendOrder(
        self,
        order_id: str,
        ticker: str,
        side: str,
        price: str,
        count: str,
        client_order_id: str | None = None,
        updated_client_order_id: str | None = None,
        subaccount: int | None = None,
        exchange_index: int | None = None,
    ):
        url = api_url(f"portfolio/events/orders/{order_id}/amend")
        return self._authenticated_post_request(
            url,
            drop_none(
                {
                    "ticker": ticker,
                    "side": side,
                    "price": price,
                    "count": count,
                    "client_order_id": client_order_id,
                    "updated_client_order_id": updated_client_order_id,
                    "exchange_index": exchange_index,
                }
            ),
            **drop_none({"subaccount": subaccount}),
        )

    AmendOrderV2 = AmendOrder

    def DecreaseOrder(
        self,
        order_id: str,
        reduce_by: str | None = None,
        reduce_to: str | None = None,
        subaccount: int | None = None,
        exchange_index: int | None = None,
        market_ticker: str | None = None,
    ):
        if (reduce_by is None) == (reduce_to is None):
            raise ValueError("provide exactly one of reduce_by or reduce_to")
        url = api_url(f"portfolio/events/orders/{order_id}/decrease")
        return self._authenticated_post_request(
            url,
            drop_none(
                {
                    "reduce_by": reduce_by,
                    "reduce_to": reduce_to,
                    "exchange_index": exchange_index,
                    "market_ticker": market_ticker,
                }
            ),
            **drop_none({"subaccount": subaccount}),
        )

    DecreaseOrderV2 = DecreaseOrder

    def CancelOrder(
        self,
        order_id: str,
        subaccount: int | None = None,
        exchange_index: int | None = None,
        market_ticker: str | None = None,
    ):
        url = api_url(f"portfolio/events/orders/{order_id}")
        return self._authenticated_del_request(
            url,
            **drop_none(
                {
                    "subaccount": subaccount,
                    "exchange_index": exchange_index,
                    "market_ticker": market_ticker,
                }
            ),
        )

    CancelOrderV2 = CancelOrder

    def BatchCancelOrders(self, orders: list[dict]):
        url = api_url("portfolio/events/orders/batched")
        return self._authenticated_del_request(url, {"orders": orders})

    BatchCancelOrdersV2 = BatchCancelOrders

    def CancelAllOrders(self, subaccount: int | None = None):
        url = api_url("portfolio/events/orders")
        return self._authenticated_del_request(
            url,
            **drop_none({"subaccount": subaccount}),
        )

    def CreateSubaccount(self, exchange_index: int | None = None):
        url = api_url("portfolio/subaccounts")
        return self._authenticated_post_request(
            url,
            drop_none({"exchange_index": exchange_index}),
        )

    def TransferBetweenSubaccounts(
        self,
        client_transfer_id: str,
        from_subaccount: int,
        to_subaccount: int,
        amount_cents: int,
        exchange_index: int | None = None,
    ):
        url = api_url("portfolio/subaccounts/transfer")
        return self._authenticated_post_request(
            url,
            drop_none(
                {
                    "client_transfer_id": client_transfer_id,
                    "from_subaccount": from_subaccount,
                    "to_subaccount": to_subaccount,
                    "amount_cents": amount_cents,
                    "exchange_index": exchange_index,
                }
            ),
        )

    def GetSubaccountBalances(self):
        url = api_url("portfolio/subaccounts/balances")
        return self._authenticated_get_request(url)

    def GetSubaccountTransfers(
        self,
        limit: int = 100,
        cursor: str | None = None,
    ):
        url = api_url("portfolio/subaccounts/transfers")
        return self._authenticated_get_request(
            url,
            **drop_none({"limit": limit, "cursor": cursor}),
        )


portfolio = Portfolio()
