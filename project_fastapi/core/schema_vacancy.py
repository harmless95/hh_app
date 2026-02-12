from pydantic import BaseModel, ConfigDict


class Vacancy(BaseModel):
    text: str
    work_format: str
    items_on_page: int
    experience: str

    model_config = ConfigDict(from_attributes=True)
