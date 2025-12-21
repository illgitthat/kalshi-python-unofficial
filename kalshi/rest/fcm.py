from .rest import drop_none, get, get_kwargs
import kalshi.auth
import kalshi.constants


class FCM:
    def _authenticated_get_request(self, url: str, **kwargs):
        return get(url, headers=kalshi.auth.request_headers("GET", url), **kwargs)

    def GetFCMOrders(
        self,
        subtrader_id: str,
        cursor: str = None,
        event_ticker: str = None,
        ticker: str = None,
        min_ts: int = None,
        max_ts: int = None,
        status: str = None,
        limit: int = None,
    ):
        return self._authenticated_get_request(
            f"{kalshi.constants.BASE_URL}{kalshi.constants.BASE_PATH}/fcm/orders",
            **drop_none(get_kwargs()),
        )

    def GetFCMPositions(
        self,
        subtrader_id: str,
        ticker: str = None,
        event_ticker: str = None,
        count_filter: str = None,
        settlement_status: str = None,
        limit: int = None,
        cursor: str = None,
    ):
        return self._authenticated_get_request(
            f"{kalshi.constants.BASE_URL}{kalshi.constants.BASE_PATH}/fcm/positions",
            **drop_none(get_kwargs()),
        )


fcm = FCM()
