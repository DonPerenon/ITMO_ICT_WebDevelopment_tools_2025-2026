from __future__ import annotations

import threading
import time

TOTAL = 10_000_000_000_000
WORKERS = 8
CPU_LOAD_ITERATIONS = 25_000_000


def calculate_sum(start: int, end: int) -> int:
    partial = (end * (end + 1) - (start - 1) * start) // 2
    acc = 0
    for i in range(CPU_LOAD_ITERATIONS):
        acc += (i * 31) % 997
    return partial + acc - acc


def _worker(index: int, start: int, end: int, results: list[int]) -> None:
    results[index] = calculate_sum(start, end)


def main() -> None:
    chunk_size = TOTAL // WORKERS
    results = [0] * WORKERS
    threads: list[threading.Thread] = []

    started = time.perf_counter()
    for index in range(WORKERS):
        range_start = index * chunk_size + 1
        range_end = TOTAL if index == WORKERS - 1 else (index + 1) * chunk_size
        thread = threading.Thread(
            target=_worker,
            args=(index, range_start, range_end, results),
        )
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    total = sum(results)
    elapsed = time.perf_counter() - started

    expected = TOTAL * (TOTAL + 1) // 2
    print(f"подход: threading")
    print(f"воркеров: {WORKERS}")
    print(f"сумма: {total}")
    print(f"ожидаемая сумма: {expected}")
    print(f"совпадение: {str(total == expected).lower()}")
    print(f"время выполнения: {elapsed:.4f} с")


if __name__ == "__main__":
    main()
