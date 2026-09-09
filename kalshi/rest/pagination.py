from collections.abc import Callable, Iterator
from typing import Any


class KalshiPaginationError(RuntimeError):
    pass


def paginate(
    fetch_page: Callable[..., Any],
    item_key: str,
    *,
    max_pages: int | None = None,
    cursor: str | None = None,
    **params: Any,
) -> Iterator[dict]:
    if max_pages is not None and max_pages < 1:
        raise ValueError("max_pages must be at least 1")

    seen_cursors = {cursor} if cursor else set()
    page_count = 0
    while True:
        page = fetch_page(cursor=cursor, **params)
        if not isinstance(page, dict) or not isinstance(page.get(item_key), list):
            raise KalshiPaginationError(
                f"Kalshi response did not contain a {item_key} list"
            )
        yield from page[item_key]
        page_count += 1
        if max_pages is not None and page_count >= max_pages:
            return

        cursor = page.get("cursor")
        if not cursor:
            return
        if cursor in seen_cursors:
            raise KalshiPaginationError("Kalshi returned a repeated cursor")
        seen_cursors.add(cursor)
