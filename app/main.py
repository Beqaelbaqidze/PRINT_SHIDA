from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import psycopg2
from typing import List, Optional
from datetime import date
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from fastapi.responses import RedirectResponse
from fastapi import Form
from datetime import date

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="BeqasSecretKey")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

templates = Jinja2Templates(directory="templates")


# Load environment variables
load_dotenv()

app = FastAPI()

@app.get("/login", response_class=HTMLResponse)
def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": None})

@app.post("/login")
def login(request: Request, username: str = Form(...), password: str = Form(...)):
    if username == "admin" and password == "admin123":
        request.session["user"] = username
        return RedirectResponse(url="/", status_code=302)
    return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})

@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=302)


@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    if not request.session.get("user"):
        return RedirectResponse(url="/login")
    return templates.TemplateResponse("dashboard.html", {"request": request})


def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )

# === MODELS ===

# === COMPANY MODELS ===
class CompanyCreate(BaseModel):
    company_name: str
    company_number: str
    company_director: Optional[str]
    company_phone_number: Optional[str]
    company_email: Optional[str]
    company_address: Optional[str]

class Company(CompanyCreate):
    company_id: int


# === OPERATOR MODELS ===
class OperatorCreate(BaseModel):
    operator_name: str
    identify_id: str

class Operator(OperatorCreate):
    operator_id: int


# === COMPUTER MODELS ===
class ComputerCreate(BaseModel):
    computer_guid: str
    computer_mac_address: Optional[str]

class Computer(ComputerCreate):
    computer_id: int


# === SOFTWARE MODELS ===
class SoftwareCreate(BaseModel):
    software_name: str
    price: float

class Software(SoftwareCreate):
    software_id: int


# === LICENSE MODELS ===
class LicenseCreate(BaseModel):
    company_id: int
    operator_id: int
    computer_id: int
    software_id: int
    expire_date: date
    paid: Optional[float] = 0
    stayed: Optional[float] = 0
    status: Optional[str] = "active"
    license_status: Optional[str] = "valid"

class License(LicenseCreate):
    license_id: int

# === GENERIC DB HELPERS ===
def fetch_all(table: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM {table}")
    rows = cur.fetchall()
    columns = [desc[0] for desc in cur.description]
    cur.close()
    conn.close()
    return [dict(zip(columns, row)) for row in rows]

def insert(table: str, data: dict, return_column: str = "id"):
    conn = get_connection()
    cur = conn.cursor()
    keys = ', '.join(data.keys())
    values = list(data.values())
    placeholders = ', '.join(['%s'] * len(values))
    cur.execute(f"INSERT INTO {table} ({keys}) VALUES ({placeholders}) RETURNING {return_column}", values)
    new_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return new_id

def update(table: str, record_id: int, data: dict, id_field: str):
    conn = get_connection()
    cur = conn.cursor()
    set_clause = ', '.join([f"{k} = %s" for k in data.keys()])
    values = list(data.values()) + [record_id]
    cur.execute(f"UPDATE {table} SET {set_clause} WHERE {id_field} = %s", values)
    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail=f"{table[:-1].capitalize()} not found")
    conn.commit()
    cur.close()
    conn.close()
    return record_id  # ✅ Add this


def delete(table: str, record_id: int, id_field: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f"DELETE FROM {table} WHERE {id_field} = %s", (record_id,))
    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail=f"{table[:-1].capitalize()} not found")
    conn.commit()
    cur.close()
    conn.close()

# === GET ENDPOINTS ===
@app.get("/companies")
def get_companies(): return fetch_all("companies")

@app.get("/operators")
def get_operators(): return fetch_all("operators")

@app.get("/computers")
def get_computers(): return fetch_all("computers")

@app.get("/softwares")
def get_softwares(): return fetch_all("softwares")

@app.get("/licenses")
def get_licenses(): return fetch_all("licenses")

# === CREATE ENDPOINTS ===
@app.post("/companies/create", response_model=int)
def create_company(company: CompanyCreate):
    return insert("companies", company.dict(), "company_id")

@app.post("/operators/create", response_model=int)
def create_operator(operator: OperatorCreate):
    return insert("operators", operator.dict(), "operator_id")

@app.post("/computers/create", response_model=int)
def create_computer(computer: ComputerCreate):
    return insert("computers", computer.dict(), "computer_id")

@app.post("/softwares/create", response_model=int)
def create_software(software: SoftwareCreate):
    return insert("softwares", software.dict(), "software_id")

@app.post("/licenses/create")
def create_license(license: License):
    conn = get_connection()
    cur = conn.cursor()

    # Get software price
    cur.execute("SELECT price FROM softwares WHERE software_id = %s", (license.software_id,))
    row = cur.fetchone()
    software_price = row[0] if row else 0

    # Calculate stayed
    stayed = software_price - (license.paid or 0)

    # Determine license status
    today = date.today()
    is_valid = license.expire_date >= today
    license_status = "valid" if license.status == "active" and is_valid else "invalid"

    cur.execute("""
        INSERT INTO licenses (company_id, operator_id, computer_id, software_id, expire_date, paid, stayed, status, license_status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        license.company_id, license.operator_id, license.computer_id, license.software_id,
        license.expire_date, license.paid, stayed, license.status, license_status
    ))

    conn.commit()
    cur.close()
    conn.close()
    return {"success": True}

# === UPDATE ENDPOINTS ===
@app.put("/companies/update", response_model=int)
def update_company(company: Company):
    return update("companies", company.company_id, company.dict(), "company_id")

@app.put("/operators/update", response_model=int)
def update_operator(operator: Operator):
    return update("operators", operator.operator_id, operator.dict(), "operator_id")

@app.put("/computers/update", response_model=int)
def update_computer(computer: Computer):
    return update("computers", computer.computer_id, computer.dict(), "computer_id")

@app.put("/softwares/update", response_model=int)
def update_software(software: Software):
    return update("softwares", software.software_id, software.dict(), "software_id")

@app.put("/licenses/update")
def update_license(license: License):
    conn = get_connection()
    cur = conn.cursor()

    # Get software price
    cur.execute("SELECT price FROM softwares WHERE software_id = %s", (license.software_id,))
    row = cur.fetchone()
    software_price = row[0] if row else 0

    # Recalculate stayed and status
    stayed = software_price - (license.paid or 0)
    today = date.today()
    is_valid = license.expire_date >= today
    license_status = "valid" if license.status == "active" and is_valid else "invalid"

    cur.execute("""
        UPDATE licenses SET
            company_id=%s, operator_id=%s, computer_id=%s, software_id=%s,
            expire_date=%s, paid=%s, stayed=%s, status=%s, license_status=%s
        WHERE license_id = %s
    """, (
        license.company_id, license.operator_id, license.computer_id, license.software_id,
        license.expire_date, license.paid, stayed, license.status, license_status,
        license.license_id
    ))

    conn.commit()
    cur.close()
    conn.close()
    return {"success": True}


# === DELETE ENDPOINTS ===
@app.delete("/companies/{company_id}")
def delete_company(company_id: int):
    delete("companies", company_id, "company_id")

@app.delete("/operators/{operator_id}")
def delete_operator(operator_id: int):
    delete("operators", operator_id, "operator_id")

@app.delete("/computers/{computer_id}")
def delete_computer(computer_id: int):
    delete("computers", computer_id, "computer_id")

@app.delete("/softwares/{software_id}")
def delete_software(software_id: int):
    delete("softwares", software_id, "software_id")

@app.delete("/licenses/{license_id}")
def delete_license(license_id: int):
    delete("licenses", license_id, "license_id")