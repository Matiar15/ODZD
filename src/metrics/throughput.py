"""
Moduł do pomiaru przepustowości (throughput) operacji odczytu z MongoDB.

Throughput to liczba operacji, które baza danych może obsłużyć
w jednostce czasu (operacje/sekundę). Kluczowa metryka wydajności.
"""

import logging
import random

import pymongo

from src.utils.catch_time import catch_time

_logger = logging.getLogger(__name__)

# Operatory porównania numerycznego używane do generowania losowych zapytań
NUMBER_COMPARISON_OPERATORS = [
    "$eq",  # równe
    "$gt",  # większe niż
    "$gte",  # większe lub równe
    "$lt",  # mniejsze niż
    "$lte",  # mniejsze lub równe
    "$ne",  # różne od
]


def throughput(
    n: int,
    client: pymongo.MongoClient,
    database: str,
    collection: str,
) -> tuple[float, list[float]]:
    """
    Mierzy przepustowość operacji find_one() do bazy MongoDB.

    Wykonuje n zapytań find_one() z losowym operatorem porównania
    i oblicza ile operacji można wykonać na sekundę.

    Args:
        n: Liczba operacji do wykonania.
        client: Połączenie z bazą MongoDB.
        database: Nazwa bazy danych.
        collection: Nazwa kolekcji.

    Returns:
        Tuple zawierający:
        - Przepustowość (operacje na sekundę)
        - Lista czasów każdej operacji (w sekundach)
    """
    _logger.debug("Checking throughput for %d operations..." % n)
    database_results = []

    # Pobieramy referencje do bazy i kolekcji przed pętlą
    # aby nie mierzyć czasu ich tworzenia w każdej iteracji
    db = client.get_database(database)
    coll = db.get_collection(collection)

    with catch_time() as t_1:
        for i in range(n):
            with catch_time() as t_2:
                # Losowy operator porównania dla różnorodności zapytań
                query = {
                    "LSTAT": {random.choice(NUMBER_COMPARISON_OPERATORS): 20}
                }  # liczba, nie string
                coll.find_one(query)
            database_results.append(t_2())
        _logger.debug("Finished checking throughput...")

    curr_throughput = n / t_1()
    _logger.debug("Throughput: %d operations per second..." % curr_throughput)

    return curr_throughput, database_results
