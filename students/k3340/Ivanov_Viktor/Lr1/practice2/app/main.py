from fastapi import FastAPI

from app.connection import init_db
from app.routers import budgets, categories, tags, transactions, users

app = FastAPI(title="Practice 1.2 - Personal Finance API with SQLModel")


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/")
def healthcheck() -> dict[str, str]:
    return {"status": "ok", "practice": "1.2"}


app.include_router(users.router)
app.include_router(categories.router)
app.include_router(tags.router)
app.include_router(transactions.router)
app.include_router(budgets.router)
