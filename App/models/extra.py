from typing import Type, Optional

__all__ = (
    'LogKind',
)


class LogKind:
    __slots__ = ('id', 'name', 'entity_model')

    def __init__(self, kind_id: int, kind_name: str, entity_model: Optional[Type]):
        self.id = kind_id
        self.name = kind_name
        self.entity_model = entity_model
