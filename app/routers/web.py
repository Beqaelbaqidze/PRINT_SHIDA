from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.db import get_db_connection

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# In-memory fake login (no authentication yet)
FAKE_USERNAME = "admin"
FAKE_PASSWORD = "1234"

@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login", response_class=HTMLResponse)
def login_post(request: Request, username: str = Form(...), password: str = Form(...)):
    if username == FAKE_USERNAME and password == FAKE_PASSWORD:
        response = RedirectResponse(url="/web/companies", status_code=302)
        return response
    return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})

@router.get("/web/companies", response_class=HTMLResponse)
def web_companies(request: Request):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM companies")
    companies = cur.fetchall()
    cur.close()
    conn.close()
    return templates.TemplateResponse("companies.html", {"request": request, "companies": companies})
