__all__ = (
    'HistoryKind',
)


class HistoryKind:
    __slots__ = ('id', 'name')

    def __init__(self, kind_id: int, kind_name: str):
        self.id = kind_id
        self.name = kind_name
