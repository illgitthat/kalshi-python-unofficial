from fastkalshi.auth import request_headers
from fastkalshi.constants import api_url

from .rest import get


class Account:
    def GetLimits(self):
        url = api_url("account/limits")
        return get(url, headers=request_headers("GET", url))

    def GetEndpointCosts(self):
        return get(api_url("account/endpoint_costs"))


account = Account()
