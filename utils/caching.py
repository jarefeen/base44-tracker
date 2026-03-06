import functools
import hashlib
import json
import diskcache
from config.settings import Settings

_cache = diskcache.Cache(Settings.CACHE_DIR)


def cached(ttl_seconds: int):
    """Disk-cache decorator with TTL. Cache key is derived from function name + args."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            raw_key = json.dumps(
                {"fn": func.__qualname__, "args": str(args), "kwargs": str(sorted(kwargs.items()))},
                sort_keys=True,
            )
            key = hashlib.sha256(raw_key.encode()).hexdigest()
            result = _cache.get(key)
            if result is not None:
                return result
            result = func(*args, **kwargs)
            _cache.set(key, result, expire=ttl_seconds)
            return result
        wrapper.cache_clear = lambda: _cache.clear()
        return wrapper
    return decorator


def clear_all_cache():
    _cache.clear()
