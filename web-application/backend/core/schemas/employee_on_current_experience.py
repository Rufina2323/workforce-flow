
from pydantic import BaseModel


class EmployeeOnCurrentExperience(BaseModel):
    id: str
    name: str
    location: str
    estimated_age: float | None
    company: str
    start_year: int | None
    end_year: int | None
