from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import MetaData

from core.config import setting


class Base(DeclarativeBase):
    __abstract__ = True

    metadata = MetaData(naming_convention=setting.db.naming_convention)
