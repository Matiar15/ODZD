import typing
from time import perf_counter
from contextlib import contextmanager

@contextmanager
def catch_time() -> typing.Generator[typing.Callable[[], float], typing.Any, None]:
    start = perf_counter()
    yield lambda: perf_counter() - start
