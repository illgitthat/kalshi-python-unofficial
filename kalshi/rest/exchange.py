from kalshi.constants import api_url

from .rest import get


class Exchange:
    def GetExchangeAnnouncements(self):
        raise NotImplementedError(
            "The current Kalshi OpenAPI specification does not expose "
            "/exchange/announcements."
        )

    def GetExchangeSchedule(self):
        return get(api_url("exchange/schedule"))

    def GetExchangeStatus(self):
        return get(api_url("exchange/status"))


exchange = Exchange()
