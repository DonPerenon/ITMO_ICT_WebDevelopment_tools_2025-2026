# Задача 1. Threading, multiprocessing и async

## Постановка

Написать три программы, считающие сумму всех целых чисел от **1 до 10 000 000 000 000**, разбив вычисления на 8 параллельных подзадач.

Каждая программа содержит функцию `calculate_sum(start, end)`.

## Математическая проверка

Сумма арифметической прогрессии:

`S = N × (N + 1) / 2 = 50 000 000 000 005 000 000 000 000`

Прямой перебор 10¹³ элементов невыполним за разумное время, поэтому сумма диапазона считается по формуле, а для наглядного сравнения подходов добавлена CPU-нагрузка (цикл из 25 млн итераций в каждом воркере).

## Файлы

| Файл | Подход |
| --- | --- |
| `threading_sum.py` | `threading.Thread` |
| `multiprocessing_sum.py` | `multiprocessing.Pool` |
| `async_sum.py` | `asyncio` + `ProcessPoolExecutor` |
| `run_benchmark.py` | сводный бенчмарк |

## Особенности реализаций

### Threading

Потоки делят один интерпретатор Python. Из-за **GIL** CPU-код не выполняется параллельно на нескольких ядрах.

### Multiprocessing

Каждый воркер — отдельный процесс со своим GIL. Реальный параллелизм на нескольких ядрах CPU.

### Async

Event loop координирует задачи. Для CPU-bound нагрузки вычисления вынесены в `ProcessPoolExecutor`, иначе async не дал бы ускорения относительно threading.

## Замеры времени

macOS, Python 3.13, 8 воркеров:

| Подход | Время, с | Ускорение к threading |
| --- | ---: | ---: |
| threading | 6.44 | 1.00× |
| multiprocessing | 1.23 | 5.16× |
| async + ProcessPoolExecutor | 1.23 | 5.18× |

## Анализ

1. **Threading самый медленный** — GIL не даёт параллельно выполнять CPU-код.
2. **Multiprocessing и async с пулом процессов** показали схожий результат (~1.2 с).
3. Для **CPU-bound** задач выбирают `multiprocessing` или `ProcessPoolExecutor`.
4. Для **I/O-bound** (сеть, диск) GIL не мешает — эффективны threading и asyncio.

## Запуск

```bash
cd Lr2/lab2
python task1/threading_sum.py
python task1/multiprocessing_sum.py
python task1/async_sum.py
python task1/run_benchmark.py
```
