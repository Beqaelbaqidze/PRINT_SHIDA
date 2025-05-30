
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.routers import web, companies, operators, computers, softwares, licenses

app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key="super_secret_key_123")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(web.router)
app.include_router(companies.router)
app.include_router(operators.router)
app.include_router(computers.router)
app.include_router(softwares.router)
app.include_router(licenses.router)
