"""Permite ejecutar `python pipeline/0X_*.py` desde la raiz importando `perfume_gender`."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Salida UTF-8 en consolas de Windows.
for stream in (sys.stdout, sys.stderr):
    try:
        stream.reconfigure(encoding="utf-8")
    except Exception:
        pass
