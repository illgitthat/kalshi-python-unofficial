from .rest import drop_none, get, get_kwargs, post, put
import kalshi.auth
import kalshi.constants


class Collection:
    def _authenticated_post_request(self, url: str, data: dict):
        return post(url, headers=kalshi.auth.request_headers("POST", url), body=data)

    def _authenticated_put_request(self, url: str, data: dict):
        return put(url, headers=kalshi.auth.request_headers("PUT", url), body=data)

    def GetMultivariateEventCollections(
        self,
        status: str = None,
        associated_event_ticker: str = None,
        series_ticker: str = None,
        limit: int = None,
        cursor: str = None,
    ):
        return get(
            f"{kalshi.constants.BASE_URL}{kalshi.constants.BASE_PATH}/multivariate_event_collections",
            **drop_none(get_kwargs()),
        )

    def GetMultivariateEventCollection(self, collection_ticker: str):
        return get(
            f"{kalshi.constants.BASE_URL}{kalshi.constants.BASE_PATH}/multivariate_event_collections/{collection_ticker}"
        )

    def CreateMarketInMultivariateEventCollection(
        self, collection_ticker: str, selected_markets: list
    ):
        args = drop_none(get_kwargs())
        del args["collection_ticker"]
        return self._authenticated_post_request(
            f"{kalshi.constants.BASE_URL}{kalshi.constants.BASE_PATH}/multivariate_event_collections/{collection_ticker}",
            args,
        )

    def LookupTickersForMarketInMultivariateEventCollection(
        self, collection_ticker: str, selected_markets: list
    ):
        args = drop_none(get_kwargs())
        del args["collection_ticker"]
        return self._authenticated_put_request(
            f"{kalshi.constants.BASE_URL}{kalshi.constants.BASE_PATH}/multivariate_event_collections/{collection_ticker}/lookup",
            args,
        )

    def GetMultivariateEventCollectionLookupHistory(
        self, collection_ticker: str, lookback_seconds: int
    ):
        return get(
            f"{kalshi.constants.BASE_URL}{kalshi.constants.BASE_PATH}/multivariate_event_collections/{collection_ticker}/lookup",
            lookback_seconds=lookback_seconds,
        )


collection = Collection()
