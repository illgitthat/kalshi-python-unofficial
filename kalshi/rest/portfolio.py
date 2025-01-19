from .rest import get, get_kwargs, drop_none
import kalshi.auth
import datetime
import urllib.parse
import requests
import json


class Portfolio:
    def _authenticated_get_request(self, url: str, **kwargs):
        current_time = datetime.datetime.now()
        timestamp = current_time.timestamp()
        current_time_milliseconds = int(timestamp * 1000)
        timestamp_str = str(current_time_milliseconds)
        sig = kalshi.auth.signer.sign(
            timestamp_str + "GET" + urllib.parse.urlparse(url).path
        )
        headers = {
            "KALSHI-ACCESS-KEY": kalshi.auth.API_ACCESS_KEY,
            "KALSHI-ACCESS-SIGNATURE": sig,
            "KALSHI-ACCESS-TIMESTAMP": timestamp_str,
        }
        return get(url, headers, **kwargs)

    def _authenticated_post_request(self, url: str, data: dict):
        current_time = datetime.datetime.now()
        timestamp = current_time.timestamp()
        current_time_milliseconds = int(timestamp * 1000)
        timestamp_str = str(current_time_milliseconds)
        sig = kalshi.auth.signer.sign(
            timestamp_str + "POST" + urllib.parse.urlparse(url).path
        )
        headers = {
            "KALSHI-ACCESS-KEY": kalshi.auth.API_ACCESS_KEY,
            "KALSHI-ACCESS-SIGNATURE": sig,
            "KALSHI-ACCESS-TIMESTAMP": timestamp_str,
        }
        response = requests.post(url, headers=headers, json=data)
        if response.status_code != 201:
            raise Exception(response.content.decode())
        return json.loads(response.content)

    def _authenticated_del_request(self, url: str, data: dict = None):
        current_time = datetime.datetime.now()
        timestamp = current_time.timestamp()
        current_time_milliseconds = int(timestamp * 1000)
        timestamp_str = str(current_time_milliseconds)
        sig = kalshi.auth.signer.sign(
            timestamp_str + "DELETE" + urllib.parse.urlparse(url).path
        )
        headers = {
            "KALSHI-ACCESS-KEY": kalshi.auth.API_ACCESS_KEY,
            "KALSHI-ACCESS-SIGNATURE": sig,
            "KALSHI-ACCESS-TIMESTAMP": timestamp_str,
        }
        if data is not None:
            response = requests.delete(url, headers=headers, json=data)
        else:
            response = requests.delete(url, headers=headers)
        if response.status_code != 200:
            raise Exception(response.content.decode())
        return json.loads(response.content)

    def GetBalance(self):
        return self._authenticated_get_request(
            "https://api.elections.kalshi.com/trade-api/v2/portfolio/balance"
        )

    def GetFills(
        self,
        ticker: str = None,
        order_id: str = None,
        min_ts: int = None,
        max_ts: int = None,
        limit: int = 100,
        cursor: str = None,
    ):
        return self._authenticated_get_request(
            "https://api.elections.kalshi.com/trade-api/v2/portfolio/fills",
            **drop_none(get_kwargs()),
        )

    def GetOrders(
        self,
        ticker: str = None,
        event_ticker: str = None,
        min_ts: int = None,
        max_ts: int = None,
        status: str = None,
        cursor: str = None,
        limit: int = 100,
    ):
        return self._authenticated_get_request(
            "https://api.elections.kalshi.com/trade-api/v2/portfolio/orders",
            **drop_none(get_kwargs()),
        )

    def GetOrder(self, order_id: str):
        return self._authenticated_get_request(
            f"https://api.elections.kalshi.com/trade-api/v2/portfolio/orders/{order_id}"
        )

    def GetPositions(
        self,
        cursor: str = None,
        limit: int = 100,
        count_filter: str = None,
        settlement_status: str = None,
        ticker: str = None,
        event_ticker: str = None,
    ):
        return self._authenticated_get_request(
            "https://api.elections.kalshi.com/trade-api/v2/portfolio/positions",
            **drop_none(get_kwargs()),
        )

    def GetPortfolioSettlements(
        self,
        limit: int = 100,
        min_ts: int = None,
        max_ts: int = None,
        cursor: str = None,
    ):
        return self._authenticated_get_request(
            "https://api.elections.kalshi.com/trade-api/v2/portfolio/settlements",
            **drop_none(get_kwargs()),
        )

    def GetPortfolioRestingOrderTotalValue(self):
        return self._authenticated_get_request(
            "https://api.elections.kalshi.com/trade-api/v2/portfolio/summary/total_resting_order_value"
        )

    def CreateOrder(
        self,
        action: str,
        client_order_id: str,
        count: int,
        side: str,
        ticker: str,
        type: str,
        buy_max_cost: int = None,
        expiration_ts: int = None,
        no_price: int = None,
        post_only: bool = None,
        sell_position_floor: int = None,
        yes_price: int = None,
    ):
        return self._authenticated_post_request(
            "https://api.elections.kalshi.com/trade-api/v2/portfolio/orders",
            drop_none(get_kwargs()),
        )

    def AmendOrder(
        self,
        order_id: str,
        action: str,
        client_order_id: str,
        count: int,
        side: str,
        ticker: str,
        updated_client_order_id: str,
        no_price: int = None,
        yes_price: int = None,
    ):
        args = drop_none(get_kwargs())
        del args["order_id"]
        return self._authenticated_post_request(
            f"https://api.elections.kalshi.com/trade-api/v2/portfolio/orders/{order_id}/amend",
            args,
        )

    def DecreaseOrder(
        self, order_id: str, reduce_by: int = None, reduce_to: int = None
    ):
        args = drop_none(get_kwargs())
        del args["order_id"]
        return self._authenticated_post_request(
            f"https://api.elections.kalshi.com/trade-api/v2/portfolio/orders/{order_id}/decrease",
            args,
        )

    def CancelOrder(self, order_id: str):
        return self._authenticated_del_request(
            f"https://api.elections.kalshi.com/trade-api/v2/portfolio/orders/{order_id}"
        )


portfolio = Portfolio()

# portfolio._authenticated_get_request(
#    "https://api.elections.kalshi.com/trade-api/v2/portfolio/balance"
# )
