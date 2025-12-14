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
    _logger.info("Checking write performance for %d operations..." % n)
    collected = []
    with catch_time() as t:
        for i in range(n):
            with catch_time() as t_2:
                properties = client.get_database(database)
                boston = properties.get_collection(
                    collection,
                    write_concern=pymongo.WriteConcern(w="majority", j=True),
                )
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
                boston.insert_one(record)
                collected.append(t_2())
        _logger.info("Finished checking write performance...")

    curr_throughput = n / t()
    _logger.info("Write performance: %d operations per second..." % curr_throughput)

    return curr_throughput, collected
