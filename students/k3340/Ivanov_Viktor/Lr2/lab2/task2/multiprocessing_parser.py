from __future__ import annotations

import multiprocessing as mp
import os
import time

from db import DB_PATH, MetalPrice, ParsedPage, get_session, init_db
from parser_utils import (
    URLS,
    extract_title,
    fetch_all_pages,
    parse_all_products,
    parse_price_value,
    split_urls,
)

WORKERS = 2


def parse_and_save(url: str) -> tuple[str, int]:
    pages_html = fetch_all_pages(url)
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

    print(f"[multiprocessing pid={os.getpid()}] {url}")
    print(f"  заголовок: {title.lower()}")
    print(f"  страниц каталога: {len(pages_html)}")
    print(f"  позиций с ценами: {len(products)}")
    return title, len(products)


def _parse_chunk(urls: list[str]) -> list[tuple[str, int]]:
    return [parse_and_save(url) for url in urls]


def main() -> None:
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    init_db()
    url_chunks = split_urls(URLS, WORKERS)

    started = time.perf_counter()
    with mp.Pool(processes=WORKERS) as pool:
        chunk_results = pool.map(_parse_chunk, url_chunks)

    elapsed = time.perf_counter() - started
    results = [item for chunk in chunk_results for item in chunk]
    total_items = sum(count for _, count in results)

    print("\nитог multiprocessing:")
    print(f"  сайтов: {len(results)}")
    print(f"  всего позиций: {total_items}")
    print(f"  время: {elapsed:.4f} с")


if __name__ == "__main__":
    main()
