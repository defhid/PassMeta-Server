from typing import Generic, TypeVar, Iterator, Optional, Dict, Callable, Type, Union, Any
from collections import OrderedDict

__all__ = (
    'Enum',
    'LRUCache',
    'Locale',
)

KT = TypeVar('KT')
VT = TypeVar('VT')
IdT = TypeVar('IdT')
EnumT = TypeVar('EnumT')


class Enum(Generic[VT, IdT]):
    """ Abstract enum class.
        Before using an instance, you need to call base method _init().
    """

    __items: Dict[IdT, VT]
    __item_names: Dict[VT, str] = dict()
    __type: Type

    @classmethod
    def _init(cls, instance: EnumT, value_type: Type, id_getter: Callable[[VT], IdT]) -> EnumT:
        instance.__type = value_type
        instance.__items = dict()
        instance.__item_names = dict()
        for attr_name, item in cls.__dict__.items():
            if type(item) is value_type and not attr_name.startswith('_'):
                instance.__items[id_getter(item)] = item
                instance.__item_names[item] = attr_name
        return instance

    def contains(self, item: VT):
        return item in self.__item_names

    def contains_id(self, item_id: Union[VT, IdT]):
        return item_id in self.__items

    def contains_name(self, item_name: str):
        return item_name in self.__item_names.values()

    def items(self) -> Iterator[VT]:
        return iter(self.__items.values())

    def item_ids(self) -> Iterator[IdT]:
        return iter(self.__items.keys())

    def item_names(self) -> Iterator[str]:
        return iter(self.__item_names.values())

    def get(self, predicate: Callable[[VT], bool], default=None) -> Union[VT, Any]:
        for item in self.__item_names.keys():
            if predicate(item):
                return item

        return default

    def get_by_id(self, item_id: IdT, default=None) -> Union[VT, Any]:
        return self.__items.get(item_id, default)

    def get_by_name(self, item_name: str, default=None) -> Union[VT, Any]:
        for item, name in self.__item_names:
            if name == item_name:
                return item
        return default

    def name_of(self, item_or_id: Union[VT, IdT]) -> Optional[str]:
        if type(item_or_id) is not self.__type:
            item_or_id = self.__items.get(item_or_id)
        return self.__item_names.get(item_or_id)


class LRUCache(Generic[KT, VT]):
    __slots__ = ('_cache', '_capacity')

    def __init__(self, capacity: int):
        self._cache = OrderedDict()
        self._capacity = capacity

    def get(self, key: KT, default=None) -> Union[VT, Any]:
        if key not in self._cache:
            return default
        else:
            self._cache.move_to_end(key)
            return self._cache[key]

    def put(self, key: KT, value: VT):
        self._cache[key] = value
        self._cache.move_to_end(key)
        if len(self._cache) > self._capacity:
            self._cache.popitem(last=False)

    def pop(self, key: KT, default=None) -> Union[VT, Any]:
        return self._cache.pop(key, default)


class Locale:
    __slots__ = ('_code', )

    def __init__(self, code: str):
        self._code = code

    @property
    def code(self):
        return self._code
