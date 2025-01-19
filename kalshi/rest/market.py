from .rest import get, get_kwargs, drop_none


class Market:
    def GetEvents(
        self,
        limit: int = 100,
        cursor: str = None,
        status: str = None,
        series_ticker: str = None,
        with_nested_markets: bool = False,
    ):
        return get(
            "https://api.elections.kalshi.com/trade-api/v2/events",
            **drop_none(get_kwargs()),
        )

    def GetEvent(
        self,
        event_ticker: str,
        with_nested_markets: bool = False,
    ):
        return get(
            f"https://api.elections.kalshi.com/trade-api/v2/events/{event_ticker}",
            with_nested_markets=with_nested_markets,
        )

    def GetMarkets(
        self,
        limit: int = 100,
        cursor: str = None,
        event_ticker: str = None,
        series_ticker: str = None,
        max_close_ts: int = None,
        min_close_ts: int = None,
        status: str = None,
        tickers: list[str] = None,
    ):
        args = drop_none(get_kwargs())
        if "tickers" in args:
            args["tickers"] = ",".join(args["tickers"])
        return get(
            "https://api.elections.kalshi.com/trade-api/v2/markets",
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
            "https://api.elections.kalshi.com/trade-api/v2/markets/trades",
            **drop_none(get_kwargs()),
        )

    def GetMarket(self, ticker: str):
        return get(f"https://api.elections.kalshi.com/trade-api/v2/markets/{ticker}")

    def GetMarketOrderbook(self, ticker: str, depth: int = None):
        if depth is not None:
            return get(
                f"https://api.elections.kalshi.com/trade-api/v2/markets/{ticker}/orderbook",
                depth=depth,
            )
        else:
            return get(
                f"https://api.elections.kalshi.com/trade-api/v2/markets/{ticker}/orderbook"
            )

    def GetSeries(self, series_ticker: str):
        return get(
            f"https://api.elections.kalshi.com/trade-api/v2/series/{series_ticker}"
        )

    def GetMarketCandlesticks(
        self,
        ticker: str,
        series_ticker: str,
        start_ts: int,
        end_ts: int,
        period_interval: int,
    ):
        return get(
            f"https://api.elections.kalshi.com/trade-api/v2/series/{series_ticker}/markets/{ticker}/candlesticks",
            start_ts=start_ts,
            end_ts=end_ts,
            period_interval=period_interval,
        )


market = Market()
