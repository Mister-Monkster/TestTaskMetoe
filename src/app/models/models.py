from pydantic import BaseModel, Field, ConfigDict


class WeatherResponse(BaseModel):
    description: str = Field(description='Описание погоды')
    emoji: str = Field(description='Эмодзи')

    model_config = ConfigDict(from_attributes=True)

class HistorySchema(BaseModel):
    token: str = Field(max_length=50, min_length=8, description='Токен сессии')
    city_name: str

class HistoryResponse(BaseModel):
    city: str
    count: int


