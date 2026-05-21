from __future__ import annotations

import asyncio
import multiprocessing as mp
import subprocess
import sys
import threading
import time
from pathlib import Path

TOTAL = 10_000_000_000_000
WORKERS = 8
CPU_LOAD_ITERATIONS = 25_000_000


def calculate_sum(start: int, end: int) -> int:
    partial = (end * (end + 1) - (start - 1) * start) // 2
    acc = 0
    for i in range(CPU_LOAD_ITERATIONS):
        acc += (i * 31) % 997
    return partial + acc - acc


def run_threading() -> float:
    chunk_size = TOTAL // WORKERS
    results = [0] * WORKERS
    threads: list[threading.Thread] = []

    started = time.perf_counter()
    for index in range(WORKERS):
        range_start = index * chunk_size + 1
        range_end = TOTAL if index == WORKERS - 1 else (index + 1) * chunk_size

        def worker(idx: int, start: int, end: int) -> None:
            results[idx] = calculate_sum(start, end)

        thread = threading.Thread(target=worker, args=(index, range_start, range_end))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()
    return time.perf_counter() - started


def run_multiprocessing() -> float:
    chunk_size = TOTAL // WORKERS
    ranges = [
        (
            index * chunk_size + 1,
            TOTAL if index == WORKERS - 1 else (index + 1) * chunk_size,
        )
        for index in range(WORKERS)
    ]

    started = time.perf_counter()
    with mp.Pool(processes=WORKERS) as pool:
        pool.starmap(calculate_sum, ranges)
    return time.perf_counter() - started


async def run_async() -> float:
    from concurrent.futures import ProcessPoolExecutor

    chunk_size = TOTAL // WORKERS
    ranges = [
        (
            index * chunk_size + 1,
            TOTAL if index == WORKERS - 1 else (index + 1) * chunk_size,
        )
        for index in range(WORKERS)
    ]

    loop = asyncio.get_running_loop()
    started = time.perf_counter()
    with ProcessPoolExecutor(max_workers=WORKERS) as executor:
        tasks = [
            loop.run_in_executor(executor, calculate_sum, start, end)
            for start, end in ranges
        ]
        await asyncio.gather(*tasks)
    return time.perf_counter() - started


def run_script(script_name: str) -> float:
    script_path = Path(__file__).with_name(script_name)
    started = time.perf_counter()
    subprocess.run([sys.executable, str(script_path)], check=True, capture_output=True, text=True)
    return time.perf_counter() - started


def main() -> None:
    print("бенчмарк задачи 1 (локальный in-process замер)\n")

    threading_time = run_threading()
    multiprocessing_time = run_multiprocessing()
    async_time = asyncio.run(run_async())

    rows = [
        ("threading", threading_time),
        ("multiprocessing", multiprocessing_time),
        ("async", async_time),
    ]

    print("| подход | время, с |")
    print("| --- | ---: |")
    for name, elapsed in rows:
        print(f"| {name} | {elapsed:.4f} |")


if __name__ == "__main__":
    main()
