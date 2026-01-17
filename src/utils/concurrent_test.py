"""
Moduł do równoległego testowania wydajności MongoDB z wieloma klientami.

Wykorzystuje multiprocessing do symulacji wielu niezależnych klientów
łączących się z bazą danych jednocześnie. Każdy proces ma własne
połączenie z MongoDB, co realistycznie symuluje obciążenie produkcyjne.
"""

import logging
from multiprocessing import Pool
from typing import Callable, Mapping, Any
import pymongo
from pymongo import MongoClient

_logger = logging.getLogger(__name__)


def _worker_task(args: tuple) -> dict:
    """
    Zadanie wykonywane przez pojedynczego workera (klienta).

    Args:
        args: Tuple zawierający (worker_id, mongo_uri, task_func, task_kwargs)

    Returns:
        Dict z wynikami: worker_id, results, error (jeśli wystąpił)
    """
    worker_id, mongo_uri, task_func, task_kwargs = args

    try:
        # Każdy worker tworzy własne połączenie
        client: MongoClient[Mapping[str, Any] | Any] = pymongo.MongoClient(mongo_uri)

        # Wykonaj zadanie testowe
        result = task_func(client=client, **task_kwargs)

        client.close()

        return {"worker_id": worker_id, "results": result, "error": None}
    except Exception as e:
        return {"worker_id": worker_id, "results": None, "error": str(e)}


def run_concurrent_test(
    num_clients: int,
    mongo_uri: str,
    task_func: Callable,
    task_kwargs: dict,
) -> list[dict]:
    """
    Uruchamia test wydajnościowy z wieloma równoległymi klientami.

    Każdy klient działa w osobnym procesie z własnym połączeniem
    do MongoDB, co realistycznie symuluje obciążenie wieloma użytkownikami.

    Args:
        num_clients: Liczba równoległych klientów (1, 3, 5).
        mongo_uri: Connection string do MongoDB.
        task_func: Funkcja testowa do wykonania (np. latency, throughput).
                   Musi przyjmować argument 'client' jako pymongo.MongoClient.
        task_kwargs: Dodatkowe argumenty do przekazania funkcji testowej.

    Returns:
        Lista wyników od każdego klienta. Każdy wynik to dict:
        - worker_id: ID klienta (0, 1, 2, ...)
        - results: Wyniki zwrócone przez task_func
        - error: Komunikat błędu lub None

    Example:
        >>> results = run_concurrent_test(
        ...     num_clients=3,
        ...     mongo_uri=os.environ["MONGO_URI"],
        ...     task_func=latency,
        ...     task_kwargs={"n": 100, "database": "test_concurrent.ipynb", "collection": "boston"}
        ... )
        >>> for r in results:
        ...     print(f"Klient {r['worker_id']}: {r['results']}")
    """
    _logger.info(f"Uruchamianie testu z {num_clients} równoległymi klientami...")

    # Przygotuj argumenty dla każdego workera
    worker_args = [(i, mongo_uri, task_func, task_kwargs) for i in range(num_clients)]

    # Uruchom workery w puli procesów
    with Pool(processes=num_clients) as pool:
        results = pool.map(_worker_task, worker_args)

    # Sprawdź błędy
    errors = [r for r in results if r["error"] is not None]
    if errors:
        for e in errors:
            _logger.error(f"Worker {e['worker_id']} failed: {e['error']}")

    _logger.info(f"Test zakończony. Sukces: {len(results) - len(errors)}/{num_clients}")

    return results


def aggregate_latency_results(results: list[dict]) -> dict:
    """
    Agreguje wyniki testów latency od wielu klientów.

    Args:
        results: Lista wyników z run_concurrent_test (task_func=latency)

    Returns:
        Dict z zagregowanymi metrykami:
        - avg_latency_ms: Średnia latency ze wszystkich klientów
        - all_runs: Lista wszystkich pomiarów (połączona)
        - per_client: Wyniki per klient
    """
    all_runs = []
    per_client = {}
    total_latency = 0
    valid_clients = 0

    for r in results:
        if r["error"] is None and r["results"] is not None:
            latency_ms, runs = r["results"]
            per_client[r["worker_id"]] = {"avg_latency_ms": latency_ms, "runs": runs}
            all_runs.extend(runs)
            total_latency += latency_ms
            valid_clients += 1

    return {
        "avg_latency_ms": total_latency / valid_clients if valid_clients > 0 else 0,
        "all_runs": all_runs,
        "per_client": per_client,
        "num_clients": valid_clients,
    }


def aggregate_throughput_results(results: list[dict]) -> dict:
    """
    Agreguje wyniki testów throughput od wielu klientów.

    Args:
        results: Lista wyników z run_concurrent_test (task_func=throughput)

    Returns:
        Dict z zagregowanymi metrykami:
        - total_throughput: Łączna przepustowość (suma wszystkich klientów)
        - avg_throughput_per_client: Średnia przepustowość per klient
        - all_runs: Lista wszystkich pomiarów czasów operacji
        - per_client: Wyniki per klient
    """
    all_runs = []
    per_client = {}
    total_throughput = 0
    valid_clients = 0

    for r in results:
        if r["error"] is None and r["results"] is not None:
            throughput, runs = r["results"]
            per_client[r["worker_id"]] = {"throughput": throughput, "runs": runs}
            all_runs.extend(runs)
            total_throughput += throughput
            valid_clients += 1

    return {
        "total_throughput": total_throughput,
        "avg_throughput_per_client": total_throughput / valid_clients
        if valid_clients > 0
        else 0,
        "all_runs": all_runs,
        "per_client": per_client,
        "num_clients": valid_clients,
    }


def aggregate_write_results(results: list[dict]) -> dict:
    """
    Agreguje wyniki testów write_performance od wielu klientów.

    Args:
        results: Lista wyników z run_concurrent_test (task_func=write_performance)

    Returns:
        Dict z zagregowanymi metrykami:
        - total_write_throughput: Łączna przepustowość zapisu
        - avg_write_throughput_per_client: Średnia przepustowość per klient
        - all_runs: Lista wszystkich pomiarów czasów zapisu
        - per_client: Wyniki per klient
    """
    all_runs = []
    per_client = {}
    total_throughput = 0
    valid_clients = 0

    for r in results:
        if r["error"] is None and r["results"] is not None:
            throughput, runs = r["results"]
            per_client[r["worker_id"]] = {"write_throughput": throughput, "runs": runs}
            all_runs.extend(runs)
            total_throughput += throughput
            valid_clients += 1

    return {
        "total_write_throughput": total_throughput,
        "avg_write_throughput_per_client": total_throughput / valid_clients
        if valid_clients > 0
        else 0,
        "all_runs": all_runs,
        "per_client": per_client,
        "num_clients": valid_clients,
    }
