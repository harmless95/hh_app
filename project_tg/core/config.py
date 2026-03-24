from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel

from .log_settings import setup_logger

# fmt: off
LOG_DEFAULT_FORMAT = "[%(asctime)s.%(msecs)03d] %(module)10s:%(lineno)-3d %(levelname)-7s - %(message)s"
# fmt: on
BASE_DIR = Path(__file__).resolve().parent.parent


class PingAPP(BaseModel):
    url: str


class ApplicationDB(BaseModel):
    url: str


class ConfigTG(BaseModel):
    token: str
    port: str


class Redis(BaseModel):
    url: str
    channel: str


class LoggingConfig(BaseModel):
    log_level: Literal[
        "DEBUG",
        "INFO",
        "WARNING",
        "ERROR",
        "CRITICAL",
    ] = "WARNING"
    log_format: str = LOG_DEFAULT_FORMAT
    log_file: str = BASE_DIR / "data_logs/error_tg_logs.log"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(
            BASE_DIR / ".env.template",
            BASE_DIR / ".env",
        ),
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="APP_CONFIG__",
    )
    redis: Redis
    app_db: ApplicationDB
    config_tg: ConfigTG
    ping_app_tg: PingAPP
    my_logger: LoggingConfig = LoggingConfig()


setting = Settings()
logger = setup_logger(
    log_level=setting.my_logger.log_level,
    log_file=setting.my_logger.log_file,
    log_format=setting.my_logger.log_format,
)
