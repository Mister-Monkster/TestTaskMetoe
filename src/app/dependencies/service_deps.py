from fastapi.params import Depends
from typing import Annotated

from app.dependencies.redis_dep import RedisDep
from app.dependencies.repositories_deps import RepositoryDep
from app.services.weather_service import WeatherService


async def get_weather_service(repository: RepositoryDep, redis: RedisDep):
    return WeatherService(repository, redis)

ServiceDep = Annotated[WeatherService, Depends(get_weather_service)]