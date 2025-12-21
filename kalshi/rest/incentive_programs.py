from .rest import drop_none, get, get_kwargs
import kalshi.constants


class IncentivePrograms:
    def GetIncentivePrograms(
        self,
        status: str = None,
        type: str = None,
        limit: int = None,
        cursor: str = None,
    ):
        return get(
            f"{kalshi.constants.BASE_URL}{kalshi.constants.BASE_PATH}/incentive_programs",
            **drop_none(get_kwargs()),
        )


incentive_programs = IncentivePrograms()
