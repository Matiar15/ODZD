import pymongo
import logging

from src.utils.catch_time import catch_time

_logger = logging.getLogger(__name__)

def latency(n: int, client: pymongo.MongoClient, database: str, collection: str,) -> float:
    _logger.info("Checking latency...")
    runs = []

    with catch_time() as t_1:
        for i in range(n):
            with catch_time() as t_2:
                properties = client.get_database(database)
                boston = properties.get_collection(collection)
                query = {'ptratio': {'$lte': 20}}
                list(boston.find(query))
                runs.append(t_2())

    latency_ms = t_1() * 1000 / n
    _logger.info("Time to fully execute find() %s times: %d ms" % (n, latency_ms))

    return latency_ms, runs