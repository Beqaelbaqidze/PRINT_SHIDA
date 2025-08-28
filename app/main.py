from fastapi import FastAPI, Query, HTTPException, Request
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
import json
from starlette.middleware.sessions import SessionMiddleware
from fastapi.responses import RedirectResponse
from fastapi import Form
from datetime import date
from decimal import Decimal
from psycopg2.extras import RealDictCursor

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="BeqasSecretKey")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

templates = Jinja2Templates(directory="templates")


# Load environment variables
load_dotenv()


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

# === SOFTWARE BUTTON MODELS ===
class SoftwareButtonCreate(BaseModel):
    software_id: int
    button_name: str

class SoftwareButton(SoftwareButtonCreate):
    button_id: int

class LicenseCheckRequest(BaseModel):
    company_name: str
    company_number: str
    company_phone_number: str
    company_email: str
    company_address: str
    computer_guid: str
    computer_mac_address: str
    operator_fullname: str



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
def filter_by(table: str, column: str, value: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM {table} WHERE {column} = %s", (value,))
    rows = cur.fetchall()
    columns = [desc[0] for desc in cur.description]
    cur.close()
    conn.close()
    return [dict(zip(columns, row)) for row in rows]

# === FILTER ENDPOINTS ===
@app.get("/companies/filter/{company_name}")
def filter_companies(company_name: str):
    results = filter_by("companies", "company_name", company_name)
    if not results:
        raise HTTPException(status_code=404, detail="Company not found")
    return results
@app.get("/operators/filter/{operator_name}")
def filter_operators(operator_name: str):
    results = filter_by("operators", "operator_name", operator_name)
    if not results:
        raise HTTPException(status_code=404, detail="Operator not found")
    return results
@app.get("/computers/filter/{computer_guid}")
def filter_computers(computer_guid: str):
    results = filter_by("computers", "computer_guid", computer_guid)
    if not results:
        raise HTTPException(status_code=404, detail="Computer not found")
    return results
@app.get("/softwares/filter/{software_name}")
def filter_softwares(software_name: str):
    results = filter_by("softwares", "software_name", software_name)
    if not results:
        raise HTTPException(status_code=404, detail="Software not found")
    return results
@app.get("/licenses/filter/{license_id}")
def filter_licenses(license_id: int):
    results = filter_by("licenses", "license_id", license_id)
    if not results:
        raise HTTPException(status_code=404, detail="License not found")
    return results

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
def create_license(license: LicenseCreate):
    conn = get_connection()
    cur = conn.cursor()

    # Get software price
    cur.execute("SELECT price FROM softwares WHERE software_id = %s", (license.software_id,))
    row = cur.fetchone()
    software_price = row[0] if row else Decimal(0)

    # Calculate stayed
    stayed = software_price - Decimal(license.paid or 0)

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
    software_price = row[0] if row else Decimal(0)

    # Calculate stayed safely
    from decimal import Decimal
    stayed = software_price - Decimal(license.paid or 0)

    # Determine license status
    today = date.today()
    is_valid = license.expire_date >= today
    license_status = "valid" if license.status == "active" and is_valid else "invalid"

    cur.execute("""
        UPDATE licenses SET 
            company_id = %s,
            operator_id = %s,
            computer_id = %s,
            software_id = %s,
            expire_date = %s,
            paid = %s,
            stayed = %s,
            status = %s,
            license_status = %s
        WHERE license_id = %s
    """, (
        license.company_id, license.operator_id, license.computer_id,
        license.software_id, license.expire_date, license.paid,
        stayed, license.status, license_status,
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


@app.get("/softwares_buttons")
def get_software_buttons():
    return fetch_all("softwares_buttons")

@app.post("/softwares_buttons/create", response_model=int)
def create_software_button(button: SoftwareButtonCreate):
    return insert("softwares_buttons", button.dict(), "button_id")

@app.put("/softwares_buttons/update", response_model=int)
def update_software_button(button: SoftwareButton):
    return update("softwares_buttons", button.button_id, button.dict(), "button_id")

@app.delete("/softwares_buttons/{button_id}")
def delete_software_button(button_id: int):
    delete("softwares_buttons", button_id, "button_id")

from fastapi import HTTPException
from pydantic import BaseModel
import re

class LicenseCheckRequest(BaseModel):
    company_name: str
    company_number: str
    company_phone_number: str
    company_email: str
    company_address: str
    computer_guid: str
    computer_mac_address: str
    operator_fullname: str  # Example: "John Smith (010110008513)"
    identify_count: Optional[int] = None  # Optional field for identify count
    button_clicked: Optional[str] = None  # Optional field for button clicked



@app.post("/licenses/check")
def check_license(request: Request, data: LicenseCheckRequest):
    conn = get_connection()
    cur = conn.cursor()

        # === Auto-expire any outdated licenses ===
    today = date.today()
    cur.execute("""
        UPDATE licenses
        SET license_status = 'invalid', status = 'inactive'
        WHERE expire_date < %s AND license_status = 'valid'
    """, (today,))
    conn.commit()


    # Extract operator name and identify ID
    match = re.match(r"^(.*)\s+\((\d+)\)$", data.operator_fullname.strip())
    if not match:
        raise HTTPException(status_code=400, detail="Invalid operator format. Expected: 'Name (ID)'")
    operator_name = match.group(1).strip()
    identify_id = match.group(2).strip()

    # Step 1: Find company
    cur.execute("""
        SELECT company_id FROM companies
        WHERE company_name = %s AND company_number = %s AND
              company_phone_number = %s AND company_email = %s AND
              company_address = %s
    """, (
        data.company_name,
        data.company_number,
        data.company_phone_number,
        data.company_email,
        data.company_address
    ))
    company_row = cur.fetchone()
    if not company_row:
        raise HTTPException(status_code=404, detail="Company not found")
    company_id = company_row[0]

    # Step 2: Find computer
    cur.execute("""
        SELECT computer_id FROM computers
        WHERE computer_guid = %s AND computer_mac_address = %s
    """, (data.computer_guid, data.computer_mac_address))
    computer_row = cur.fetchone()
    if not computer_row:
        raise HTTPException(status_code=404, detail="Computer not found")
    computer_id = computer_row[0]

    # Step 3: Find operator
    cur.execute("""
        SELECT operator_id FROM operators
        WHERE operator_name = %s AND identify_id::text = %s
    """, (operator_name, identify_id))
    operator_row = cur.fetchone()
    if not operator_row:
        raise HTTPException(status_code=404, detail="Operator not found")
    operator_id = operator_row[0]

    # Step 4: Find valid licenses
    cur.execute("""
        SELECT s.software_id, s.software_name, s.price
        FROM licenses l
        JOIN softwares s ON l.software_id = s.software_id
        WHERE l.company_id = %s AND l.computer_id = %s AND
              l.operator_id = %s AND l.license_status = 'valid'
    """, (company_id, computer_id, operator_id))
    softwares = cur.fetchall()
    if not softwares:
        raise HTTPException(status_code=403, detail="No valid license found for this setup")

    # Step 5: Return software list with buttons
    software_list = []
    for s_id, s_name, s_price in softwares:
        cur.execute("""
            SELECT button_id, button_name
            FROM softwares_buttons
            WHERE software_id = %s
        """, (s_id,))
        buttons = cur.fetchall()

        software_list.append({
            "software_id": s_id,
            "software_name": s_name,
            "price": float(s_price),
            "buttons": [
                {"button_id": b_id, "button_name": b_name} for b_id, b_name in buttons
            ]
        })

    cur.close()
    conn.close()

    # Prepare response
    response = {
        "status": "valid",
        "softwares": software_list
    }

    # Log request and response
    log_request_to_db(
        endpoint=str(request.url.path),
        method=request.method,
        request_body=data.dict(),
        response_body=response
    )

    return response



class AutofillRequest(BaseModel):
    computer_guid: str
    computer_mac_address: str

def log_request_to_db(endpoint: str, method: str, request_body: dict, response_body: dict):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO log (endpoint, method, request_body, response_body)
        VALUES (%s, %s, %s, %s)
    """, (endpoint, method, json.dumps(request_body), json.dumps(response_body)))
    conn.commit()
    cur.close()
    conn.close()



@app.post("/licenses/autofill")
def autofill_license_info(data: AutofillRequest):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT c.company_name, c.company_number, c.company_phone_number,
               c.company_email, c.company_address, o.operator_name, o.identify_id
        FROM licenses l
        JOIN companies c ON l.company_id = c.company_id
        JOIN computers m ON l.computer_id = m.computer_id
        JOIN operators o ON l.operator_id = o.operator_id
        WHERE m.computer_guid = %s AND m.computer_mac_address = %s
          AND l.license_status = 'valid'
        LIMIT 1
    """, (data.computer_guid, data.computer_mac_address))

    rows = cur.fetchall()
    cur.close()
    conn.close()

    if not rows:
        raise HTTPException(status_code=404, detail="No valid license found for this computer.")

    results = []
    seen = set()  # To avoid duplicates for same company/operator

    for row in rows:
        key = (row[0], row[5], row[6])  # (company_name, operator_name, identify_id)
        if key in seen:
            continue
        seen.add(key)

        results.append({
            "company_name": row[0],
            "company_number": row[1],
            "company_phone_number": row[2],
            "company_email": row[3],
            "company_address": row[4],
            "operator_fullname": f"{row[5]} ({row[6]})"
    })

    return results
from fastapi.responses import PlainTextResponse


#commit
@app.get("/api/operators/by-machine", response_class=PlainTextResponse)
def get_operators_by_machine_get(machine_name: str, mac_address: str):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT DISTINCT o.operator_name || ' (' || o.identify_id || ')' AS fullname
        FROM licenses l
        JOIN operators o ON l.operator_id = o.operator_id
        WHERE l.computer_id = (
            SELECT computer_id FROM computers
            WHERE TRIM(LOWER(computer_guid)) = TRIM(LOWER(%s))
              AND TRIM(LOWER(computer_mac_address)) = TRIM(LOWER(%s))
        )
        AND LOWER(l.license_status) = 'valid'
    """, (machine_name.strip().lower(), mac_address.strip().lower()))

    rows = cur.fetchall()
    cur.close()
    conn.close()

    if not rows:
        raise HTTPException(status_code=404, detail="No operators found for this machine.")

    result = "\n".join([r[0] for r in rows])
    return result

