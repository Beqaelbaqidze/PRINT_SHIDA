from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.db import get_db_connection

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/web/companies", response_class=HTMLResponse)
def web_companies(request: Request):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM companies ORDER BY company_id")
    companies = cur.fetchall()
    cur.close()
    conn.close()
    return templates.TemplateResponse("companies.html", {"request": request, "companies": companies})

@router.post("/web/companies/create")
def create_company(request: Request,
                   company_name: str = Form(...),
                   company_number: str = Form(...),
                   company_director: str = Form(None),
                   company_phone_number: str = Form(None),
                   company_email: str = Form(None),
                   company_address: str = Form(None)):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO companies (company_name, company_number, company_director, company_phone_number, company_email, company_address)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (company_name, company_number, company_director, company_phone_number, company_email, company_address))
    conn.commit()
    cur.close()
    conn.close()
    return RedirectResponse("/web/companies", status_code=302)

@router.post("/web/companies/delete")
def delete_company(request: Request, company_id: int = Form(...)):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM companies WHERE company_id = %s", (company_id,))
    conn.commit()
    cur.close()
    conn.close()
    return RedirectResponse("/web/companies", status_code=302)
