from pydantic import BaseModel, ConfigDict


class VacancyTG(BaseModel):
    name_vacancy: str
    name_company: str
    link: str

    model_config = ConfigDict(
        from_attributes=True,
        str_strip_whitespace=True,
    )
