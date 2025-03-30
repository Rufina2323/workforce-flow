from pydantic import BaseModel

from core.schemas.experience import Experience


class Employee(BaseModel):
    id: str
    name: str
    location: str
    estimated_age: float | None
    experiences: list[Experience]
