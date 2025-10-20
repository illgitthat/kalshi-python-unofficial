from .rest import get, post, delete, get_kwargs, drop_none
import kalshi.auth
import kalshi.constants


class Portfolio:
    def _authenticated_get_request(self, url: str, **kwargs):
        return get(url, headers=kalshi.auth.request_headers("GET", url), **kwargs)

    def _authenticated_post_request(self, url: str, data: dict):
        return post(url, headers=kalshi.auth.request_headers("POST", url), body=data)

    def _authenticated_del_request(self, url: str, data: dict = None):
        return delete(
            url, headers=kalshi.auth.request_headers("DELETE", url), json=data
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

    def GetPositions(
        self,
        cursor: str = None,
        limit: int = 100,
        count_filter: str = None,
        settlement_status: str = None,
        ticker: str = None,
        event_ticker: str = None,
    ):
        return self._authenticated_get_request(
            f"{kalshi.constants.BASE_URL}{kalshi.constants.BASE_PATH}/portfolio/positions",
            **drop_none(get_kwargs()),
        )

    def GetPortfolioSettlements(
        self,
        limit: int = 100,
        min_ts: int = None,
        max_ts: int = None,
        cursor: str = None,
    ):
        return self._authenticated_get_request(
            f"{kalshi.constants.BASE_URL}{kalshi.constants.BASE_PATH}/portfolio/settlements",
            **drop_none(get_kwargs()),
        )

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
        type: str,
        buy_max_cost: int = None,
        expiration_ts: int = None,
        no_price: int = None,
        post_only: bool = None,
        sell_position_floor: int = None,
        yes_price: int = None,
        time_in_force: str = None
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

    def AmendOrder(
        self,
        order_id: str,
        action: str,
        client_order_id: str,
        count: int,
        side: str,
        ticker: str,
        updated_client_order_id: str,
        no_price: int = None,
        yes_price: int = None,
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
