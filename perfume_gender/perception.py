"""Indice de masculinidad percibida a partir de los votos `perceived_*` de Fragrantica.

Fuente unica para el pipeline y la API. Los votos `perceived_*` se usan SOLO para
construir el objetivo (indice), nunca como variables predictoras.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:  # pandas solo se necesita en el pipeline, no para servir la API
    import pandas as pd

# Peso de cada tipo de voto en el espectro: 0 = femenino, 1 = masculino.
PESOS = {
    "perceived_female": 0.0,
    "perceived_female_leaning": 0.25,
    "perceived_unisex": 0.5,
    "perceived_male_leaning": 0.75,
    "perceived_male": 1.0,
}
PERCEIVED_COLUMNS = list(PESOS)

# Limites de las zonas: < 0,33 femenino · 0,33-0,67 unisex · > 0,67 masculino.
ZONE_LIMITS = (0.33, 0.67)
VOTE_CAP = 100


def perception_votes(votes: pd.DataFrame) -> pd.Series:
    """Total de votos de percepcion de cada perfume."""
    return votes[PERCEIVED_COLUMNS].sum(axis=1)


def perception_index(votes: pd.DataFrame) -> pd.Series:
    """Indice 0-1 (0 = femenino, 1 = masculino): promedio de los pesos ponderado por votos.

    Devuelve NaN si el perfume no tiene votos de percepcion.
    """
    total = perception_votes(votes)
    score = sum(votes[c] * w for c, w in PESOS.items())
    return (score / total).where(total > 0)


def zone(index: np.ndarray | float) -> np.ndarray:
    """Indice -> 'female' / 'unisex' / 'male' segun las zonas del espectro."""
    index = np.asarray(index, dtype=float)
    return np.where(index < ZONE_LIMITS[0], "female", np.where(index > ZONE_LIMITS[1], "male", "unisex"))


def zone_center(name: str) -> float:
    """Punto medio de una zona ('female', 'unisex' o 'male'); sirve como objetivo de las sugerencias."""
    lo, hi = ZONE_LIMITS
    centers = {"female": lo / 2, "unisex": (lo + hi) / 2, "male": (hi + 1) / 2}
    if name not in centers:
        raise ValueError(f"Zona desconocida: {name!r} (usar female, unisex o male)")
    return centers[name]


def vote_weight(votes: np.ndarray, cap: int = VOTE_CAP) -> np.ndarray:
    """Peso de entrenamiento: raiz de los votos con tope (mas votos = etiqueta mas confiable)."""
    return np.sqrt(np.minimum(np.asarray(votes, dtype=float), cap))
