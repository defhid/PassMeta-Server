from typing import Generic, TypeVar, Union, Any
from collections import OrderedDict

__all__ = (
    'LRUCache',
)

KT = TypeVar('KT')
VT = TypeVar('VT')


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
