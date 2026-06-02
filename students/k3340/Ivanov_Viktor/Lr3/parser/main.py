from __future__ import annotations

import requests
from fastapi import FastAPI, HTTPException

from db import MetalPrice, ParsedPage, get_session, init_db
from parser_utils import (
    URLS,
    extract_title,
    fetch_all_pages,
    parse_all_products,
    parse_price_value,
)

app = FastAPI(title="Parser Service", description="Микросервис парсинга каталогов металлопроката")


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/")
def root() -> dict[str, str]:
    return {"status": "ok", "service": "parser"}


@app.get("/urls")
def list_urls() -> dict:
    return {"urls": URLS}


@app.post("/parse")
def parse(url: str) -> dict:
    try:
        pages_html = fetch_all_pages(url)
    except requests.RequestException as exc:
        raise HTTPException(status_code=502, detail=f"ошибка загрузки {url}: {exc}")

    if not pages_html:
        raise HTTPException(status_code=404, detail=f"страницы не загружены: {url}")

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
