from .rest import delete, get, get_kwargs, drop_none, post, put
import kalshi.auth
import kalshi.constants


class Portfolio:
    def _authenticated_get_request(self, url: str, **kwargs):
        return get(url, headers=kalshi.auth.request_headers("GET", url), **kwargs)

    def _authenticated_post_request(
        self, url: str, data: dict, expected_status=(200, 201)
    ):
        return post(
            url,
            headers=kalshi.auth.request_headers("POST", url),
            body=data,
            expected_status=expected_status,
        )

    def _authenticated_del_request(self, url: str, data: dict = None):
        return delete(
            url, headers=kalshi.auth.request_headers("DELETE", url), body=data
        )

    def _authenticated_put_request(self, url: str, data: dict = None):
        return put(
            url, headers=kalshi.auth.request_headers("PUT", url), body=data
        )

    def GetBalance(self):
        return self._authenticated_get_request(
            f"{kalshi.constants.BASE_URL}{kalshi.constants.BASE_PATH}/portfolio/balance"
        )

    def GetFills(
        self,
        ticker: str = None,
        order_id: str = None,
        min_ts: int = None,
        max_ts: int = None,
        limit: int = 100,
        cursor: str = None,
    ):
        return self._authenticated_get_request(
            f"{kalshi.constants.BASE_URL}{kalshi.constants.BASE_PATH}/portfolio/fills",
            **drop_none(get_kwargs()),
        )

    def GetOrders(
        self,
        ticker: str = None,
        event_ticker: str = None,
        min_ts: int = None,
        max_ts: int = None,
        status: str = None,
        cursor: str = None,
        limit: int = 100,
    ):
        return self._authenticated_get_request(
            f"{kalshi.constants.BASE_URL}{kalshi.constants.BASE_PATH}/portfolio/orders",
            **drop_none(get_kwargs()),
        )

    def GetOrder(self, order_id: str):
        return self._authenticated_get_request(
            f"{kalshi.constants.BASE_URL}{kalshi.constants.BASE_PATH}/portfolio/orders/{order_id}"
        )

    def GetOrderQueuePositions(
        self, market_tickers=None, event_ticker: str = None
    ):
        args = drop_none(get_kwargs())
        if "market_tickers" in args and isinstance(args["market_tickers"], list):
            args["market_tickers"] = ",".join(args["market_tickers"])
        return self._authenticated_get_request(
            f"{kalshi.constants.BASE_URL}{kalshi.constants.BASE_PATH}/portfolio/orders/queue_positions",
            **args,
        )

    def GetOrderQueuePosition(self, order_id: str):
        return self._authenticated_get_request(
            f"{kalshi.constants.BASE_URL}{kalshi.constants.BASE_PATH}/portfolio/orders/{order_id}/queue_position"
        )

    def GetOrderGroups(self):
        return self._authenticated_get_request(
            f"{kalshi.constants.BASE_URL}{kalshi.constants.BASE_PATH}/portfolio/order_groups"
        )

    def CreateOrderGroup(self, contracts_limit: int):
        return self._authenticated_post_request(
            f"{kalshi.constants.BASE_URL}{kalshi.constants.BASE_PATH}/portfolio/order_groups/create",
            drop_none(get_kwargs()),
        )

    def GetOrderGroup(self, order_group_id: str):
        return self._authenticated_get_request(
            f"{kalshi.constants.BASE_URL}{kalshi.constants.BASE_PATH}/portfolio/order_groups/{order_group_id}"
        )

    def DeleteOrderGroup(self, order_group_id: str):
        return self._authenticated_del_request(
            f"{kalshi.constants.BASE_URL}{kalshi.constants.BASE_PATH}/portfolio/order_groups/{order_group_id}"
        )

    def ResetOrderGroup(self, order_group_id: str):
        args = drop_none(get_kwargs())
        del args["order_group_id"]
        return self._authenticated_put_request(
            f"{kalshi.constants.BASE_URL}{kalshi.constants.BASE_PATH}/portfolio/order_groups/{order_group_id}/reset",
            args or {},
        )

    def GetPositions(
        self,
        cursor: str = None,
        limit: int = 100,
        count_filter: str = None,
        ticker: str = None,
        event_ticker: str = None,
    ):
        return self._authenticated_get_request(
            f"{kalshi.constants.BASE_URL}{kalshi.constants.BASE_PATH}/portfolio/positions",
            **drop_none(get_kwargs()),
        )

    def GetSettlements(
        self,
        limit: int = 100,
        min_ts: int = None,
        max_ts: int = None,
        cursor: str = None,
        ticker: str = None,
        event_ticker: str = None,
    ):
        return self._authenticated_get_request(
            f"{kalshi.constants.BASE_URL}{kalshi.constants.BASE_PATH}/portfolio/settlements",
            **drop_none(get_kwargs()),
        )

    def GetPortfolioSettlements(
        self,
        limit: int = 100,
        min_ts: int = None,
        max_ts: int = None,
        cursor: str = None,
        ticker: str = None,
        event_ticker: str = None,
    ):
        return self.GetSettlements(limit, min_ts, max_ts, cursor, ticker, event_ticker)

    def GetPortfolioRestingOrderTotalValue(self):
        return self._authenticated_get_request(
            f"{kalshi.constants.BASE_URL}{kalshi.constants.BASE_PATH}/portfolio/summary/total_resting_order_value"
        )

    def CreateOrder(
        self,
        action: str,
        client_order_id: str,
        count: int,
        side: str,
        ticker: str,
        type: str = None,
        yes_price: int = None,
        no_price: int = None,
        yes_price_dollars: str = None,
        no_price_dollars: str = None,
        expiration_ts: int = None,
        time_in_force: str = None,
        buy_max_cost: int = None,
        post_only: bool = None,
        reduce_only: bool = None,
        sell_position_floor: int = None,
        self_trade_prevention_type: str = None,
        order_group_id: str = None,
        cancel_order_on_pause: bool = None,
    ):
        return self._authenticated_post_request(
            f"{kalshi.constants.BASE_URL}{kalshi.constants.BASE_PATH}/portfolio/orders",
            drop_none(get_kwargs()),
        )

    def BatchCreateOrders(self, orders: list):
        return self._authenticated_post_request(
            f"{kalshi.constants.BASE_URL}{kalshi.constants.BASE_PATH}/portfolio/orders/batched",
            drop_none(get_kwargs()),
        )

    def BatchCancelOrders(self, ids: list):
        return self._authenticated_del_request(
            f"{kalshi.constants.BASE_URL}{kalshi.constants.BASE_PATH}/portfolio/orders/batched",
            drop_none(get_kwargs()),
        )

    def AmendOrder(
        self,
        order_id: str,
        action: str,
        client_order_id: str,
        side: str,
        ticker: str,
        updated_client_order_id: str,
        yes_price: int = None,
        no_price: int = None,
        yes_price_dollars: str = None,
        no_price_dollars: str = None,
        count: int = None,
    ):
        args = drop_none(get_kwargs())
        del args["order_id"]
        return self._authenticated_post_request(
            f"{kalshi.constants.BASE_URL}{kalshi.constants.BASE_PATH}/portfolio/orders/{order_id}/amend",
            args,
        )

    def DecreaseOrder(
        self, order_id: str, reduce_by: int = None, reduce_to: int = None
    ):
        args = drop_none(get_kwargs())
        del args["order_id"]
        return self._authenticated_post_request(
            f"{kalshi.constants.BASE_URL}{kalshi.constants.BASE_PATH}/portfolio/orders/{order_id}/decrease",
            args,
        )

    def CancelOrder(self, order_id: str):
        return self._authenticated_del_request(
            f"{kalshi.constants.BASE_URL}{kalshi.constants.BASE_PATH}/portfolio/orders/{order_id}"
        )


portfolio = Portfolio()
