from .rest import get, get_kwargs, drop_none


class Collection:
    def GetMultivariateEventCollections(
        self,
        status: str = None,
        associated_event_ticker: str = None,
        series_ticker: str = None,
        limit: int = None,
        cursor: str = None,
    ):
        return get(
            "https://api.elections.kalshi.com/trade-api/v2/multivariate_event_collections",
            **drop_none(get_kwargs()),
        )

    def GetMultivariateEventCollection(self, collection_ticker: str):
        return get(
            f"https://api.elections.kalshi.com/trade-api/v2/multivariate_event_collections/{collection_ticker}"
        )


collection = Collection()
