from functools import wraps
from cachetools import TTLCache

cache = TTLCache(maxsize=100, ttl=300)

def cache_response(ttl=300):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            key = f"{f.__name__}:{str(args)}:{str(kwargs)}"
            if key in cache:
                return cache[key]
            result = f(*args, **kwargs)
            cache[key] = result
            return result
        return decorated
    return decorator