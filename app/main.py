from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import datetime

from app.routers import (
    companies,
    operators,
    computers,
    softwares,
    licenses,
    web  # <-- HTML routes
)
from app.db import get_db_connection

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# ✅ Include all routers
app.include_router(companies.router)
app.include_router(operators.router)
app.include_router(computers.router)
app.include_router(softwares.router)
app.include_router(licenses.router)
app.include_router(web.router)

# ✅ Root Endpoint
@app.get("/")
def root():
    return {"msg": "Licenses API running"}

# ✅ Middleware for Logging Requests to DB
@app.middleware("http")
async def log_requests(request: Request, call_next):
    response = await call_next(request)

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO logs (endpoint, method, timestamp)
            VALUES (%s, %s, %s)
        """, (str(request.url.path), request.method, datetime.datetime.now()))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print("Logging error:", e)

    return response
