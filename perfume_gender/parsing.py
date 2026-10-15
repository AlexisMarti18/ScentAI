"""Parseo y normalizacion de acordes. Unica fuente de verdad para ETL y API."""
from __future__ import annotations

import re

# Sinonimos detectados en el dataset (se unifican al nombre canonico).
ACCORD_ALIASES = {"powder": "powdery"}

_WS = re.compile(r"\s+")


def normalize_accord(name: str) -> str:
    """'  Fresh  Spicy ' -> 'fresh spicy'; aplica sinonimos conocidos."""
    n = _WS.sub(" ", str(name).strip().lower())
    return ACCORD_ALIASES.get(n, n)


def parse_accords(raw: object) -> dict[str, float]:
    """Convierte 'woody:100|sweet:65' en {'woody': 100.0, 'sweet': 65.0}.

    Las intensidades quedan en la escala original 0-100 de Fragrantica.
    Devuelve {} si el valor es nulo o no tiene ningun par valido.
    """
    result: dict[str, float] = {}
    if raw is None or (isinstance(raw, float) and raw != raw):  # None o NaN
        return result
    for item in str(raw).split("|"):
        name, sep, value = item.rpartition(":")
        if not sep:
            continue
        try:
            intensity = float(value.strip())
        except ValueError:
            continue
        key = normalize_accord(name)
        if key:
            # Si un sinonimo aparece dos veces nos quedamos con la intensidad mayor.
            result[key] = max(result.get(key, 0.0), intensity)
    return result
