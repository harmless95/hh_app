import logging


def setup_logger(log_level, log_file, log_format):
    """Метод для настройки логгера на основе конфига"""
    my_logger = logging.getLogger("MainLogger")
    if not my_logger.handlers:
        my_logger.setLevel(log_level)

        # Создаем родительские папки, если их нет
        log_file.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file, encoding="utf-8")

        formater = logging.Formatter(
            fmt=log_format,
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(formater)

        my_logger.addHandler(file_handler)
    return my_logger
