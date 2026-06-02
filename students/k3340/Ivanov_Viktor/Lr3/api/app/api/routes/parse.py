from __future__ import annotations

import httpx
from celery import Celery
from celery.result import AsyncResult
from fastapi import APIRouter, HTTPException

from app.core.config import settings

router = APIRouter(prefix="/parse", tags=["parse"])

celery_app = Celery(
    "api_worker",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)
celery_app.conf.task_routes = {"parser.tasks.*": {"queue": "parse"}}


@router.post("/sync")
def parse_sync(url: str) -> dict:
    try:
        response = httpx.post(
            f"{settings.parser_url}/parse",
            params={"url": url},
            timeout=120,
        )
        response.raise_for_status()
        return response.json()
    except httpx.RequestError as exc:
        raise HTTPException(status_code=503, detail=f"parser недоступен: {exc}")
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)


@router.post("/async")
def parse_async(url: str) -> dict:
    task = celery_app.send_task("parser.tasks.parse_url", args=[url], queue="parse")
    return {"task_id": task.id, "status": "queued"}


@router.get("/result/{task_id}")
def parse_result(task_id: str) -> dict:
    result = AsyncResult(task_id, app=celery_app)
    if result.state == "PENDING":
        return {"task_id": task_id, "status": "pending"}
    if result.state == "FAILURE":
        raise HTTPException(status_code=500, detail=str(result.result))
    if result.state == "SUCCESS":
        return {"task_id": task_id, "status": "success", "result": result.result}
    return {"task_id": task_id, "status": result.state}
