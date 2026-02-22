from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class Vacancy(BaseModel):
    id_vacancy: int
    name_vacancy: str
    name_company: Optional[str] = "Название компании не указано"
    link: str
    skills: List[str] = Field(default=list)

    model_config = ConfigDict(
        from_attributes=True,
        str_strip_whitespace=True,
    )
