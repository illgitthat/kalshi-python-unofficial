from .rest import delete, drop_none, get, get_kwargs, post
import kalshi.auth
import kalshi.constants


class ApiKeys:
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

    def GetApiKeys(self):
        return self._authenticated_get_request(
            f"{kalshi.constants.BASE_URL}{kalshi.constants.BASE_PATH}/api_keys"
        )

    def CreateApiKey(self, name: str, public_key: str, scopes: list = None):
        return self._authenticated_post_request(
            f"{kalshi.constants.BASE_URL}{kalshi.constants.BASE_PATH}/api_keys",
            drop_none(get_kwargs()),
        )

    def GenerateApiKey(self, name: str, scopes: list = None):
        return self._authenticated_post_request(
            f"{kalshi.constants.BASE_URL}{kalshi.constants.BASE_PATH}/api_keys/generate",
            drop_none(get_kwargs()),
        )

    def DeleteApiKey(self, api_key: str):
        return self._authenticated_del_request(
            f"{kalshi.constants.BASE_URL}{kalshi.constants.BASE_PATH}/api_keys/{api_key}"
        )


api_keys = ApiKeys()
