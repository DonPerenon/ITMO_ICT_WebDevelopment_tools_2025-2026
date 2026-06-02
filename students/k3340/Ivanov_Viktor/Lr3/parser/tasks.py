from __future__ import annotations

import os

import requests
from celery import Celery

from db import MetalPrice, ParsedPage, get_session, init_db
from parser_utils import (
    extract_title,
    fetch_all_pages,
    parse_all_products,
    parse_price_value,
)

CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/0")

celery_app = Celery(
    "parser",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
)
celery_app.conf.task_queues = {
    "parse": {"exchange": "parse", "routing_key": "parse"},
}
celery_app.conf.task_default_queue = "parse"


@celery_app.task(name="parser.tasks.parse_url", bind=True)
def parse_url(self, url: str) -> dict:
    init_db()

    try:
        pages_html = fetch_all_pages(url)
    except requests.RequestException as exc:
        raise self.retry(exc=exc, countdown=10, max_retries=3)

    if not pages_html:
        return {"url": url, "error": "страницы не загружены", "products": 0}

    title = extract_title(pages_html[0])
    products = parse_all_products(pages_html, url)

    with get_session() as session:
        page = ParsedPage(url=url, title=title)
        session.add(page)
        session.commit()
        session.refresh(page)

        for product in products:
            session.add(
                MetalPrice(
                    page_id=page.id,
                    name=product.name,
                    kind=product.kind,
                    size=product.size,
                    steel_grade=product.steel_grade,
                    characteristics=product.characteristics,
                    manufacturer=product.manufacturer,
                    warehouse=product.warehouse,
                    price_text=product.price_text,
                    price_value=parse_price_value(product.price_text),
                )
            )
        session.commit()

    return {
        "url": url,
        "title": title,
        "pages": len(pages_html),
        "products": len(products),
    }
