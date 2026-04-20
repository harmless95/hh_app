import logging
from pathlib import Path


def setup_logger(
    log_level,
    log_file,
    log_format,
    use_clickhouse,
    ch_host,
    ch_port,
    ch_user,
    ch_password,
    ch_db,
):
    """
    Метод для настройки логгера на основе конфига.

    Аргументы:
        log_level: уровень логирования
        log_file: путь к файлу (используется как fallback или если use_clickhouse=False)
        log_format: формат логов
        use_clickhouse: True - писать в ClickHouse, False - в файл
        ch_host, ch_port, ch_user, ch_password, ch_db: параметры ClickHouse
    """
    my_logger = logging.getLogger("MainLogger")

    # Очищаем старые handlers, если есть (чтобы не дублировать)
    if my_logger.handlers:
        my_logger.handlers.clear()

    my_logger.setLevel(log_level)

    # Создаём formatter (как в вашем старом коде)
    formatter = logging.Formatter(
        fmt=log_format,
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    if use_clickhouse:
        from core.log_config.async_logger import ClickHouseHandler

        # Используем ClickHouse handler
        ch_handler = ClickHouseHandler(
            host=ch_host,
            port=ch_port,
            username=ch_user,
            password=ch_password,
            database=ch_db,
        )
        ch_handler.setFormatter(formatter)
        my_logger.addHandler(ch_handler)

        # Дополнительно: если файл указан, пишем туда тоже (как бэкап)
        if log_file:
            log_file = Path(log_file)
            log_file.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_file, encoding="utf-8")
            file_handler.setFormatter(formatter)
            my_logger.addHandler(file_handler)
            my_logger.info(f"Логирование настроено: ClickHouse + файл {log_file}")
        else:
            my_logger.info("Логирование настроено: только ClickHouse")
    else:
        # Старый способ: только файл
        log_file = Path(log_file)
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(formatter)
        my_logger.addHandler(file_handler)
        my_logger.info(f"Логирование настроено: только файл {log_file}")

    return my_logger
