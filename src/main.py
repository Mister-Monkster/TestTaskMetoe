import uvicorn
from fastapi import FastAPI
from starlette.staticfiles import StaticFiles


from app.api.routers.weather_router import router
from app.api.routers.api_router import router as api_router

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")


app.include_router(router)
app.include_router(api_router)


if __name__ == "__main__":
    uvicorn.run(app)
