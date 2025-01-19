from .rest import get, get_kwargs, drop_none
import kalshi.constants


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
            f"{kalshi.constants.BASE_URL}{kalshi.constants.BASE_PATH}/multivariate_event_collections",
            **drop_none(get_kwargs()),
        )

    def GetMultivariateEventCollection(self, collection_ticker: str):
        return get(
            f"{kalshi.constants.BASE_URL}{kalshi.constants.BASE_PATH}/multivariate_event_collections/{collection_ticker}"
        )


collection = Collection()
