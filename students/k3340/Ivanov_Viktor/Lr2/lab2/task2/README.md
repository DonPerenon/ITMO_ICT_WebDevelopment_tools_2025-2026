# Задача 2. Параллельный парсинг веб-страниц

Три программы парсят каталоги горячекатаного листа, извлекают **заголовок страницы** и **все позиции с ценами**, сохраняют данные в SQLite.

## Источники данных

| URL | Сайт |
| --- | --- |
| https://areal-metal.ru/catalog/list-goryachekatanyy | ТД «Ареал», Москва |
| https://szmetal.ru/catalog/list_goryachekatanyy/ | Севзаметалл, Санкт-Петербург |

## Файлы

| Файл | Назначение |
| --- | --- |
| `db.py` | Модели SQLModel и подключение к SQLite |
| `parser_utils.py` | Загрузка HTML, парсинг, список URL |
| `threading_parser.py` | Реализация через `ThreadPoolExecutor` |
| `multiprocessing_parser.py` | Реализация через `multiprocessing.Pool` |
| `async_parser.py` | Реализация через `asyncio` + `aiohttp` |
| `run_benchmark.py` | Последовательный запуск всех трёх парсеров |
| `requirements.txt` | Зависимости Python |

## База данных

Используется SQLite (`lab2_parser.db`) в стиле ЛР1 (SQLModel + SQLite, как в practice2/practice3).

### Таблицы

**`parsedpage`** — спарсенные страницы:

| Поле | Описание |
| --- | --- |
| `url` | Адрес страницы |
| `title` | Заголовок (`<title>`) |
| `fetched_at` | Время парсинга |

**`metalprice`** — позиции каталога с ценами:

| Поле | Описание |
| --- | --- |
| `page_id` | FK на `parsedpage` |
| `name` | Наименование листа |
| `size` | Толщина / размер |
| `steel_grade` | Марка стали |
| `characteristics` | ГОСТ / характеристики |
| `manufacturer` | Изготовитель (areal) |
| `warehouse` | Склад (szmetal) |
| `price_text` | Цена как на сайте |
| `price_value` | Числовая цена (руб.), `NULL` для «Договорная» |

## Функция `parse_and_save(url)`

В каждой программе:

1. Загружает HTML по URL.
2. Извлекает заголовок страницы.
3. Парсит все строки каталога с ценами (таблица на areal-metal.ru, div-блоки на szmetal.ru).
4. Сохраняет страницу и позиции в БД.
5. Выводит результат в консоль.

## Параллелизация

Список из 2 URL делится на 2 части — по одной на воркер. Каждый воркер обрабатывает свою часть независимо.

## Особенности подходов

### Threading

- HTTP-запросы — I/O-bound: пока один поток ждёт ответ сервера, другой может работать.
- GIL не мешает, потому что во время сетевого ожидания GIL освобождается.
- Простая модель для небольшого числа URL.

### Multiprocessing

- Каждый процесс делает свой HTTP-запрос и пишет в SQLite независимо.
- Накладные расходы на fork выше, чем у потоков, но для 2 URL разница минимальна.
- Масштабируется при росте числа страниц и тяжёлом пост-обработке HTML.

### Async (aiohttp)

- Один event loop, несколько одновременных HTTP-запросов без блокировки.
- Минимальные накладные расходы на создание «задач» compared to threads/processes.
- Оптимален при сотнях и тысячах URL.

## Замеры времени

Запуск на macOS, 2 URL, Python 3.13:

| Подход | Время, с | Позиций спарсено |
| --- | ---: | ---: |
| threading | 2.40 | 79 |
| multiprocessing | 2.37 | 79 |
| async (aiohttp) | 2.33 | 79 |

Распределение: **20 позиций** с areal-metal.ru + **59 позиций** с szmetal.ru.

## Анализ результатов

1. **Все три подхода показали близкое время (~2.3–2.4 с)** — узкое место это сетевая задержка (TTFB + загрузка HTML), а не CPU или GIL.

2. **Threading достаточен для I/O** — при 2 URL ускорение относительно последовательного парсинга (~4–5 с) примерно 2×, как и ожидалось.

3. **Multiprocessing не быстрее threading** на малом числе URL — overhead создания процессов съедает выигрыш. Имеет смысл при CPU-heavy обработке после загрузки.

4. **Async чуть быстрее** — меньше накладных расходов на переключение потоков/процессов; при 100+ URL разрыв будет заметнее.

5. **Для production-парсинга** обычно выбирают async (aiohttp/httpx) или threading с `requests` + `ThreadPoolExecutor`.

## Запуск

```bash
# из каталога lab2 с активированным venv
pip install -r task2/requirements.txt

python task2/threading_parser.py
python task2/multiprocessing_parser.py
python task2/async_parser.py
python task2/run_benchmark.py
```

## Пример вывода

```
[async] https://areal-metal.ru/catalog/list-goryachekatanyy
  Заголовок: Лист горячекатаный — низкая цена, купить лист горячекатаный в Москве
  Позиций с ценами: 20
```

## Проверка данных в БД

```bash
sqlite3 task2/lab2_parser.db "SELECT COUNT(*) FROM metalprice;"
sqlite3 task2/lab2_parser.db "SELECT name, price_text FROM metalprice LIMIT 5;"
```
