from fastapi import APIRouter
from app.db import get_db_connection
from pydantic import BaseModel
from datetime import date

router = APIRouter(prefix="/licenses", tags=["Licenses"])

class LicenseCreate(BaseModel):
    company_id: int
    operator_id: int
    computer_id: int
    software_id: int
    expire_date: date
    paid: float = 0
    stayed: float = 0
    status: str = "active"
    license_status: str = "valid"

@router.get("/")
def get_licenses():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM licenses ORDER BY license_id")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

@router.post("/")
def create_license(lic: LicenseCreate):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO licenses (company_id, operator_id, computer_id, software_id,
            expire_date, paid, stayed, status, license_status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING license_id
    """, (
        lic.company_id, lic.operator_id, lic.computer_id, lic.software_id,
        lic.expire_date, lic.paid, lic.stayed, lic.status, lic.license_status
    ))
    new_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return {"license_id": new_id}
