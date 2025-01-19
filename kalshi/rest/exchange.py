from .rest import get


class Exchange:
    def GetExchangeAnnouncements(self):
        return get(
            "https://api.elections.kalshi.com/trade-api/v2/exchange/announcements"
        )

    def GetExchangeSchedule(self):
        return get("https://api.elections.kalshi.com/trade-api/v2/exchange/schedule")

    def GetExchangeStatus(self):
        return get("https://api.elections.kalshi.com/trade-api/v2/exchange/status")


exchange = Exchange()
