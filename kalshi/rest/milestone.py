from kalshi.constants import api_url

from .pagination import paginate
from .rest import drop_none, get


class Milestone:
    def GetMilestones(
        self,
        limit: int = 100,
        minimum_start_date: str | None = None,
        category: str | None = None,
        competition: str | None = None,
        source_id: str | None = None,
        type: str | None = None,
        related_event_ticker: str | None = None,
        cursor: str | None = None,
        min_updated_ts: int | None = None,
    ):
        return get(
            api_url("milestones"),
            **drop_none(
                {
                    "limit": limit,
                    "minimum_start_date": minimum_start_date,
                    "category": category,
                    "competition": competition,
                    "source_id": source_id,
                    "type": type,
                    "related_event_ticker": related_event_ticker,
                    "cursor": cursor,
                    "min_updated_ts": min_updated_ts,
                }
            ),
        )

    def GetMilestone(self, milestone_id: str):
        return get(api_url(f"milestones/{milestone_id}"))

    def GetLiveData(
        self,
        milestone_id: str,
        include_player_stats: bool = False,
    ):
        return get(
            api_url(f"live_data/milestone/{milestone_id}"),
            include_player_stats=include_player_stats,
        )

    def IterMilestones(self, *, max_pages: int | None = None, **params):
        return paginate(
            self.GetMilestones,
            "milestones",
            max_pages=max_pages,
            **params,
        )


milestone = Milestone()
