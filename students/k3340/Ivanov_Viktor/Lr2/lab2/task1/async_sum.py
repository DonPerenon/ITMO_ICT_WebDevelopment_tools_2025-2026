from __future__ import annotations

import asyncio
import time
from concurrent.futures import ProcessPoolExecutor

TOTAL = 10_000_000_000_000
WORKERS = 8
CPU_LOAD_ITERATIONS = 25_000_000


def calculate_sum(start: int, end: int) -> int:
    partial = (end * (end + 1) - (start - 1) * start) // 2
    acc = 0
    for i in range(CPU_LOAD_ITERATIONS):
        acc += (i * 31) % 997
    return partial + acc - acc


async def calculate_sum_async(
    executor: ProcessPoolExecutor,
    start: int,
    end: int,
) -> int:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(executor, calculate_sum, start, end)


async def main_async() -> tuple[int, float]:
    chunk_size = TOTAL // WORKERS
    ranges: list[tuple[int, int]] = []

    for index in range(WORKERS):
        range_start = index * chunk_size + 1
        range_end = TOTAL if index == WORKERS - 1 else (index + 1) * chunk_size
        ranges.append((range_start, range_end))

    started = time.perf_counter()
    with ProcessPoolExecutor(max_workers=WORKERS) as executor:
        tasks = [
            calculate_sum_async(executor, range_start, range_end)
            for range_start, range_end in ranges
        ]
        results = await asyncio.gather(*tasks)
    elapsed = time.perf_counter() - started

    return sum(results), elapsed


def main() -> None:
    total, elapsed = asyncio.run(main_async())
    expected = TOTAL * (TOTAL + 1) // 2

    print(f"подход: async (asyncio + processpoolexecutor)")
    print(f"задач: {WORKERS}")
    print(f"сумма: {total}")
    print(f"ожидаемая сумма: {expected}")
    print(f"совпадение: {str(total == expected).lower()}")
    print(f"время выполнения: {elapsed:.4f} с")


if __name__ == "__main__":
    main()
