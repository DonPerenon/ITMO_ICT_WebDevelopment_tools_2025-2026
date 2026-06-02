from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import settings
from app.db.session import init_db

app = FastAPI(
    title="Personal Finance API",
    description="Лабораторная работа №1 — сервис личных финансов. ЛР3 добавляет эндпоинты /api/v1/parse/*",
    version="1.3.0",
)


@app.on_event("startup")
def on_startup() -> None:
    if settings.auto_create_tables:
        init_db()


@app.get("/")
def root() -> dict[str, str]:
    return {"status": "ok", "service": "personal-finance-api"}


app.include_router(api_router, prefix="/api/v1")
