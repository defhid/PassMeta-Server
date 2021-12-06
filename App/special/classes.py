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


class Enum(Generic[VT, IdT]):
    """ Abstract enum class.
        Before using, you need to call base method _init().
    """

    __items: Dict[IdT, VT] = dict()
    __item_names: Dict[VT, str] = dict()
    __type: Type

    @classmethod
    def _init(cls, value_type: Type, id_getter: Callable[[VT], IdT]):
        cls.__type = value_type
        for attr_name, item in cls.__dict__.items():
            if type(item) is value_type and not attr_name.startswith('_'):
                cls.__items[id_getter(item)] = item
                cls.__item_names[item] = attr_name

    @classmethod
    def contains(cls, item: VT):
        return item in cls.__item_names

    @classmethod
    def contains_id(cls, item_id: Union[VT, IdT]):
        return item_id in cls.__items

    @classmethod
    def contains_name(cls, item_name: str):
        return item_name in cls.__item_names.values()

    @classmethod
    def items(cls) -> Iterator[VT]:
        return iter(cls.__items.values())

    @classmethod
    def item_ids(cls) -> Iterator[IdT]:
        return iter(cls.__items.keys())

    @classmethod
    def item_names(cls) -> Iterator[str]:
        return iter(cls.__item_names.values())

    @classmethod
    def get(cls, predicate: Callable[[VT], bool], default=None) -> Union[VT, Any]:
        for item in cls.__item_names.keys():
            if predicate(item):
                return item

        return default

    @classmethod
    def get_by_id(cls, item_id: IdT, default=None) -> Union[VT, Any]:
        return cls.__items.get(item_id, default)

    @classmethod
    def get_by_name(cls, item_name: str, default=None) -> Union[VT, Any]:
        for item, name in cls.__item_names:
            if name == item_name:
                return item
        return default

    @classmethod
    def name_of(cls, item_or_id: Union[VT, IdT]) -> Optional[str]:
        if type(item_or_id) is not cls.__type:
            item_or_id = cls.__items.get(item_or_id)
        return cls.__item_names.get(item_or_id)


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
