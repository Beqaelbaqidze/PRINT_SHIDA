from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from app.routers import web

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="super-secret-session-key")

templates = Jinja2Templates(directory="templates")
app.include_router(web.router)

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    if not request.session.get("user"):
        return RedirectResponse("/login")
    return RedirectResponse("/web/companies")
