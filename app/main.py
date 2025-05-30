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

templates = Jinja2Templates(directory="templates")


# Load environment variables
load_dotenv()

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
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
class Company(BaseModel):
    company_name: str
    company_number: str
    company_director: Optional[str]
    company_phone_number: Optional[str]
    company_email: Optional[str]
    company_address: Optional[str]

class Operator(BaseModel):
    operator_name: str
    identify_id: str

class Computer(BaseModel):
    computer_guid: str
    computer_mac_address: Optional[str]

class Software(BaseModel):
    software_name: str
    price: float

class License(BaseModel):
    company_id: int
    operator_id: int
    computer_id: int
    software_id: int
    expire_date: date
    paid: Optional[float] = 0
    stayed: Optional[float] = 0
    status: Optional[str] = "active"
    license_status: Optional[str] = "valid"

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

def delete(table: str, record_id: int, id_field: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f"DELETE FROM {table} WHERE {id_field} = %s", (record_id,))
    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail=f"{table[:-1].capitalize()} not found")
    conn.commit()
    cur.close()
    conn.close()

# === CRUD ENDPOINTS ===

# Companies
@app.get("/companies")
def get_companies(): return fetch_all("companies")

@app.post("/companies")
def create_company(company: Company):
    new_id = insert("companies", company.dict(), "company_id")
    return {**company.dict(), "company_id": new_id}

@app.put("/companies/{company_id}")
def update_company(company_id: int, company: Company):
    update("companies", company_id, company.dict(), "company_id")
    return {**company.dict(), "company_id": company_id}

@app.delete("/companies/{company_id}")
def delete_company(company_id: int):
    delete("companies", company_id, "company_id")
    return {"message": f"Company {company_id} deleted"}

# Operators
@app.get("/operators")
def get_operators(): return fetch_all("operators")

@app.post("/operators")
def create_operator(op: Operator):
    new_id = insert("operators", op.dict(), "operator_id")
    return {**op.dict(), "operator_id": new_id}

@app.put("/operators/{operator_id}")
def update_operator(operator_id: int, op: Operator):
    update("operators", operator_id, op.dict(), "operator_id")
    return {**op.dict(), "operator_id": operator_id}

@app.delete("/operators/{operator_id}")
def delete_operator(operator_id: int):
    delete("operators", operator_id, "operator_id")
    return {"message": f"Operator {operator_id} deleted"}

# Computers
@app.get("/computers")
def get_computers(): return fetch_all("computers")

@app.post("/computers")
def create_computer(comp: Computer):
    new_id = insert("computers", comp.dict(), "computer_id")
    return {**comp.dict(), "computer_id": new_id}

@app.put("/computers/{computer_id}")
def update_computer(computer_id: int, comp: Computer):
    update("computers", computer_id, comp.dict(), "computer_id")
    return {**comp.dict(), "computer_id": computer_id}

@app.delete("/computers/{computer_id}")
def delete_computer(computer_id: int):
    delete("computers", computer_id, "computer_id")
    return {"message": f"Computer {computer_id} deleted"}

# Softwares
@app.get("/softwares")
def get_softwares(): return fetch_all("softwares")

@app.post("/softwares")
def create_software(soft: Software):
    new_id = insert("softwares", soft.dict(), "software_id")
    return {**soft.dict(), "software_id": new_id}

@app.put("/softwares/{software_id}")
def update_software(software_id: int, soft: Software):
    update("softwares", software_id, soft.dict(), "software_id")
    return {**soft.dict(), "software_id": software_id}

@app.delete("/softwares/{software_id}")
def delete_software(software_id: int):
    delete("softwares", software_id, "software_id")
    return {"message": f"Software {software_id} deleted"}

# Licenses

@app.post("/licenses")
def create_license(lic: License):
    new_id = insert("licenses", lic.dict(), "license_id")
    return {**lic.dict(), "license_id": new_id}

@app.put("/licenses/{license_id}")
def update_license(license_id: int, lic: License):
    update("licenses", license_id, lic.dict(), "license_id")
    return {**lic.dict(), "license_id": license_id}

@app.delete("/licenses/{license_id}")
def delete_license(license_id: int):
    delete("licenses", license_id, "license_id")
    return {"message": f"License {license_id} deleted"}
