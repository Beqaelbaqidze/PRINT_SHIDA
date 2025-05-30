from fastapi import APIRouter
from app.db import get_db_connection
from pydantic import BaseModel

router = APIRouter(prefix="/companies", tags=["Companies"])

class CompanyCreate(BaseModel):
    company_name: str
    company_number: str
    company_director: str | None = None
    company_phone_number: str | None = None
    company_email: str | None = None
    company_address: str | None = None

@router.get("/")
def get_companies():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM companies ORDER BY company_id")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

@router.post("/")
def create_company(company: CompanyCreate):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO companies (company_name, company_number, company_director, company_phone_number, company_email, company_address)
        VALUES (%s, %s, %s, %s, %s, %s) RETURNING company_id
    """, (
        company.company_name,
        company.company_number,
        company.company_director,
        company.company_phone_number,
        company.company_email,
        company.company_address
    ))
    new_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return {"company_id": new_id}
