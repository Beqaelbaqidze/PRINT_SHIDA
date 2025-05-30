from fastapi import APIRouter
from app.db import get_db_connection
from pydantic import BaseModel

router = APIRouter(prefix="/softwares", tags=["Softwares"])

class SoftwareCreate(BaseModel):
    software_name: str
    price: float

@router.get("/")
def get_softwares():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM softwares ORDER BY software_id")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

@router.post("/")
def create_software(sw: SoftwareCreate):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO softwares (software_name, price)
        VALUES (%s, %s) RETURNING software_id
    """, (sw.software_name, sw.price))
    new_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return {"software_id": new_id}
