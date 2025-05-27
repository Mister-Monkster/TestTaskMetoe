from sqlalchemy import select, insert, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import WeatherCodes, UsersHistory
from app.models.models import WeatherResponse, HistorySchema


class Repository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_weather_by_code(self, weathercode: int) -> WeatherResponse:
        query = select(WeatherCodes).where(WeatherCodes.code == weathercode)
        res = await self.session.execute(query)
        res = res.scalars().one_or_none()
        result = WeatherResponse.model_validate(res)
        return result

    async def save_to_history(self, data: HistorySchema):
        try:
            new_row = UsersHistory(**data.model_dump())
            self.session.add(new_row)
            await self.session.commit()
            return True
        except:
            await self.session.rollback()
            return False


    async def get_statistic(self):
        query = (
            select(
                UsersHistory.city_name,
                func.count().label("search_count")
            )
            .group_by(UsersHistory.city_name)
            .order_by(func.count().desc())
        )

        result = await self.session.execute(query)
        return [
            {"city": row.city_name, "count": row.search_count}
            for row in result.all()
        ]
