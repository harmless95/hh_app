from typing import Union
from uuid import uuid4
from datetime import datetime, UTC
from pydantic import BaseModel, ConfigDict, Field, field_validator


class ChatInfo(BaseModel):
    id: int
    model_config = ConfigDict(extra="ignore")


class DataTG(BaseModel):
    chat: ChatInfo
    text: list
    user_id: str
    request_id: str = Field(default_factory=lambda: str(uuid4()))
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    @field_validator("user_id", mode="before")
    @classmethod
    def convert_user_id_to_str(cls, value: Union[str, int, None]) -> str:
        """Автоматически преобразует user_id из int в str"""
        if value is None:
            return ""
        if isinstance(value, int):
            return str(value)
        return str(value)

    @field_validator("request_id", mode="before")
    @classmethod
    def convert_request_id_to_str(cls, value: Union[str, int, None]) -> str:
        """Автоматически преобразует request_id из int в str"""
        if value is None:
            return str(uuid4())
        if isinstance(value, int):
            return str(value)
        return str(value)
