from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

import aiohttp
import requests
from bs4 import BeautifulSoup

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
)
REQUEST_TIMEOUT = 60
MC_PAGE_SIZE = 30

URLS = [
    "https://areal-metal.ru/catalog/list-goryachekatanyy",
    "https://szmetal.ru/catalog/list_goryachekatanyy/",
    "https://mc.ru/metalloprokat/stal_listovaya_g_k",
]


@dataclass
class ParsedProduct:
    name: str
    kind: str | None = None
    size: str | None = None
    steel_grade: str | None = None
    characteristics: str | None = None
    manufacturer: str | None = None
    warehouse: str | None = None
    price_text: str = ""


def _build_page_url(base_url: str, page: int, extra_params: dict[str, str] | None = None) -> str:
    parsed = urlparse(base_url)
    query = parse_qs(parsed.query)
    if page > 1:
        query["page"] = [str(page)]
    elif "page" in query:
        del query["page"]
    if extra_params:
        for key, value in extra_params.items():
            query[key] = [value]
    encoded = urlencode({key: values[0] for key, values in query.items()})
    return urlunparse(parsed._replace(query=encoded))


def fetch_html(url: str) -> str:
    response = requests.get(
        url,
        headers={"User-Agent": USER_AGENT, "Accept-Language": "ru-RU,ru;q=0.9"},
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    response.encoding = response.apparent_encoding or "utf-8"
    return response.text


async def fetch_html_async(session: aiohttp.ClientSession, url: str) -> str:
    timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
    async with session.get(url, timeout=timeout) as response:
        response.raise_for_status()
        return await response.text()


def extract_title(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    if soup.title and soup.title.string:
        return soup.title.string.strip()
    heading = soup.find("h1")
    return heading.get_text(strip=True) if heading else ""


def parse_price_value(price_text: str) -> float | None:
    normalized = price_text.lower().replace("\xa0", " ").strip()
    if "договор" in normalized:
        return None
    match = re.search(r"([\d\s]+)", normalized)
    if not match:
        return None
    digits = match.group(1).replace(" ", "")
    return float(digits) if digits else None


def _site_host(url: str) -> str:
    return urlparse(url).netloc


def parse_products(html: str, url: str) -> list[ParsedProduct]:
    host = _site_host(url)
    if "areal-metal.ru" in host:
        return _parse_areal(html)
    if "szmetal.ru" in host:
        return _parse_szmetal(html)
    if "mc.ru" in host:
        return _parse_mc(html)
    raise ValueError(f"неподдерживаемый url: {url}")


def parse_all_products(pages_html: list[str], url: str) -> list[ParsedProduct]:
    products: list[ParsedProduct] = []
    seen: set[str] = set()
    for html in pages_html:
        for product in parse_products(html, url):
            if product.name in seen:
                continue
            seen.add(product.name)
            products.append(product)
    return products


def fetch_all_pages(url: str) -> list[str]:
    host = _site_host(url)
    if "areal-metal.ru" in host:
        return _fetch_areal_pages(url)
    if "szmetal.ru" in host:
        return [fetch_html(url)]
    if "mc.ru" in host:
        return _fetch_mc_pages(url)
    raise ValueError(f"неподдерживаемый url: {url}")


async def fetch_all_pages_async(session: aiohttp.ClientSession, url: str) -> list[str]:
    host = _site_host(url)
    if "areal-metal.ru" in host:
        return await _fetch_areal_pages_async(session, url)
    if "szmetal.ru" in host:
        return [await fetch_html_async(session, url)]
    if "mc.ru" in host:
        return await _fetch_mc_pages_async(session, url)
    raise ValueError(f"неподдерживаемый url: {url}")


def _fetch_areal_pages(base_url: str) -> list[str]:
    pages_html: list[str] = []
    page = 1
    while True:
        page_url = base_url if page == 1 else _build_page_url(base_url, page)
        html = fetch_html(page_url)
        if not _parse_areal(html):
            break
        pages_html.append(html)
        soup = BeautifulSoup(html, "html.parser")
        if not soup.select_one("a.ditto_next_link"):
            break
        page += 1
    return pages_html


async def _fetch_areal_pages_async(session: aiohttp.ClientSession, base_url: str) -> list[str]:
    pages_html: list[str] = []
    page = 1
    while True:
        page_url = base_url if page == 1 else _build_page_url(base_url, page)
        html = await fetch_html_async(session, page_url)
        if not _parse_areal(html):
            break
        pages_html.append(html)
        soup = BeautifulSoup(html, "html.parser")
        if not soup.select_one("a.ditto_next_link"):
            break
        page += 1
    return pages_html


def _fetch_mc_pages(base_url: str) -> list[str]:
    pages_html: list[str] = []
    page = 1
    extra = {"count": str(MC_PAGE_SIZE)}
    while True:
        page_url = _build_page_url(base_url, page, extra)
        html = fetch_html(page_url)
        if not _parse_mc(html):
            break
        pages_html.append(html)
        page += 1
    return pages_html


async def _fetch_mc_pages_async(session: aiohttp.ClientSession, base_url: str) -> list[str]:
    pages_html: list[str] = []
    page = 1
    extra = {"count": str(MC_PAGE_SIZE)}
    while True:
        page_url = _build_page_url(base_url, page, extra)
        html = await fetch_html_async(session, page_url)
        if not _parse_mc(html):
            break
        pages_html.append(html)
        page += 1
    return pages_html


def _parse_areal(html: str) -> list[ParsedProduct]:
    soup = BeautifulSoup(html, "html.parser")
    products: list[ParsedProduct] = []

    rows = soup.select('#prodtbody tbody tr[itemtype="http://schema.org/Product"]')
    for row in rows:
        cells = row.find_all("td")
        if len(cells) < 7:
            continue

        name_node = cells[0].find("span", attrs={"itemprop": "name"})
        name = name_node.get_text(strip=True) if name_node else cells[0].get_text(strip=True)

        price_meta = cells[6].find("meta", attrs={"itemprop": "price"})
        price_text = (
            price_meta.get("content", "").strip()
            if price_meta
            else cells[6].get_text(" ", strip=True)
        )

        products.append(
            ParsedProduct(
                name=name,
                kind=cells[1].get_text(strip=True),
                size=cells[2].get_text(strip=True),
                steel_grade=cells[3].get_text(strip=True),
                characteristics=cells[4].get_text(strip=True),
                manufacturer=cells[5].get_text(strip=True),
                price_text=price_text,
            )
        )

    return products


def _parse_szmetal(html: str) -> list[ParsedProduct]:
    soup = BeautifulSoup(html, "html.parser")
    products: list[ParsedProduct] = []

    rows = soup.select("div.catalog-table__row-tr.catalog-table__row")
    for row in rows:
        title_col = row.select_one(".catalog-table__col-title")
        if not title_col:
            continue

        sub = title_col.select_one(".catalog-table__col-title_sub")
        gost = sub.get_text(strip=True) if sub else None
        if sub:
            sub.extract()
        name = title_col.get_text(" ", strip=True)

        warehouse_node = row.select_one(".catalog-table__col-stock")
        warehouse = warehouse_node.get_text(" ", strip=True) if warehouse_node else None

        price_node = None
        for col in row.select(".catalog-table__col"):
            strong = col.find("strong")
            if strong and "руб" in strong.get_text():
                price_node = strong
                break
        price_text = price_node.get_text(" ", strip=True) if price_node else "нет цены"

        products.append(
            ParsedProduct(
                name=name,
                characteristics=gost,
                warehouse=warehouse,
                price_text=price_text,
            )
        )

    return products


def _parse_mc(html: str) -> list[ParsedProduct]:
    soup = BeautifulSoup(html, "html.parser")
    products: list[ParsedProduct] = []

    rows = soup.select("tr.catalogItem")
    for row in rows:
        cells = row.find_all("td")
        if not cells:
            continue

        link = cells[0].find("a")
        name = link.get_text(strip=True) if link else cells[0].get_text(strip=True)
        if not name:
            continue

        price_text = ""
        for cell in reversed(cells):
            text = cell.get_text(" ", strip=True)
            if "₽" in text or "руб" in text.lower():
                price_text = text
                break
        if not price_text:
            continue

        products.append(
            ParsedProduct(
                name=name,
                size=cells[1].get_text(strip=True) if len(cells) > 1 else None,
                steel_grade=cells[2].get_text(strip=True) if len(cells) > 2 else None,
                warehouse=cells[3].get_text(strip=True) if len(cells) > 3 else None,
                price_text=price_text,
            )
        )

    return products


def split_urls(urls: Iterable[str], parts: int) -> list[list[str]]:
    url_list = list(urls)
    if not url_list:
        return []
    chunk_size = max(1, (len(url_list) + parts - 1) // parts)
    return [url_list[index : index + chunk_size] for index in range(0, len(url_list), chunk_size)]
