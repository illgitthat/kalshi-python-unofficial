from .rest import get
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


exchange = Exchange()
