from typing import List, Dict, Any

__all__ = (
    'PageFactory',
)


class PageFactory:
    @staticmethod
    def create(lst: List, total: int, offset: int, limit: int) -> Dict[str, Any]:
        return dict(
            list=lst,
            total=total,
            offset=offset,
            limit=limit
        )
