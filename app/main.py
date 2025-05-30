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
    company_id: int
    company_name: str
    company_number: str
    company_director: Optional[str]
    company_phone_number: Optional[str]
    company_email: Optional[str]
    company_address: Optional[str]

class Operator(BaseModel):
    operator_id: int
    operator_name: str
    identify_id: str

class Computer(BaseModel):
    computer_id: int
    computer_guid: str
    computer_mac_address: Optional[str]

class Software(BaseModel):
    software_id: int
    software_name: str
    price: float

class License(BaseModel):
    license_id: int
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

# === GET DATA ENDPOINTS ===


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

# === UPDATE DATA ENDPOINTS ===

@app.post("/companies", response_model=int)
def update_company(company: Company): return update("companies", company.company_id, company.dict(), "company_id")

@app.post("/operators", response_model=int)
def update_operator(operator: Operator): return update("operators", operator.operator_id, operator.dict(), "operator_id")

@app.post("/computers", response_model=int)
def update_computer(computer: Computer): return update("computers", computer.computer_id, computer.dict(), "computer_id")

@app.post("/softwares", response_model=int)
def update_software(software: Software): return update("softwares", software.software_id, software.dict(), "software_id")

@app.post("/licenses", response_model=int)
def update_license(license: License): return update("licenses", license.license_id, license.dict(), "license_id")