from fastapi import Depends
from typing import Annotated

from app.db.reository import Repository
from app.dependencies.session_deps import SessionDep


async def get_repository(session: SessionDep) -> Repository:
    return Repository(session)

RepositoryDep = Annotated[Repository, Depends(get_repository)]