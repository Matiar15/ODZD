"""
Moduł do pomiaru wydajności operacji zapisu do MongoDB.

Write performance mierzy ile operacji insert_one() można wykonać
na sekundę. Używa write concern z potwierdzeniem większości
replik (w="majority") i journaling (j=True) dla bezpieczeństwa danych.

UWAGA: Ta operacja modyfikuje dane w kolekcji! Użyj CollectionStateManager
z modułu db_reset do przywrócenia stanu kolekcji po testach.
"""

import logging
import pymongo

from src.utils.catch_time import catch_time

_logger = logging.getLogger(__name__)


def write_performance(
    n: int,
    client: pymongo.MongoClient,
    database: str,
    collection: str,
) -> tuple[float, list[float]]:
    """
    Mierzy wydajność operacji zapisu (insert_one) do bazy MongoDB.

    Wstawia n dokumentów z przykładowymi danymi i mierzy czas
    każdej operacji oraz całkowitą przepustowość.

    UWAGA: Funkcja dodaje dokumenty do kolekcji! Aby zachować
    bezstanowość testów, użyj CollectionStateManager:

        from src.utils.db_reset import CollectionStateManager

        with CollectionStateManager(client, database, collection):
            write_performance(n, client, database, collection)

    Args:
        n: Liczba dokumentów do wstawienia.
        client: Połączenie z bazą MongoDB.
        database: Nazwa bazy danych.
        collection: Nazwa kolekcji.

    Returns:
        Tuple zawierający:
        - Przepustowość (operacje zapisu na sekundę)
        - Lista czasów każdej operacji zapisu (w sekundach)
    """
    _logger.info("Checking write performance for %d operations..." % n)
    collected = []

    # Pobieramy referencje do bazy i kolekcji przed pętlą
    # aby nie mierzyć czasu ich tworzenia w każdej iteracji
    db = client.get_database(database)
    coll = db.get_collection(
        collection,
        write_concern=pymongo.WriteConcern(w="majority", j=True),
    )

    # Przykładowy rekord do wstawienia
    record = {
        "CRIM": 0.02,
        "ZN": 18.0,
        "INDUS": 2.31,
        "CHAS": 0.0,
        "NOX": 0.538,
        "RM": 6.575,
        "AGE": 65.2,
        "DIS": 4.09,
        "RAD": 1.0,
        "TAX": 296.0,
        "PTRATIO": 15.3,
        "MEDV": 346.24,
        "B": 396.9,
        "LSTAT": 4.98,
    }

    with catch_time() as t:
        for i in range(n):
            with catch_time() as t_2:
                coll.insert_one(
                    record.copy()
                )  # .copy() aby każdy insert miał nowy dokument
            collected.append(t_2())
    _logger.info("Finished checking write performance...")

    curr_throughput = n / t()
    _logger.info("Write performance: %d operations per second..." % curr_throughput)

    return curr_throughput, collected
