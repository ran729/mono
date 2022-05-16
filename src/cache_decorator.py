import enum
import json
import os
from abc import ABC, abstractmethod
from typing import Any, Optional


class Storage(enum.Enum):
    Memory = 1,
    File = 2


class Cache(ABC):
    @abstractmethod
    def get(self, key: str) -> Any:
        pass

    @abstractmethod
    def set(self, key: str, value: Any) -> None:
        pass


class MemoryCache(Cache):
    cache = {}

    def get(self, key: int) -> Any:
        return self.cache.get(key)

    def set(self, key: int, value: Any) -> None:
        self.cache[key] = value


class FileCache(Cache):
    def get(self, key: int) -> Optional[Any]:
        filename = self._get_file_name(key)
        exists = os.path.exists(filename)

        if not exists:
            return None

        return json.load(open(filename))

    def set(self, key: int, value: Any) -> None:
        filename = self._get_file_name(key)
        f = open(filename, "x")
        json.dump(value, f)

    @staticmethod
    def _get_file_name(key):
        return f'{key}.cache'


cache_types = {
    Storage.Memory: MemoryCache,
    Storage.File: FileCache
}


class Cacher:
    def __init__(self, storage: Storage = Storage.Memory, on_hit_return_value: Optional[Any] = None, key_fn=None):
        self.key_fn = key_fn
        self.on_hit_return_value = on_hit_return_value
        self.cacher = cache_types[storage]()

    def __call__(self, func, *args, **kwargs):
        def wrapper(*a, **kw):
            key = self.key_fn() if self.key_fn else self._make_key(func.__name__, a, kw)
            result = self.cacher.get(key)

            if result:
                return result if self.on_hit_return_value is None else self.on_hit_return_value

            result = func(*a, **kw)
            self.cacher.set(key, result)
            return result

        wrapper.__name__ = func.__name__
        return wrapper

    @staticmethod
    def _make_key(name: str, args, kwargs) -> int:
        key = args
        if kwargs:
            for item in kwargs.items():
                key += item
        return hash((name,) + key)
