from kalshi.constants import api_url

from .rest import drop_none, get, get_kwargs


class Collection:
    def GetMultivariateEventCollections(
        self,
        status: str | None = None,
        associated_event_ticker: str | None = None,
        series_ticker: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ):
        return get(
            api_url("multivariate_event_collections"),
            **drop_none(get_kwargs()),
        )

    def GetMultivariateEventCollection(self, collection_ticker: str):
        return get(api_url(f"multivariate_event_collections/{collection_ticker}"))


collection = Collection()
