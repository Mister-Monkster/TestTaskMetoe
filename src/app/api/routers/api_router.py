from fastapi import APIRouter

from app.dependencies.service_deps import ServiceDep
from app.models.models import HistoryResponse

router = APIRouter(prefix='/api')


@router.get('/stats')
async def get_stats(service: ServiceDep) -> list[HistoryResponse] | dict:
    res = await service.get_history()
    if res:
        return res
    return {"ok": True, 'message': "History is empty"}