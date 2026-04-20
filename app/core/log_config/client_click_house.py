import clickhouse_connect

# Подключение к локальному ClickHouse
client = clickhouse_connect.get_client(
    host="localhost",
    port=8123,  # HTTP порт (или 9000 для нативного)
    username="default",
    password="",
    database="logs_db",
)
