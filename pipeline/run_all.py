"""Corre el pipeline completo (EDA -> ETL -> experimentos -> entrenamiento -> evaluacion).

Uso: python pipeline/run_all.py        (requiere data/raw/perfumes.csv)
"""
import _bootstrap  # noqa: F401

import subprocess
import sys
import time
from pathlib import Path

STEPS = ["01_eda.py", "02_etl.py", "03_experiments.py", "04_train.py", "05_evaluate.py"]


def main() -> None:
    here = Path(__file__).resolve().parent
    for step in STEPS:
        print(f"\n=== {step} ===", flush=True)
        t = time.time()
        subprocess.run([sys.executable, str(here / step)], check=True)
        print(f"({time.time() - t:.0f}s)", flush=True)


if __name__ == "__main__":
    main()
