from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from app.routers import web

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.include_router(web.router)

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return RedirectResponse("/web/companies")
