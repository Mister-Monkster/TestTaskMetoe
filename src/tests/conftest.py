import pytest_asyncio
from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock

from starlette.staticfiles import StaticFiles


from app.api.routers.weather_router import router as weather_router
from app.api.routers.api_router import router as api_router


from app.dependencies.service_deps import get_weather_service


from app.services.weather_service import WeatherService


@pytest_asyncio.fixture(scope="module")
def configured_app() -> FastAPI:
    test_app = FastAPI()

    test_app.include_router(weather_router)
    test_app.include_router(api_router)
    test_app.mount("/static", StaticFiles(directory="static"), name="static")


    return test_app


@pytest_asyncio.fixture(scope="module")
async def client(configured_app: FastAPI):

    base_url = "http://test"
    async with AsyncClient(transport=ASGITransport(app=configured_app), base_url=base_url) as ac:
        yield ac


@pytest_asyncio.fixture(scope="function")
def mock_weather_service(mocker) -> AsyncMock:
    mock_service = AsyncMock(spec=WeatherService)

    mock_service.get_city_name_nominatim.return_value = "Mocked City"
    mock_service.get_weather.return_value = {
        "temperature": 20,
        "description": "Ясно",
        "emoji": "☀️",
        "date": "2024-05-27",
        "time": "10:00",
        "interval": "15"
    }
    mock_service.save_to_history.return_value = True
    mock_service.get_history.return_value = [
        {"city": "Москва", "count": 5},
        {"city": "Лондон", "count": 3}
    ]

    return mock_service


@pytest_asyncio.fixture(autouse=True, scope="function")
def override_dependencies(configured_app: FastAPI, mock_weather_service: AsyncMock):
    configured_app.dependency_overrides[get_weather_service] = lambda: mock_weather_service
    yield
    configured_app.dependency_overrides = {}

