from fastapi import APIRouter
from app.db import get_db_connection
from pydantic import BaseModel

router = APIRouter(prefix="/computers", tags=["Computers"])

class ComputerCreate(BaseModel):
    computer_guid: str
    computer_mac_address: str

@router.get("/")
def get_computers():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM computers ORDER BY computer_id")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

@router.post("/")
def create_computer(comp: ComputerCreate):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO computers (computer_guid, computer_mac_address)
        VALUES (%s, %s) RETURNING computer_id
    """, (comp.computer_guid, comp.computer_mac_address))
    new_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return {"computer_id": new_id}
