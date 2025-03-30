from core import dependencies
from core.schemas.employee import Employee
from core.repository.repository import Repository
from core.schemas.employee_on_current_experience import \
    EmployeeOnCurrentExperience


class EmployeeService:
    def __init__(self) -> None:
        self.repository: Repository = dependencies.repository()

    def get_statictics_for_year(self, year: int) -> (
        dict[str, list[EmployeeOnCurrentExperience]]
    ):
        all_employees: list[Employee] = self.repository.get_employees()

        top_companies: dict[str, list[EmployeeOnCurrentExperience]] = {}

        for employee in all_employees:
            for experience in employee.experiences:
                if experience.start_date is None:
                    continue

                if experience.start_date.year <= year and \
                    (experience.end_date is None or
                     experience.end_date.year >= year):

                    if experience.company not in top_companies:
                        top_companies[experience.company] = []

                    top_companies[experience.company].append(
                        EmployeeOnCurrentExperience(
                            **employee.model_dump(),
                            company=experience.company,
                            start_year=(
                                experience.start_date.year
                                if experience.start_date else None
                            ),
                            end_year=(
                                experience.end_date.year
                                if experience.end_date else None
                            ),
                        )
                    )

        top_10_companies_raw: list[
            tuple[str, list[EmployeeOnCurrentExperience]]
        ] = \
            sorted(
                top_companies.items(),
                key=lambda x: len(x[1]),
                reverse=True)[:10]

        top_10_companies: dict[str, list[EmployeeOnCurrentExperience]] = {}

        for company, employees in top_10_companies_raw:
            top_10_companies[company] = employees

        return top_10_companies
