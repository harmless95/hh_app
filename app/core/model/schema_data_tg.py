from pydantic import BaseModel, ConfigDict


class ChatInfo(BaseModel):
    id: int
    model_config = ConfigDict(extra="ignore")


class DataTG(BaseModel):
    chat: ChatInfo
    text: list
    model_config = ConfigDict(populate_by_name=True, extra="ignore")
