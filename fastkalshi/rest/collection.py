from fastkalshi.constants import api_url

from .rest import drop_none, get


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
            **drop_none(
                {
                    "status": status,
                    "associated_event_ticker": associated_event_ticker,
                    "series_ticker": series_ticker,
                    "limit": limit,
                    "cursor": cursor,
                }
            ),
        )

    def GetMultivariateEventCollection(self, collection_ticker: str):
        return get(api_url(f"multivariate_event_collections/{collection_ticker}"))


collection = Collection()
