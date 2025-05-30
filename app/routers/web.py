
from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.db import get_db_connection

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
def login(request: Request, username: str = Form(...), password: str = Form(...)):
    if username == "admin" and password == "admin":
        request.session["user"] = username
        return RedirectResponse("/dashboard", status_code=302)
    return RedirectResponse("/", status_code=302)

@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/", status_code=302)

@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    if not request.session.get("user"):
        return RedirectResponse("/", status_code=302)
    return templates.TemplateResponse("dashboard.html", {"request": request})
