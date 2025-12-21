from .rest import get
import kalshi.constants


class Search:
    def GetTagsForSeriesCategories(self):
        return get(
            f"{kalshi.constants.BASE_URL}{kalshi.constants.BASE_PATH}/search/tags_by_categories"
        )

    def GetFiltersForSports(self):
        return get(
            f"{kalshi.constants.BASE_URL}{kalshi.constants.BASE_PATH}/search/filters_by_sport"
        )


search = Search()
