from pydantic import BaseModel, ConfigDict


class ChatInfo(BaseModel):
    id: int


class DataTG(BaseModel):
    chat: ChatInfo
    text: str
    model_config = ConfigDict(from_attributes=True)
