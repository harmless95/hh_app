import csv
from datetime import datetime
from clickhouse_connect import get_client
from core.config import setting


def migrate_from_csv(csv_file_path, batch_size=10000):
    """Импорт логов из CSV файла в ClickHouse"""

    client = get_client(host="localhost", port=8123)
    batch = []

    with open(csv_file_path, "r", encoding="utf-8") as f:
        # Предполагаем формат: timestamp,level,logger,module,message
        reader = csv.DictReader(f)

        for row in reader:
            log_entry = {
                "timestamp": datetime.fromisoformat(row["timestamp"]),
                "level": row["level"],
                "logger": row["logger"],
                "module": row.get("module", ""),
                "function": row.get("function", ""),
                "line": int(row.get("line", 0)),
                "message": row["message"],
                "exception": row.get("exception", ""),
                "user_id": row.get("user_id", ""),
                "request_id": row.get("request_id", ""),
                "duration_ms": int(row.get("duration_ms", 0)),
            }
            batch.append(log_entry)

            if len(batch) >= batch_size:
                client.insert("app_logs", batch)
                print(f"Импортировано {len(batch)} записей")
                batch = []

        # Последняя пачка
        if batch:
            client.insert("app_logs", batch)
            print(f"Импортировано {len(batch)} записей (финал)")

    print("Миграция завершена!")


# Запуск
migrate_from_csv(setting.my_logger.log_file)
