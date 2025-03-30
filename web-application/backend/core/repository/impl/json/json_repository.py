import json
from pathlib import Path

from core.schemas.employee import Employee
from core.repository.repository import Repository


class JSONRepository(Repository):
    def __init__(self) -> None:
        super().__init__()
        self.path_to_data = Path("core/repository/impl/json/users.json")

    def _read_raw_data(self) -> list:
        with open(self.path_to_data) as json_file:
            employees_raw: list = json.load(json_file)
        return employees_raw

    def get_employees(self) -> list[Employee]:
        employees_raw: list = self._read_raw_data()

        return list(map(
            lambda raw_employee: Employee(
                **raw_employee
            ),
            employees_raw
        ))
