from abc import ABC, abstractmethod

from core.schemas.employee import Employee


class Repository(ABC):
    @abstractmethod
    def get_employees(self) -> list[Employee]:
        pass
