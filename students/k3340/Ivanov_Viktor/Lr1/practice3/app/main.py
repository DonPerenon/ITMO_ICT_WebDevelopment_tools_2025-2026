from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import settings
from app.db.session import init_db

app = FastAPI(title="Practice 1.3 - Personal Finance API")


@app.on_event("startup")
def on_startup() -> None:
    if settings.auto_create_tables:
        init_db()


@app.get("/")
def root() -> dict[str, str]:
    return {"status": "ok", "practice": "1.3"}


app.include_router(api_router, prefix="/api/v1")
