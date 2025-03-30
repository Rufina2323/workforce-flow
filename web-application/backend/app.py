from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.employee_service import EmployeeService

app = FastAPI()

employee_service = EmployeeService()

origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get(
        "/employees/{year}",
)
def get_employees(year: int):
    return employee_service.get_statictics_for_year(year)
