from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

SCRIPTS = [
    ("threading", "threading_parser.py"),
    ("multiprocessing", "multiprocessing_parser.py"),
    ("async", "async_parser.py"),
]


def run_parser(name: str, script: str) -> float:
    script_path = Path(__file__).with_name(script)
    db_path = Path(__file__).with_name("lab2_parser.db")
    if db_path.exists():
        db_path.unlink()

    started = time.perf_counter()
    result = subprocess.run(
        [sys.executable, str(script_path)],
        capture_output=True,
        text=True,
        check=False,
    )
    elapsed = time.perf_counter() - started

    print(f"\n=== {name} ===")
    if result.stdout:
        print(result.stdout.lower())
    if result.returncode != 0:
        print(result.stderr.lower())
        raise RuntimeError(f"скрипт {script} завершился с кодом {result.returncode}")

    return elapsed


def main() -> None:
    rows: list[tuple[str, float]] = []
    for name, script in SCRIPTS:
        rows.append((name, run_parser(name, script)))

    print("\n| подход | время, с |")
    print("| --- | ---: |")
    for name, elapsed in rows:
        print(f"| {name} | {elapsed:.4f} |")


if __name__ == "__main__":
    main()
