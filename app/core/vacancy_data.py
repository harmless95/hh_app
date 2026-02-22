from datetime import datetime, timezone

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import BIGINT, String, Text, TIMESTAMP
from sqlalchemy.dialects.postgresql import ARRAY

from core.base import Base


class VacancyData(Base):
    __tablename__ = "vacancy_data"

    id: Mapped[int] = mapped_column(primary_key=True)
    id_vacancy: Mapped[int] = mapped_column(BIGINT, unique=True, index=True)
    name_vacancy: Mapped[str] = mapped_column(String(255), nullable=False)
    name_company: Mapped[str] = mapped_column(String(255), nullable=True)
    link: Mapped[str] = mapped_column(Text, nullable=False)
    skills: Mapped[list[str]] = mapped_column(ARRAY(String))
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
