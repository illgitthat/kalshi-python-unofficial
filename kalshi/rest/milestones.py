from .rest import drop_none, get, get_kwargs
import kalshi.constants


class Milestones:
    def GetMilestone(self, milestone_id: str):
        return get(
            f"{kalshi.constants.BASE_URL}{kalshi.constants.BASE_PATH}/milestones/{milestone_id}"
        )

    def GetMilestones(
        self,
        limit: int,
        minimum_start_date: str = None,
        category: str = None,
        competition: str = None,
        source_id: str = None,
        type: str = None,
        related_event_ticker: str = None,
        cursor: str = None,
    ):
        return get(
            f"{kalshi.constants.BASE_URL}{kalshi.constants.BASE_PATH}/milestones",
            **drop_none(get_kwargs()),
        )


milestones = Milestones()
