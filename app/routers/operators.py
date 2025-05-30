from fastapi import APIRouter
from app.db import get_db_connection
from pydantic import BaseModel

router = APIRouter(prefix="/operators", tags=["Operators"])

class OperatorCreate(BaseModel):
    operator_name: str
    identify_id: str

@router.get("/")
def get_operators():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM operators ORDER BY operator_id")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

@router.post("/")
def create_operator(op: OperatorCreate):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO operators (operator_name, identify_id)
        VALUES (%s, %s) RETURNING operator_id
    """, (op.operator_name, op.identify_id))
    new_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return {"operator_id": new_id}
