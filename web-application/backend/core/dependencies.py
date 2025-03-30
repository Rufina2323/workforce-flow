from core.repository.impl.json.json_repository import JSONRepository
from core.repository.repository import Repository


def repository() -> Repository:
    return JSONRepository()
