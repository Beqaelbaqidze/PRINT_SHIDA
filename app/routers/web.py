from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.db import get_db_connection

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/web/companies", response_class=HTMLResponse)
def view_companies(request: Request):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM companies ORDER BY 1")
    records = cur.fetchall()
    cur.close()
    conn.close()
    return templates.TemplateResponse("companies.html", {"request": request, "records": records})

@router.post("/web/companies/create")
def create_companies(request: Request,
    company_name: str = Form(...),
    company_number: str = Form(...),
    company_director: str = Form(...),
    company_phone_number: str = Form(...),
    company_email: str = Form(...),
    company_address: str = Form(...)
):
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
def delete_companies(request: Request, companie_id: int = Form(...)):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM companies WHERE companie_id = %s", (companie_id,))
    conn.commit()
    cur.close()
    conn.close()
    return RedirectResponse("/web/companies", status_code=302)

@router.get("/web/operators", response_class=HTMLResponse)
def view_operators(request: Request):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM operators ORDER BY 1")
    records = cur.fetchall()
    cur.close()
    conn.close()
    return templates.TemplateResponse("operators.html", {"request": request, "records": records})

@router.post("/web/operators/create")
def create_operators(request: Request,
    operator_name: str = Form(...),
    identify_id: str = Form(...)
):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO operators (operator_name, identify_id)
        VALUES (%s, %s)
    """, (operator_name, identify_id))
    conn.commit()
    cur.close()
    conn.close()
    return RedirectResponse("/web/operators", status_code=302)

@router.post("/web/operators/delete")
def delete_operators(request: Request, operator_id: int = Form(...)):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM operators WHERE operator_id = %s", (operator_id,))
    conn.commit()
    cur.close()
    conn.close()
    return RedirectResponse("/web/operators", status_code=302)

@router.get("/web/computers", response_class=HTMLResponse)
def view_computers(request: Request):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM computers ORDER BY 1")
    records = cur.fetchall()
    cur.close()
    conn.close()
    return templates.TemplateResponse("computers.html", {"request": request, "records": records})

@router.post("/web/computers/create")
def create_computers(request: Request,
    computer_guid: str = Form(...),
    computer_mac_address: str = Form(...)
):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO computers (computer_guid, computer_mac_address)
        VALUES (%s, %s)
    """, (computer_guid, computer_mac_address))
    conn.commit()
    cur.close()
    conn.close()
    return RedirectResponse("/web/computers", status_code=302)

@router.post("/web/computers/delete")
def delete_computers(request: Request, computer_id: int = Form(...)):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM computers WHERE computer_id = %s", (computer_id,))
    conn.commit()
    cur.close()
    conn.close()
    return RedirectResponse("/web/computers", status_code=302)

@router.get("/web/softwares", response_class=HTMLResponse)
def view_softwares(request: Request):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM softwares ORDER BY 1")
    records = cur.fetchall()
    cur.close()
    conn.close()
    return templates.TemplateResponse("softwares.html", {"request": request, "records": records})

@router.post("/web/softwares/create")
def create_softwares(request: Request,
    software_name: str = Form(...),
    price: str = Form(...)
):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO softwares (software_name, price)
        VALUES (%s, %s)
    """, (software_name, price))
    conn.commit()
    cur.close()
    conn.close()
    return RedirectResponse("/web/softwares", status_code=302)

@router.post("/web/softwares/delete")
def delete_softwares(request: Request, software_id: int = Form(...)):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM softwares WHERE software_id = %s", (software_id,))
    conn.commit()
    cur.close()
    conn.close()
    return RedirectResponse("/web/softwares", status_code=302)

@router.get("/web/licenses", response_class=HTMLResponse)
def view_licenses(request: Request):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM licenses ORDER BY 1")
    records = cur.fetchall()
    cur.close()
    conn.close()
    return templates.TemplateResponse("licenses.html", {"request": request, "records": records})

@router.post("/web/licenses/create")
def create_licenses(request: Request,
    company_id: str = Form(...),
    operator_id: str = Form(...),
    computer_id: str = Form(...),
    software_id: str = Form(...),
    expire_date: str = Form(...),
    paid: str = Form(...),
    stayed: str = Form(...),
    status: str = Form(...),
    license_status: str = Form(...)
):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO licenses (company_id, operator_id, computer_id, software_id, expire_date, paid, stayed, status, license_status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (company_id, operator_id, computer_id, software_id, expire_date, paid, stayed, status, license_status))
    conn.commit()
    cur.close()
    conn.close()
    return RedirectResponse("/web/licenses", status_code=302)

@router.post("/web/licenses/delete")
def delete_licenses(request: Request, license_id: int = Form(...)):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM licenses WHERE license_id = %s", (license_id,))
    conn.commit()
    cur.close()
    conn.close()
    return RedirectResponse("/web/licenses", status_code=302)
