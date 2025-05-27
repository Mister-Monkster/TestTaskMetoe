import asyncio
import json

import requests
from geopy import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from redis.asyncio import Redis

from app.db.reository import Repository
from app.models.models import HistorySchema


class WeatherService:
    def __init__(self, repository: Repository, redis: Redis):
        self.repository = repository
        self.geolocator = Nominatim(user_agent="my-city-translator-app-v1")
        self.geocode = RateLimiter(self.geolocator.geocode)
        self.redis = redis

    async def get_city_name_nominatim(self, city_name, lang='en'):
        """Перевод названий городов"""
        try:
            location = self.geocode(city_name, language=lang)
            if location:
                return location.raw['name']
            else:
                return None
        except:
            return None


    async def get_geo(self, city: str) -> dict[str, float] | None:
        """Получение координат по названию"""
        response = requests.get(
            f"https://geocoding-api.open-meteo.com/v1/search?name={city.strip()}&count=1&language=ru&format=json"
        ).json()
        try:
            latitude = response['results'][0]['latitude']
            longitude = response['results'][0]['longitude']
            return {'latitude': latitude, 'longitude': longitude}
        except KeyError:
            return None


    async def format_json(self, data: dict):
        """Форматирование словаря/json под нужный формат"""
        date_time_list = data['time'].split('T')
        data['time'] = date_time_list[1]
        data['date'] = date_time_list[0]
        data['interval'] = str(data['interval'] // 60) + ' минут'
        data['temperature'] = str(data['temperature']) + ' C°'
        data['windspeed'] = str(data['windspeed']) + ' км/ч'
        data['is_day'] = bool(data['is_day'])
        data.pop('winddirection')
        weather_info = await self.repository.get_weather_by_code(weathercode=data['weathercode'])
        data['description'] = weather_info.description
        data["emoji"] = weather_info.emoji

    async def get_weather(self, city: str):
        """Обращение к апи для получения погоды"""
        try:
            if res_cache := await self.redis.get(city):
                weather_data_json = json.loads(res_cache)
            else:
                coordinates = await self.get_geo(city)
                response = requests.get(f'https://api.open-meteo.com/v1/forecast?latitude={coordinates['latitude']}&longitude={coordinates['longitude']}&current_weather=true&timezone=auto')
                weather_data_json = response.json()['current_weather']
                await self.format_json(weather_data_json)
                try:
                    await self.redis.set(city, json.dumps(weather_data_json), ex=300)
                except:
                    print("Redis connection error")
            return weather_data_json
        except TypeError:
            return None

    async def save_to_history(self, data: HistorySchema):
        """Сохранение обращения в историю"""
        res = await self.repository.save_to_history(data)
        if res:
            return True
        else:
            return False

    async def get_history(self):
        """Получение истории"""
        res = await self.repository.get_statistic()
        if res:
            return res
        return None





