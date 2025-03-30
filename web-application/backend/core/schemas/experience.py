from datetime import date
from pydantic import BaseModel


class Experience(BaseModel):
    start_date: date | None
    end_date: date | None
    title: str
    company: str
    emp_type: str | None
