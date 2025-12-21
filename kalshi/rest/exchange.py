from .rest import drop_none, get, get_kwargs
import kalshi.constants


class Exchange:
    def GetExchangeAnnouncements(self):
        return get(
            f"{kalshi.constants.BASE_URL}{kalshi.constants.BASE_PATH}/exchange/announcements"
        )

    def GetExchangeSchedule(self):
        return get(
            f"{kalshi.constants.BASE_URL}{kalshi.constants.BASE_PATH}/exchange/schedule"
        )

    def GetExchangeStatus(self):
        return get(
            f"{kalshi.constants.BASE_URL}{kalshi.constants.BASE_PATH}/exchange/status"
        )

    def GetSeriesFeeChanges(self, series_ticker: str = None, show_historical: bool = False):
        return get(
            f"{kalshi.constants.BASE_URL}{kalshi.constants.BASE_PATH}/series/fee_changes",
            **drop_none(get_kwargs()),
        )

    def GetUserDataTimestamp(self):
        return get(
            f"{kalshi.constants.BASE_URL}{kalshi.constants.BASE_PATH}/exchange/user_data_timestamp"
        )


exchange = Exchange()
