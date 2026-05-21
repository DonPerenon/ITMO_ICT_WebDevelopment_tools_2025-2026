# Лабораторная работа №2 — Потоки. Процессы. Асинхронность

**Дисциплина:** Инструментальные средства веб-разработки  
**Тема:** threading, multiprocessing, asyncio в Python  
**Срок сдачи:** 12 мая 2026

## Цель работы

Понять отличия потоков и процессов, разобраться с асинхронностью в Python на практических задачах: CPU-bound вычисления и I/O-bound парсинг веб-страниц.

## Структура проекта

```
Lr2/lab2/
├── task1/          # сумма чисел 1..10¹³
│   ├── threading_sum.py
│   ├── multiprocessing_sum.py
│   ├── async_sum.py
│   └── run_benchmark.py
└── task2/          # парсинг каталогов металлопроката
    ├── parser_utils.py
    ├── db.py
    ├── threading_parser.py
    ├── multiprocessing_parser.py
    ├── async_parser.py
    └── run_benchmark.py
```

## Теоретические материалы

- [Конспект по threading](https://github.com/ITMO-ICT-Technology-Group/ITMO_ICT_WebDevelopment_tools_2025-2026)
- [AsyncIO — краткое объяснение](https://www.youtube.com/watch?v=t5Bo1Je9EmE)
- [GIL в Python — Григорий Петров](https://www.youtube.com/watch?v=Obt-vMVWV0A)
- [Плейлист по asyncio — Олег Молчанов](https://www.youtube.com/playlist?list=PLow2V3t1JgdaNecagg9oF8ePQepg3sCpD)

## Задания

| Задание | Описание |
| --- | --- |
| [Задача 1](task1.md) | Сумма чисел от 1 до 10¹³ — threading / multiprocessing / async |
| [Задача 2](task2.md) | Параллельный парсинг каталогов с сохранением в SQLite |

## Краткие выводы

**CPU-bound (задача 1):** threading проигрывает из-за GIL; multiprocessing и async с `ProcessPoolExecutor` дают ~5× ускорение.

**I/O-bound (задача 2):** все три подхода показывают близкое время при небольшом числе URL; async с `aiohttp` и асинхронной записью в БД (`aiosqlite`) — оптимален при большом числе одновременных запросов.

## Ссылки

- [Код ЛР2 на GitHub](https://github.com/DonPerenon/ITMO_ICT_WebDevelopment_tools_2025-2026/tree/main/students/k3340/Ivanov_Viktor/Lr2/lab2)
- [Лабораторная работа №1](../lr1/overview.md)
