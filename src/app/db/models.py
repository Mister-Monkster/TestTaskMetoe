from typing import Annotated

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from config import Base

pk = Annotated[int, mapped_column(primary_key=True, autoincrement=True)]

class WeatherCodes(Base):
    __tablename__ = 'weather_codes'

    id: Mapped[pk]
    code: Mapped[int] = mapped_column(index=True)
    description: Mapped[str] = mapped_column(String(100))
    emoji: Mapped[str] = mapped_column(String(25))


class UsersHistory(Base):
    __tablename__ = 'users_history'

    id: Mapped[pk]
    token: Mapped[str]
    city_name: Mapped[str] = mapped_column(String(100))
