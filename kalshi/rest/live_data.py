from .rest import drop_none, get, get_kwargs
import kalshi.constants


class LiveData:
    def GetLiveData(self, type: str, milestone_id: str):
        return get(
            f"{kalshi.constants.BASE_URL}{kalshi.constants.BASE_PATH}/live_data/{type}/milestone/{milestone_id}"
        )

    def GetLiveDatas(self, milestone_ids: list):
        return get(
            f"{kalshi.constants.BASE_URL}{kalshi.constants.BASE_PATH}/live_data/batch",
            **drop_none(get_kwargs()),
        )


live_data = LiveData()
