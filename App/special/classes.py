from typing import Generic, TypeVar, Iterator

__all__ = (
    'Enum',
)

VT = TypeVar('VT')


class Enum(Generic[VT]):
    """ Абстрактный класс перечисления.
        После объявления наследника необходимо вызвать метод init().
    """

    __items: dict[VT, str] = dict()

    @classmethod
    def init(cls):
        for attr_name, item in cls.__class__.__dict__.items():
            if not attr_name.startswith("_"):
                cls.__items[item] = attr_name

    @classmethod
    def contains(cls, item: VT):
        return cls.__items.keys().__contains__(item)

    @classmethod
    def contains_name(cls, name: str):
        return cls.__items.values().__contains__(name)

    @classmethod
    def items(cls) -> Iterator[VT]:
        return cls.__items.keys().__iter__()

    @classmethod
    def item_names(cls) -> Iterator[str]:
        return cls.__items.values().__iter__()

    @classmethod
    def name_of(cls, item: VT) -> str:
        """ Получить название элемента перечисления. """
        return cls.__items[item]
