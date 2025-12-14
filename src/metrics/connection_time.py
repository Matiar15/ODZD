import logging

import pymongo

from src.utils.catch_time import catch_time

_logger = logging.getLogger(__name__)


def connection_time(
    n: int,
    client: pymongo.MongoClient,
) -> tuple[float, list[float]]:
    client.close()
    collected = []

    with catch_time() as t_1:
        for i in range(n):
            with catch_time() as t_2:
                client._connect()
                client.close()
                collected.append(t_2())

    return n / t_1(), collected
