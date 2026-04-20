import logging
from datetime import datetime
import json


class ClickHouseHandler(logging.Handler):
    """Handler для отправки логов в ClickHouse с async_insert"""

    def __init__(
        self,
        host="clickhouse_log",
        port=8123,
        username="userlog",
        password="passwordlog",
        database="logs_db",
    ):
        super().__init__()

        self.ch_available = False
        self.client = None
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.database = database

        # Пытаемся подключиться
        self._connect()

    def _connect(self):
        """Подключение к ClickHouse с обработкой ошибок"""
        try:
            from clickhouse_connect import get_client

            self.client = get_client(
                host=self.host,
                port=self.port,
                username=self.username,
                password=self.password,
                database=self.database,
            )

            # Включаем асинхронную вставку
            self.client.command("SET async_insert = 1")
            self.client.command("SET wait_for_async_insert = 0")

            # Создаём таблицу
            self._ensure_table_exists()

            self.ch_available = True
            print(f"ClickHouse подключён: {self.host}:{self.port}/{self.database}")

        except Exception as e:
            self.ch_available = False
            print(f"НЕ УДАЛОСЬ подключиться к ClickHouse: {type(e).__name__}: {e}")
            print(f"   Проверьте: доступен ли ClickHouse на {self.host}:{self.port}")

    def _ensure_table_exists(self):
        """Создаёт таблицу для логов, если её нет"""
        create_table_query = """
        CREATE TABLE IF NOT EXISTS app_logs (
            timestamp DateTime,
            level String,
            logger String,
            module String,
            function String,
            line UInt32,
            message String,
            exception String DEFAULT '',
            user_id String DEFAULT '',
            request_id String DEFAULT '',
            duration_ms UInt32 DEFAULT 0,
            event_date Date DEFAULT toDate(timestamp)
        ) ENGINE = MergeTree()
        PARTITION BY event_date
        ORDER BY (timestamp, level)
        """
        self.client.command(create_table_query)

    def emit(self, record):
        """Отправляет лог в ClickHouse"""
        if not self.ch_available:
            # Если ClickHouse недоступен, просто игнорируем (не спамим ошибками)
            return

        try:
            # Безопасное получение extra полей
            user_id = getattr(record, "user_id", "")
            request_id = getattr(record, "request_id", "")
            duration_ms = getattr(record, "duration_ms", 0)

            log_entry = [
                [
                    datetime.fromtimestamp(record.created),  # timestamp
                    record.levelname,  # level
                    record.name,  # logger
                    record.module,  # module
                    record.funcName,  # function
                    record.lineno,  # line
                    self.format(record),  # message
                    (
                        self._format_exception(record.exc_info)
                        if record.exc_info
                        else ""
                    ),
                    user_id,
                    request_id,
                    duration_ms,
                ]
            ]

            self.client.insert(
                table="app_logs",
                data=log_entry,
                column_names=[
                    "timestamp",
                    "level",
                    "logger",
                    "module",
                    "function",
                    "line",
                    "message",
                    "exception",
                    "user_id",
                    "request_id",
                    "duration_ms",
                ],
            )
            if hasattr(self, "_last_error_shown"):
                delattr(self, "_last_error_shown")
        except Exception as e:
            print(f"\nОШИБКА: {type(e).__name__}: {e}")

            if not hasattr(self, "_last_error_shown"):
                import traceback

                traceback.print_exc()
                self._last_error_shown = True

    def _format_exception(self, exc_info):
        import traceback

        return "".join(traceback.format_exception(*exc_info))

    def _format_extra(self, record):
        extra = {}
        for key, value in record.__dict__.items():
            if key not in [
                "name",
                "msg",
                "args",
                "levelname",
                "levelno",
                "pathname",
                "filename",
                "module",
                "exc_info",
                "exc_text",
                "stack_info",
                "lineno",
                "funcName",
                "created",
                "msecs",
                "relativeCreated",
                "thread",
                "threadName",
                "processName",
                "process",
                "message",
            ]:
                extra[key] = str(value)
        return json.dumps(extra, ensure_ascii=False) if extra else ""

    def close(self):
        if self.client and self.ch_available:
            try:
                self.client.command("SYSTEM FLUSH ASYNC INSERT QUEUE")
            except:
                pass
        super().close()
