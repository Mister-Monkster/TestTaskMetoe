import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock


@pytest.mark.asyncio
async def test_main_page_no_recent_city(client: AsyncClient, mock_weather_service: AsyncMock):

    response = await client.get("/", cookies={})
    assert response.status_code == 200

    assert "Нет данных по вашему последнему запросу" in response.text
    mock_weather_service.get_city_name_nominatim.assert_not_called()
    mock_weather_service.get_weather.assert_not_called()


@pytest.mark.asyncio
async def test_main_page_with_recent_city(client: AsyncClient, mock_weather_service: AsyncMock):
    """
    Тест GET / когда есть кука recent_city.
    Проверяем, что отображается информация о погоде, используя мокированные данные.
    """
    cookies = {"recent_city": "Moscow"}
    response = await client.get("/", cookies=cookies)

    assert response.status_code == 200

    assert "Погода в городе Mocked City" in response.text
    assert '20°C' in response.text
    assert "Ясно ☀" in response.text
    mock_weather_service.get_city_name_nominatim.assert_called_once_with("Moscow", lang='ru')
    mock_weather_service.get_weather.assert_called_once_with("Moscow")


@pytest.mark.asyncio
async def test_main_page_with_recent_city_no_weather_data(client: AsyncClient, mock_weather_service: AsyncMock):
    """
    Тест GET / когда есть кука recent_city, но сервис погоды не вернул данные.
    """
    mock_weather_service.get_weather.return_value = None
    cookies = {"recent_city": "InvalidCity"}
    response = await client.get("/", cookies=cookies)

    assert response.status_code == 200
    assert "<h2>Погода в городе Mocked City</h2>" in response.text
    assert "Температура" not in response.text
    assert "Нет данных по вашему последнему запросу" not in response.text

    mock_weather_service.get_city_name_nominatim.assert_called_once_with("InvalidCity", lang='ru')
    mock_weather_service.get_weather.assert_called_once_with("InvalidCity")


@pytest.mark.asyncio
async def test_change_city_new_session(client: AsyncClient, mock_weather_service: AsyncMock):
    form_data = {"city": "Екатеринбург"}
    response = await client.post("/", data=form_data, follow_redirects=False)
    assert response.status_code == 301 # Ожидаем редирект
    assert response.headers["Location"] == "/"
    set_cookie_headers = response.headers.get_list("set-cookie")
    assert any('recent_city="Mocked City"' in cookie for cookie in set_cookie_headers)
    assert any('session_token=' in cookie for cookie in set_cookie_headers)
    mock_weather_service.get_city_name_nominatim.assert_called_once_with("Екатеринбург")
    mock_weather_service.save_to_history.assert_called_once()
    called_with_data = mock_weather_service.save_to_history.call_args.args[0]
    assert called_with_data.city_name == "Екатеринбург"
    assert isinstance(called_with_data.token, str)
    assert len(called_with_data.token) > 0





@pytest.mark.asyncio
async def test_change_city_nominatim_fails(client: AsyncClient, mock_weather_service: AsyncMock):

    mock_weather_service.get_city_name_nominatim.return_value = None
    form_data = {"city": "НесуществующийГород"}
    response = await client.post("/", data=form_data, follow_redirects=False)

    assert response.status_code == 301
    assert response.headers["Location"] == "/"

    set_cookie_headers = response.headers.get_list("set-cookie")
    assert set_cookie_headers == []

    mock_weather_service.get_city_name_nominatim.assert_called_once_with("НесуществующийГород")
    mock_weather_service.save_to_history.assert_not_called()


@pytest.mark.asyncio
async def test_change_city_save_to_history_fails(client: AsyncClient, mock_weather_service: AsyncMock):
    mock_weather_service.save_to_history.return_value = False
    form_data = {"city": "ТестовыйГород"}
    response = await client.post("/", data=form_data, follow_redirects=False)

    assert response.status_code == 500
    assert response.json() == {"detail": "Somthing went's wrong"}

    mock_weather_service.save_to_history.assert_called_once()


@pytest.mark.asyncio
async def test_get_stats_with_history(client: AsyncClient, mock_weather_service: AsyncMock):
    mock_weather_service.get_history.return_value = [
        {"city": "Москва", "count": 5},
        {"city": "Лондон", "count": 3}
    ]
    response = await client.get("/api/stats")

    assert response.status_code == 200
    assert response.json() == [
        {"city": "Москва", "count": 5},
        {"city": "Лондон", "count": 3}
    ]
    mock_weather_service.get_history.assert_called_once()


@pytest.mark.asyncio
async def test_get_stats_empty_history(client: AsyncClient, mock_weather_service: AsyncMock):
    mock_weather_service.get_history.return_value = None # Или []
    response = await client.get("/api/stats")

    assert response.status_code == 200
    assert response.json() == {"ok": True, 'message': "History is empty"}
    mock_weather_service.get_history.assert_called_once()


    mock_weather_service.get_city_name_nominatim.assert_called_once_with("НесуществующийГород")
    mock_weather_service.save_to_history.assert_not_called() # Сохранение в историю не должно происходить


@pytest.mark.asyncio
async def test_change_city_save_to_history_fails(client: AsyncClient, mock_weather_service: AsyncMock):

    mock_weather_service.save_to_history.return_value = False # Мокируем ошибку сохранения
    form_data = {"city": "ТестовыйГород"}
    response = await client.post("/", data=form_data, follow_redirects=False)

    assert response.status_code == 500
    assert response.json() == {"detail": "Somthing went's wrong"}

    mock_weather_service.save_to_history.assert_called_once()


@pytest.mark.asyncio
async def test_get_stats_with_history(client: AsyncClient, mock_weather_service: AsyncMock):
    mock_weather_service.get_history.return_value = [
        {"city": "Москва", "count": 5},
        {"city": "Лондон", "count": 3}
    ]
    response = await client.get("/api/stats")

    assert response.status_code == 200
    assert response.json() == [
        {"city": "Москва", "count": 5},
        {"city": "Лондон", "count": 3}
    ]
    mock_weather_service.get_history.assert_called_once()


@pytest.mark.asyncio
async def test_get_stats_empty_history(client: AsyncClient, mock_weather_service: AsyncMock):
    mock_weather_service.get_history.return_value = None # Или []
    response = await client.get("/api/stats")
    assert response.status_code == 200
    assert response.json() == {"ok": True, 'message': "History is empty"}
    mock_weather_service.get_history.assert_called_once()

