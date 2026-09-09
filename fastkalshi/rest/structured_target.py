from fastkalshi.constants import api_url

from .pagination import paginate
from .rest import DEFAULT_TIMEOUT, RequestTimeout, drop_none, get


class StructuredTarget:
    def GetStructuredTargets(
        self,
        ids: list[str] | None = None,
        type: str | None = None,
        competition: str | None = None,
        page_size: int = 100,
        cursor: str | None = None,
        *,
        timeout: RequestTimeout = DEFAULT_TIMEOUT,
    ):
        if ids is not None and not ids:
            raise ValueError("ids must not be empty")
        return get(
            api_url("structured_targets"),
            timeout=timeout,
            **drop_none(
                {
                    "ids": ids,
                    "type": type,
                    "competition": competition,
                    "page_size": page_size,
                    "cursor": cursor,
                }
            ),
        )

    def IterStructuredTargets(self, *, max_pages: int | None = None, **params):
        return paginate(
            self.GetStructuredTargets,
            "structured_targets",
            max_pages=max_pages,
            **params,
        )


structured_target = StructuredTarget()
