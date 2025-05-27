
from fastapi import HTTPException
from uuid import uuid4

from fastapi import APIRouter, Cookie, Request, Form
from starlette.responses import RedirectResponse
from starlette.templating import Jinja2Templates

from app.dependencies.service_deps import ServiceDep
from app.models.models import HistorySchema

router = APIRouter()
templates = Jinja2Templates(directory='./templates')

@router.get('/')
async def main_page(request: Request, service: ServiceDep, recent_city: str  =  Cookie(default=None)):
    context = {"request": request,
               "recent_city": recent_city}
    if not recent_city is None:
        ru_city = await service.get_city_name_nominatim(recent_city, lang='ru')
        context['recent_city'] = ru_city
        res = await service.get_weather(recent_city)
        if not res is None:
            context.update(res)
    return templates.TemplateResponse('mainpage.html', context=context)

@router.post('/')
async def change_city(service: ServiceDep, session_token: str | None = Cookie(default=None), city: str = Form(...)):
    en_city = await service.get_city_name_nominatim(city)
    res = RedirectResponse(status_code=301, url='/')
    if not en_city is None:
        res.set_cookie(key='recent_city', value=en_city, expires=3600 * 24 * 365)
        if session_token is None:
            session_token = str(uuid4())
            res.set_cookie(key='session_token', value=session_token, expires=3600 *  24 * 30)
        data = HistorySchema(token=session_token, city_name=city)
        service_res = await service.save_to_history(data)
        print(service_res)
        if not service_res:
            raise HTTPException(status_code=500, detail="Somthing went's wrong")
    return res

