import logging
import random

import pymongo

from src.utils.catch_time import catch_time

_logger = logging.getLogger(__name__)

NUMBER_COMPARISON_OPERATORS = [
    "$eq", "$gt", "$gte", "$lt", "$lte", "$ne",
]

def throughput(n: int, client: pymongo.MongoClient, database: str, collection: str,) -> tuple[float, list[float]]:
    _logger.debug("Checking throughput for %d operations..." % n)
    database_results = []

    with catch_time() as t_1:
        for i in range(n):
            with catch_time() as t_2:
                properties = client.get_database(database)
                boston = properties.get_collection(collection)
                query = {"LSTAT": {random.choice(NUMBER_COMPARISON_OPERATORS): "20"}}
                boston.find_one(query)
            database_results.append(t_2())
        _logger.debug("Finished checking throughput...")

    curr_throughput = n / t_1()
    _logger.debug("Throughput: %d operations per second..." % curr_throughput)

    return curr_throughput, database_results
