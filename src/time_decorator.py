from datetime import datetime


class Timer:
    def __call__(self, func, *args, **kwargs):
        def wrapper(*a, **kw):
            start = datetime.now()
            result = func(*a, **kw)
            end = datetime.now()
            print(func.__name__, a, kw, end - start)
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
