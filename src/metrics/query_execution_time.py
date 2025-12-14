import random

import pymongo
import logging


_logger = logging.getLogger(__name__)

NUMBER_COMPARISON_OPERATORS = [
    "$eq", "$gt", "$gte", "$lt", "$lte", "$ne",
]

def query_execution_time(n: int, client: pymongo.MongoClient, database: str, collection: str,) -> list[float]:
    _logger.info("Checking query execution time...")
    execution_times = []

    for i in range(n):
        properties = client.get_database(database)
        boston = properties.get_collection(collection)
        query = {"LSTAT": {random.choice(NUMBER_COMPARISON_OPERATORS): "20"}}
        result = boston.find(query).explain()
        _logger.info("Query execution time: %d" % result["executionStats"]["executionTimeMillis"])
        execution_times.append(result["executionStats"]["executionTimeMillis"])


    _logger.info("Finished checking query execution time...")
    return execution_times