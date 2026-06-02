from __future__ import annotations

import asyncio
import os
import time

import aiohttp

from db import DB_PATH, MetalPrice, ParsedPage, get_async_session, init_db_async
from parser_utils import (
    URLS,
    USER_AGENT,
    extract_title,
    fetch_all_pages_async,
    parse_all_products,
    parse_price_value,
    split_urls,
)

WORKERS = 2
REQUEST_TIMEOUT = aiohttp.ClientTimeout(total=60)


async def parse_and_save(session: aiohttp.ClientSession, url: str) -> tuple[str, int]:
    pages_html = await fetch_all_pages_async(session, url)
    title = extract_title(pages_html[0])
    products = parse_all_products(pages_html, url)

    async with get_async_session() as db_session:
        page = ParsedPage(url=url, title=title)
        db_session.add(page)
        await db_session.commit()
        await db_session.refresh(page)

        for product in products:
            db_session.add(
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
        await db_session.commit()

    print(f"[async] {url}")
    print(f"  заголовок: {title.lower()}")
    print(f"  страниц каталога: {len(pages_html)}")
    print(f"  позиций с ценами: {len(products)}")
    return title, len(products)


async def _parse_chunk(
    session: aiohttp.ClientSession,
    urls: list[str],
) -> list[tuple[str, int]]:
    tasks = [parse_and_save(session, url) for url in urls]
    return await asyncio.gather(*tasks)


async def main_async() -> tuple[list[tuple[str, int]], float]:
    url_chunks = split_urls(URLS, WORKERS)
    started = time.perf_counter()

    headers = {"User-Agent": USER_AGENT, "Accept-Language": "ru-RU,ru;q=0.9"}
    async with aiohttp.ClientSession(headers=headers) as session:
        chunk_results = await asyncio.gather(
            *[_parse_chunk(session, chunk) for chunk in url_chunks]
        )

    elapsed = time.perf_counter() - started
    results = [item for chunk in chunk_results for item in chunk]
    return results, elapsed


async def run() -> None:
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    await init_db_async()
    results, elapsed = await main_async()
    total_items = sum(count for _, count in results)

    print("\nитог async:")
    print(f"  сайтов: {len(results)}")
    print(f"  всего позиций: {total_items}")
    print(f"  время: {elapsed:.4f} с")


def main() -> None:
    asyncio.run(run())


if __name__ == "__main__":
    main()
