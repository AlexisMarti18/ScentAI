"""Vocabulario de acordes y vectorizacion (acordes -> vector de intensidades 0-1)."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, Mapping

import numpy as np

from .parsing import normalize_accord


def build_vocab(accord_dicts: Iterable[Mapping[str, float]], min_count: int = 1) -> list[str]:
    """Vocabulario ordenado alfabeticamente con los acordes que aparecen >= min_count veces."""
    counts: dict[str, int] = {}
    for d in accord_dicts:
        for k in d:
            counts[k] = counts.get(k, 0) + 1
    return sorted(k for k, c in counts.items() if c >= min_count)


def rescale_to_max(accords: Mapping[str, float]) -> dict[str, float]:
    """Reescala para que el acorde mas fuerte valga 100, igual que en el dataset.

    En Fragrantica las intensidades son relativas: el acorde dominante es siempre 100.
    El modelo se entreno con esa convencion, asi que la entrada del usuario se
    normaliza de la misma forma.
    """
    top = max(accords.values(), default=0.0)
    if top <= 0:
        return {}
    return {k: v * 100.0 / top for k, v in accords.items()}


def vectorize(accords: Mapping[str, float], vocab: list[str]) -> np.ndarray:
    """Un perfume -> vector float32 de largo len(vocab) con intensidades en [0, 1]."""
    return to_matrix([accords], vocab)[0]


def to_matrix(accord_dicts: Iterable[Mapping[str, float]], vocab: list[str]) -> np.ndarray:
    """Lista de perfumes -> matriz (n, len(vocab)) float32 con intensidades en [0, 1].

    Los acordes fuera del vocabulario se ignoran.
    """
    index = {a: i for i, a in enumerate(vocab)}
    rows = list(accord_dicts)
    X = np.zeros((len(rows), len(vocab)), dtype=np.float32)
    for r, d in enumerate(rows):
        for name, value in d.items():
            j = index.get(normalize_accord(name))
            if j is not None:
                X[r, j] = value / 100.0
    return X


def save_vocab(vocab: list[str], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(vocab, ensure_ascii=False, indent=1), encoding="utf-8")


def load_vocab(path: Path) -> list[str]:
    return json.loads(path.read_text(encoding="utf-8"))
