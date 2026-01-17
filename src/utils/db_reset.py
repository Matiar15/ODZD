"""
Moduł odpowiedzialny za resetowanie stanu bazy danych do stanu początkowego.

Zapewnia powtarzalność testów wydajnościowych poprzez przywrócenie kolekcji
do znanej liczby dokumentów przed każdym testem.
"""

import logging
import pymongo

_logger = logging.getLogger(__name__)


def get_collection_count(
    client: pymongo.MongoClient,
    database: str,
    collection: str,
) -> int:
    """
    Pobiera aktualną liczbę dokumentów w kolekcji.

    Args:
        client: Połączenie z bazą MongoDB.
        database: Nazwa bazy danych.
        collection: Nazwa kolekcji.

    Returns:
        Liczba dokumentów w kolekcji.
    """
    db = client.get_database(database)
    coll = db.get_collection(collection)
    return coll.count_documents({})


def reset_collection_to_count(
    client: pymongo.MongoClient,
    database: str,
    collection: str,
    target_count: int,
) -> int:
    """
    Resetuje kolekcję do określonej liczby dokumentów.

    Usuwa nadmiarowe dokumenty (te dodane podczas testów write),
    zachowując pierwotne rekordy. Dokumenty są usuwane w kolejności
    od najnowszych (LIFO - last in, first out).

    Args:
        client: Połączenie z bazą MongoDB.
        database: Nazwa bazy danych.
        collection: Nazwa kolekcji.
        target_count: Docelowa liczba dokumentów.

    Returns:
        Liczba usuniętych dokumentów.

    Example:
        >>> initial_count = get_collection_count(client, "nieruchomosci", "boston")
        >>> # ... wykonaj testy write ...
        >>> deleted = reset_collection_to_count(client, "nieruchomosci", "boston", initial_count)
        >>> print(f"Usunięto {deleted} testowych dokumentów")
    """
    db = client.get_database(database)
    coll = db.get_collection(collection)

    current_count = coll.count_documents({})
    documents_to_delete = current_count - target_count

    if documents_to_delete <= 0:
        _logger.info(
            f"Kolekcja {database}.{collection} ma {current_count} dokumentów, "
            f"cel: {target_count}. Brak dokumentów do usunięcia."
        )
        return 0

    _logger.info(
        f"Resetowanie kolekcji {database}.{collection}: "
        f"usuwanie {documents_to_delete} dokumentów (z {current_count} do {target_count})..."
    )

    # Pobierz _id dokumentów do usunięcia (najnowsze - sortowanie malejące po _id)
    # ObjectId zawiera timestamp, więc sortowanie po _id daje kolejność chronologiczną
    documents_to_remove = (
        coll.find({}, {"_id": 1})
        .sort("_id", pymongo.DESCENDING)
        .limit(documents_to_delete)
    )

    ids_to_remove = [doc["_id"] for doc in documents_to_remove]

    # Usuń dokumenty
    result = coll.delete_many({"_id": {"$in": ids_to_remove}})

    _logger.info(f"Usunięto {result.deleted_count} dokumentów.")

    return result.deleted_count


class CollectionStateManager:
    """
    Kontekstowy manager stanu kolekcji dla testów wydajnościowych.

    Automatycznie zapisuje liczbę dokumentów przed wejściem do kontekstu
    i przywraca ją po wyjściu. Zapewnia bezstanowość testów.

    Example:
        >>> with CollectionStateManager(client, "nieruchomosci", "boston") as manager:
        ...     # Wykonaj testy write_performance
        ...     write_performance(1000, client, "nieruchomosci", "boston")
        >>> # Kolekcja automatycznie przywrócona do stanu początkowego
    """

    def __init__(
        self,
        client: pymongo.MongoClient,
        database: str,
        collection: str,
    ):
        """
        Inicjalizuje manager stanu kolekcji.

        Args:
            client: Połączenie z bazą MongoDB.
            database: Nazwa bazy danych.
            collection: Nazwa kolekcji.
        """
        self.client = client
        self.database = database
        self.collection = collection
        self.initial_count = 0

    def __enter__(self):
        """Zapisuje początkową liczbę dokumentów przy wejściu do kontekstu."""
        self.initial_count = get_collection_count(
            self.client, self.database, self.collection
        )
        _logger.info(
            f"Zapisano początkowy stan kolekcji {self.database}.{self.collection}: "
            f"{self.initial_count} dokumentów"
        )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Przywraca kolekcję do stanu początkowego przy wyjściu z kontekstu."""
        deleted = reset_collection_to_count(
            self.client, self.database, self.collection, self.initial_count
        )
        if deleted > 0:
            _logger.info(
                f"Przywrócono stan kolekcji {self.database}.{self.collection}: "
                f"usunięto {deleted} testowych dokumentów"
            )
        return False  # Nie przechwytuj wyjątków
