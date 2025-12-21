from .rest import get, get_kwargs, drop_none
import kalshi.auth
import kalshi.constants


class Market:
    def _authenticated_get_request(self, url: str, **kwargs):
        return get(url, headers=kalshi.auth.request_headers("GET", url), **kwargs)

    def GetEvents(
        self,
        limit: int = 200,
        cursor: str = None,
        with_nested_markets: bool = False,
        with_milestones: bool = False,
        status: str = None,
        series_ticker: str = None,
        min_close_ts: int = None,
    ):
        return get(
            f"{kalshi.constants.BASE_URL}{kalshi.constants.BASE_PATH}/events",
            **drop_none(get_kwargs()),
        )

    def GetMultivariateEvents(
        self,
        limit: int = 100,
        cursor: str = None,
        series_ticker: str = None,
        collection_ticker: str = None,
        with_nested_markets: bool = False,
    ):
        return get(
            f"{kalshi.constants.BASE_URL}{kalshi.constants.BASE_PATH}/events/multivariate",
            **drop_none(get_kwargs()),
        )

    def GetEvent(self, event_ticker: str, with_nested_markets: bool = False):
        return get(
            f"{kalshi.constants.BASE_URL}{kalshi.constants.BASE_PATH}/events/{event_ticker}",
            with_nested_markets=with_nested_markets,
        )

    def GetEventMetadata(self, event_ticker: str):
        return get(
            f"{kalshi.constants.BASE_URL}{kalshi.constants.BASE_PATH}/events/{event_ticker}/metadata"
        )

    def GetEventForecastPercentilesHistory(
        self,
        series_ticker: str,
        ticker: str,
        percentiles: list[int],
        start_ts: int,
        end_ts: int,
        period_interval: int,
    ):
        args = drop_none(get_kwargs())
        del args["series_ticker"]
        del args["ticker"]
        return self._authenticated_get_request(
            f"{kalshi.constants.BASE_URL}{kalshi.constants.BASE_PATH}/series/{series_ticker}/events/{ticker}/forecast_percentile_history",
            **args,
        )

    def GetMarkets(
        self,
        limit: int = 100,
        cursor: str = None,
        event_ticker: str = None,
        series_ticker: str = None,
        min_created_ts: int = None,
        max_created_ts: int = None,
        max_close_ts: int = None,
        min_close_ts: int = None,
        min_settled_ts: int = None,
        max_settled_ts: int = None,
        status: str = None,
        tickers=None,
        mve_filter: str = None,
    ):
        args = drop_none(get_kwargs())
        if "tickers" in args and isinstance(args["tickers"], list):
            args["tickers"] = ",".join(args["tickers"])
        return get(
            f"{kalshi.constants.BASE_URL}{kalshi.constants.BASE_PATH}/markets",
            **args,
        )

    def GetTrades(
        self,
        cursor: str = None,
        limit: int = 100,
        ticker: str = None,
        min_ts: int = None,
        max_ts: int = None,
    ):
        return get(
            f"{kalshi.constants.BASE_URL}{kalshi.constants.BASE_PATH}/markets/trades",
            **drop_none(get_kwargs()),
        )

    def GetMarket(self, ticker: str):
        return get(
            f"{kalshi.constants.BASE_URL}{kalshi.constants.BASE_PATH}/markets/{ticker}"
        )

    def GetMarketOrderbook(self, ticker: str, depth: int = 0):
        args = drop_none(get_kwargs())
        del args["ticker"]
        return self._authenticated_get_request(
            f"{kalshi.constants.BASE_URL}{kalshi.constants.BASE_PATH}/markets/{ticker}/orderbook",
            **args,
        )

    def GetSeries(self, series_ticker: str):
        return get(
            f"{kalshi.constants.BASE_URL}{kalshi.constants.BASE_PATH}/series/{series_ticker}"
        )

    def GetSeriesList(
        self,
        category: str = None,
        tags=None,
        include_product_metadata: bool = False,
    ):
        args = drop_none(get_kwargs())
        if "tags" in args and isinstance(args["tags"], list):
            args["tags"] = ",".join(args["tags"])
        return get(
            f"{kalshi.constants.BASE_URL}{kalshi.constants.BASE_PATH}/series",
            **args,
        )

    def GetMarketCandlesticks(
        self,
        series_ticker: str,
        ticker: str,
        start_ts: int,
        end_ts: int,
        period_interval: int,
    ):
        return get(
            f"{kalshi.constants.BASE_URL}{kalshi.constants.BASE_PATH}/series/{series_ticker}/markets/{ticker}/candlesticks",
            start_ts=start_ts,
            end_ts=end_ts,
            period_interval=period_interval,
        )

    def GetMarketCandlesticksByEvent(
        self,
        series_ticker: str,
        ticker: str,
        start_ts: int,
        end_ts: int,
        period_interval: int,
    ):
        return get(
            f"{kalshi.constants.BASE_URL}{kalshi.constants.BASE_PATH}/series/{series_ticker}/events/{ticker}/candlesticks",
            start_ts=start_ts,
            end_ts=end_ts,
            period_interval=period_interval,
        )

    def BatchGetMarketCandlesticks(
        self,
        market_tickers,
        start_ts: int,
        end_ts: int,
        period_interval: int,
        include_latest_before_start: bool = False,
    ):
        args = drop_none(get_kwargs())
        if "market_tickers" in args and isinstance(args["market_tickers"], list):
            args["market_tickers"] = ",".join(args["market_tickers"])
        return get(
            f"{kalshi.constants.BASE_URL}{kalshi.constants.BASE_PATH}/markets/candlesticks",
            **args,
        )


market = Market()
