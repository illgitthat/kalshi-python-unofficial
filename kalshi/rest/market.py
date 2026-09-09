from kalshi.auth import request_headers
from kalshi.constants import api_url

from .pagination import paginate
from .rest import drop_none, get


class Market:
    def _authenticated_get_request(self, url: str, **kwargs):
        return get(url, headers=request_headers("GET", url), **kwargs)

    def GetEvents(
        self,
        limit: int = 200,
        cursor: str | None = None,
        status: str | None = None,
        series_ticker: str | None = None,
        with_nested_markets: bool = False,
        with_milestones: bool = False,
        tickers: list[str] | None = None,
        min_close_ts: int | None = None,
        min_updated_ts: int | None = None,
    ):
        params = drop_none(
            {
                "limit": limit,
                "cursor": cursor,
                "status": status,
                "series_ticker": series_ticker,
                "with_nested_markets": with_nested_markets,
                "with_milestones": with_milestones,
                "tickers": ",".join(tickers) if tickers else None,
                "min_close_ts": min_close_ts,
                "min_updated_ts": min_updated_ts,
            }
        )
        return get(api_url("events"), **params)

    def GetEvent(
        self,
        event_ticker: str,
        with_nested_markets: bool = False,
    ):
        return get(
            api_url(f"events/{event_ticker}"),
            with_nested_markets=with_nested_markets,
        )

    def GetEventMetadata(self, event_ticker: str):
        return get(api_url(f"events/{event_ticker}/metadata"))

    def GetEventLiveData(
        self,
        event_ticker: str,
        range: str | None = None,
    ):
        return get(
            api_url(f"live_data/events/{event_ticker}"),
            **drop_none({"range": range}),
        )

    def GetMarkets(
        self,
        limit: int = 100,
        cursor: str | None = None,
        *,
        event_ticker: str | None = None,
        series_ticker: str | None = None,
        min_created_ts: int | None = None,
        max_created_ts: int | None = None,
        min_updated_ts: int | None = None,
        max_close_ts: int | None = None,
        min_close_ts: int | None = None,
        min_settled_ts: int | None = None,
        max_settled_ts: int | None = None,
        status: str | None = None,
        tickers: list[str] | None = None,
        mve_filter: str | None = None,
    ):
        params = drop_none(
            {
                "limit": limit,
                "cursor": cursor,
                "event_ticker": event_ticker,
                "series_ticker": series_ticker,
                "min_created_ts": min_created_ts,
                "max_created_ts": max_created_ts,
                "min_updated_ts": min_updated_ts,
                "max_close_ts": max_close_ts,
                "min_close_ts": min_close_ts,
                "min_settled_ts": min_settled_ts,
                "max_settled_ts": max_settled_ts,
                "status": status,
                "tickers": ",".join(tickers) if tickers else None,
                "mve_filter": mve_filter,
            }
        )
        return get(api_url("markets"), **params)

    def GetTrades(
        self,
        cursor: str | None = None,
        limit: int = 100,
        ticker: str | None = None,
        min_ts: int | None = None,
        max_ts: int | None = None,
        is_block_trade: bool | None = None,
    ):
        return get(
            api_url("markets/trades"),
            **drop_none(
                {
                    "cursor": cursor,
                    "limit": limit,
                    "ticker": ticker,
                    "min_ts": min_ts,
                    "max_ts": max_ts,
                    "is_block_trade": is_block_trade,
                }
            ),
        )

    def GetMarket(self, ticker: str):
        return get(api_url(f"markets/{ticker}"))

    def GetMarketOrderbook(self, ticker: str, depth: int | None = None):
        url = api_url(f"markets/{ticker}/orderbook")
        return self._authenticated_get_request(url, depth=depth)

    def GetSeries(self, series_ticker: str, include_volume: bool = False):
        return get(
            api_url(f"series/{series_ticker}"),
            include_volume=include_volume,
        )

    def GetMarketCandlesticks(
        self,
        ticker: str,
        series_ticker: str,
        start_ts: int,
        end_ts: int,
        period_interval: int,
        include_latest_before_start: bool = False,
    ):
        return get(
            api_url(f"series/{series_ticker}/markets/{ticker}/candlesticks"),
            start_ts=start_ts,
            end_ts=end_ts,
            period_interval=period_interval,
            include_latest_before_start=include_latest_before_start,
        )

    def GetLiveMarkets(self, **kwargs):
        return self.GetMarkets(status="open", **kwargs)

    def GetUpcomingMarkets(self, **kwargs):
        return self.GetMarkets(status="unopened", **kwargs)

    def GetLiveEvents(self, with_nested_markets: bool = False, **kwargs):
        return self.GetEvents(
            status="open",
            with_nested_markets=with_nested_markets,
            **kwargs,
        )

    def GetUpcomingEvents(self, with_nested_markets: bool = False, **kwargs):
        return self.GetEvents(
            status="unopened",
            with_nested_markets=with_nested_markets,
            **kwargs,
        )

    def IterMarkets(self, *, max_pages: int | None = None, **params):
        return paginate(
            self.GetMarkets,
            "markets",
            max_pages=max_pages,
            **params,
        )

    def IterEvents(self, *, max_pages: int | None = None, **params):
        return paginate(
            self.GetEvents,
            "events",
            max_pages=max_pages,
            **params,
        )


market = Market()
