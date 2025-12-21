from .rest import drop_none, get, get_kwargs
import kalshi.constants


class StructuredTargets:
    def GetStructuredTargets(
        self,
        type: str = None,
        competition: str = None,
        page_size: int = 100,
        cursor: str = None,
    ):
        return get(
            f"{kalshi.constants.BASE_URL}{kalshi.constants.BASE_PATH}/structured_targets",
            **drop_none(get_kwargs()),
        )

    def GetStructuredTarget(self, structured_target_id: str):
        return get(
            f"{kalshi.constants.BASE_URL}{kalshi.constants.BASE_PATH}/structured_targets/{structured_target_id}"
        )


structured_targets = StructuredTargets()
