"""
Moduł do pomiaru opóźnienia (latency) zapytań do bazy MongoDB.

Latency to czas odpowiedzi bazy danych na pojedyncze zapytanie,
mierzony od wysłania żądania do otrzymania pełnej odpowiedzi.
"""

import pymongo
import logging

from src.utils.catch_time import catch_time

_logger = logging.getLogger(__name__)


def latency(
    n: int,
    client: pymongo.MongoClient,
    database: str,
    collection: str,
) -> tuple[float, list[float]]:
    """
    Mierzy średnie opóźnienie zapytań find() do bazy MongoDB.

    Wykonuje n zapytań z filtrem na pole 'ptratio' i mierzy czas
    każdego zapytania oraz całkowity czas wykonania wszystkich.

    Args:
        n: Liczba zapytań do wykonania.
        client: Połączenie z bazą MongoDB.
        database: Nazwa bazy danych.
        collection: Nazwa kolekcji.

    Returns:
        Tuple zawierający:
        - Średnie opóźnienie w milisekundach
        - Lista czasów wykonania każdego zapytania (w sekundach)
    """
    _logger.info("Checking latency...")
    runs = []

    # Pobieramy referencje do bazy i kolekcji przed pętlą
    # aby nie mierzyć czasu ich tworzenia w każdej iteracji
    db = client.get_database(database)
    coll = db.get_collection(collection)
    query = {"ptratio": {"$lte": 20}}

    with catch_time() as t_1:
        for i in range(n):
            with catch_time() as t_2:
                # list() wymusza pełne pobranie danych z kursora
                list(coll.find(query))
            runs.append(t_2())

    latency_ms = t_1() * 1000 / n
    _logger.info("Time to fully execute find() %s times: %d ms" % (n, latency_ms))

    return latency_ms, runs
