import asyncio
from functools import wraps


def repeat(*, seconds: float):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            async def loop(*args, **kwargs):
                while True:
                    try:
                        await func(*args, **kwargs)
                    except Exception as e:
                        print(f"Error: {e}")
                    await asyncio.sleep(seconds)
            asyncio.ensure_future(loop(*args, **kwargs))
        return wrapper
    return decorator


# Compare this snippet from .venv/Lib/site-packages/fastapi_utilities/repeat/repeat_every.py:
# slimmed down version of the repeat_every decorator
