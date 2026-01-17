"""
Moduł do precyzyjnego pomiaru czasu wykonania operacji.

Wykorzystuje perf_counter() dla wysokiej rozdzielczości pomiaru.
"""

import typing
from time import perf_counter
from contextlib import contextmanager


@contextmanager
def catch_time() -> typing.Generator[typing.Callable[[], float], typing.Any, None]:
    """
    Context manager do pomiaru czasu wykonania bloku kodu.

    Używa time.perf_counter() dla najwyższej dostępnej rozdzielczości
    pomiaru czasu na danej platformie.

    Yields:
        Callable[[], float]: Funkcja zwracająca czas (w sekundach) od rozpoczęcia pomiaru.

    Example:
        >>> with catch_time() as elapsed:
        ...     # operacja do zmierzenia
        ...     time.sleep(1)
        >>> print(f"Czas wykonania: {elapsed():.4f}s")
        Czas wykonania: 1.0012s
    """
    start = perf_counter()
    yield lambda: perf_counter() - start
