# Задача 2. Параллельный парсинг веб-страниц

## Постановка

Три программы парсят каталоги горячекатаного листа, извлекают **заголовок страницы** и **все позиции с ценами**, сохраняют данные в SQLite.

Каждая программа содержит функцию `parse_and_save(url)`.

## Источники данных

| URL | Сайт | Пагинация |
| --- | --- | --- |
| [areal-metal.ru](https://areal-metal.ru/catalog/list-goryachekatanyy) | ТД «Ареал» | `?page=N`, ссылка «далее» |
| [szmetal.ru](https://szmetal.ru/catalog/list_goryachekatanyy/) | Севзаметалл | одна страница |
| [mc.ru](https://mc.ru/metalloprokat/stal_listovaya_g_k) | Металлсервис | `?count=30&page=N` |

Список из 3 URL делится между воркерами. Для каждого сайта обходятся **все страницы каталога**.

## Файлы

| Файл | Назначение |
| --- | --- |
| `db.py` | SQLModel-модели, sync и async движки SQLite |
| `parser_utils.py` | HTTP, парсинг, пагинация |
| `threading_parser.py` | `ThreadPoolExecutor` |
| `multiprocessing_parser.py` | `multiprocessing.Pool` |
| `async_parser.py` | `asyncio` + `aiohttp` + `aiosqlite` |
| `run_benchmark.py` | последовательный запуск всех парсеров |

## База данных

SQLite (`lab2_parser.db`), SQLModel — в стиле [ЛР1](../lr1/database.md).

### Таблица `parsedpage`

| Поле | Описание |
| --- | --- |
| `url` | адрес каталога |
| `title` | заголовок `<title>` |
| `fetched_at` | время парсинга |

### Таблица `metalprice`

| Поле | Описание |
| --- | --- |
| `page_id` | FK на `parsedpage` |
| `name` | наименование |
| `size` | толщина / размер |
| `steel_grade` | марка стали |
| `characteristics` | ГОСТ |
| `manufacturer` | изготовитель (areal) |
| `warehouse` | склад (szmetal, mc.ru) |
| `price_text` | цена как на сайте |
| `price_value` | число или `NULL` («договорная») |

## Особенности подходов

### Threading

HTTP-запросы — I/O-bound. Пока один поток ждёт ответ сервера, другой работает. Запись в БД — синхронная (`SQLModel` + `Session`).

### Multiprocessing

Каждый процесс загружает и парсит свой URL независимо. Выше overhead на создание процессов.

### Async

- HTTP через **aiohttp** (неблокирующие запросы)
- Запись в БД через **aiosqlite** и `AsyncSession` — полностью асинхронный пайплайн
- Оптимален при большом числе одновременных соединений

## Замеры времени

macOS, Python 3.13, 3 сайта (без полного обхода areal):

| Подход | Время, с | Позиций |
| --- | ---: | ---: |
| threading | 2.81 | 78+ |
| multiprocessing | 2.98 | 78+ |
| async | 2.80 | 78+ |

При **полной пагинации areal-metal.ru** (50+ страниц, 1000+ позиций) время выполнения значительно возрастает — узкое место смещается к количеству HTTP-запросов.

## Анализ

1. При малом числе URL все три подхода дают **близкое время** — ограничивает сеть, а не GIL.
2. **Threading достаточен** для I/O при нескольких URL.
3. **Multiprocessing** не быстрее threading на малых задачах из-за overhead процессов.
4. **Async** выигрывает при масштабировании: сотни URL, асинхронная БД без блокировки event loop.
5. **Пагинация** критична: без неё парсится только первая страница каталога.

## Запуск

```bash
cd Lr2/lab2
python3 -m venv .venv
source .venv/bin/activate
pip install -r task2/requirements.txt

python task2/threading_parser.py
python task2/multiprocessing_parser.py
python task2/async_parser.py
python task2/run_benchmark.py
```

## Проверка БД

```bash
sqlite3 task2/lab2_parser.db "SELECT COUNT(*) FROM metalprice;"
sqlite3 task2/lab2_parser.db "SELECT p.url, COUNT(m.id) FROM parsedpage p JOIN metalprice m ON m.page_id = p.id GROUP BY p.id;"
```
