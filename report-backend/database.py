import clickhouse_connect
from functools import lru_cache

@lru_cache()
def get_clickhouse_client():
    return clickhouse_connect.get_client(
        # host="olap_db",
        host="localhost",
        port=8123,
        username="default",
        password="",
        database="bionicpro"
    )