from typing import Dict

__all__ = (
    'HistoryKind',
)


class HistoryKind:
    __slots__ = ('id', 'name_loc')

    def __init__(self, kind_id: int, kind_name_loc: Dict[str, str]):
        self.id = kind_id
        self.name_loc = kind_name_loc
