# Лабораторная работа 2

**Тема:** потоки, процессы, асинхронность в Python  
**Студент:** Иванов Виктор, K3340  
**Срок сдачи:** 12 мая 2026

## Структура

```
lab2/
├── task1/   # Сумма чисел 1..10^13 (threading / multiprocessing / async)
└── task2/   # Парсинг цен металлопроката и сохранение в SQLite
```

## Быстрый старт

```bash
cd lab2
python3 -m venv .venv
source .venv/bin/activate
pip install -r task2/requirements.txt

# Задача 1
python task1/threading_sum.py
python task1/multiprocessing_sum.py
python task1/async_sum.py

# Задача 2
python task2/threading_parser.py
python task2/multiprocessing_parser.py
python task2/async_parser.py
```

## Теоретические материалы

- [Конспект по threading](https://github.com/ITMO-ICT-Technology-Group/ITMO_ICT_WebDevelopment_tools_2025-2026)
- [AsyncIO — краткое объяснение](https://www.youtube.com/watch?v=t5Bo1Je9EmE)
- [GIL в Python — Григорий Петров](https://www.youtube.com/watch?v=Obt-vMVWV0A)
- [Плейлист по asyncio — Олег Молчанов](https://www.youtube.com/playlist?list=PLow2V3t1JgdaNecagg9oF8ePQepg3sCpD)

Подробное описание реализаций — в `task1/README.md` и `task2/README.md`.
