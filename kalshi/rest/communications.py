from .rest import delete, drop_none, get, get_kwargs, post, put
import kalshi.auth
import kalshi.constants


class Communications:
    def _authenticated_get_request(self, url: str, **kwargs):
        return get(url, headers=kalshi.auth.request_headers("GET", url), **kwargs)

    def _authenticated_post_request(self, url: str, data: dict):
        return post(
            url,
            headers=kalshi.auth.request_headers("POST", url),
            body=data,
        )

    def _authenticated_del_request(self, url: str):
        return delete(
            url, headers=kalshi.auth.request_headers("DELETE", url)
        )

    def _authenticated_put_request(self, url: str, data: dict):
        return put(
            url, headers=kalshi.auth.request_headers("PUT", url), body=data
        )

    def GetCommunicationsID(self):
        return self._authenticated_get_request(
            f"{kalshi.constants.BASE_URL}{kalshi.constants.BASE_PATH}/communications/id"
        )

    def GetRFQs(
        self,
        cursor: str = None,
        event_ticker: str = None,
        market_ticker: str = None,
        limit: int = 100,
        status: str = None,
        creator_user_id: str = None,
    ):
        return self._authenticated_get_request(
            f"{kalshi.constants.BASE_URL}{kalshi.constants.BASE_PATH}/communications/rfqs",
            **drop_none(get_kwargs()),
        )

    def CreateRFQ(
        self,
        market_ticker: str,
        rest_remainder: bool,
        contracts: int = None,
        target_cost_centi_cents: int = None,
        replace_existing: bool = None,
        subtrader_id: str = None,
    ):
        return self._authenticated_post_request(
            f"{kalshi.constants.BASE_URL}{kalshi.constants.BASE_PATH}/communications/rfqs",
            drop_none(get_kwargs()),
        )

    def GetRFQ(self, rfq_id: str):
        return self._authenticated_get_request(
            f"{kalshi.constants.BASE_URL}{kalshi.constants.BASE_PATH}/communications/rfqs/{rfq_id}"
        )

    def DeleteRFQ(self, rfq_id: str):
        return self._authenticated_del_request(
            f"{kalshi.constants.BASE_URL}{kalshi.constants.BASE_PATH}/communications/rfqs/{rfq_id}"
        )

    def GetQuotes(
        self,
        cursor: str = None,
        event_ticker: str = None,
        market_ticker: str = None,
        limit: int = 500,
        status: str = None,
        quote_creator_user_id: str = None,
        rfq_creator_user_id: str = None,
        rfq_creator_subtrader_id: str = None,
        rfq_id: str = None,
    ):
        return self._authenticated_get_request(
            f"{kalshi.constants.BASE_URL}{kalshi.constants.BASE_PATH}/communications/quotes",
            **drop_none(get_kwargs()),
        )

    def CreateQuote(
        self,
        rfq_id: str,
        yes_bid,
        no_bid,
        rest_remainder: bool,
    ):
        return self._authenticated_post_request(
            f"{kalshi.constants.BASE_URL}{kalshi.constants.BASE_PATH}/communications/quotes",
            drop_none(get_kwargs()),
        )

    def GetQuote(self, quote_id: str):
        return self._authenticated_get_request(
            f"{kalshi.constants.BASE_URL}{kalshi.constants.BASE_PATH}/communications/quotes/{quote_id}"
        )

    def DeleteQuote(self, quote_id: str):
        return self._authenticated_del_request(
            f"{kalshi.constants.BASE_URL}{kalshi.constants.BASE_PATH}/communications/quotes/{quote_id}"
        )

    def AcceptQuote(self, quote_id: str, accepted_side: str):
        args = drop_none(get_kwargs())
        del args["quote_id"]
        return self._authenticated_put_request(
            f"{kalshi.constants.BASE_URL}{kalshi.constants.BASE_PATH}/communications/quotes/{quote_id}/accept",
            args,
        )

    def ConfirmQuote(self, quote_id: str):
        return self._authenticated_put_request(
            f"{kalshi.constants.BASE_URL}{kalshi.constants.BASE_PATH}/communications/quotes/{quote_id}/confirm",
            {},
        )


communications = Communications()
