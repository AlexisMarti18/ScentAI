"""Carga y limpieza del dataset crudo de Fragrantica (Kaggle)."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from .config import CLASSES, DATA_RAW
from .parsing import parse_accords

RAW_COLUMNS = [
    "id", "name", "brand", "gender", "vote_count", "accords",
    "notes_top", "notes_middle", "notes_base", "notes_flat",
]


def load_raw(path: Path = DATA_RAW) -> pd.DataFrame:
    if not Path(path).exists():
        raise FileNotFoundError(
            f"No se encontro {path}. Descarga perfumes.csv de Kaggle y copialo ahi "
            "(ver data/raw/README.md)."
        )
    return pd.read_csv(path, usecols=RAW_COLUMNS, low_memory=False)


def fingerprint(accords: dict[str, float]) -> str:
    """Huella canonica de un perfil de acordes (dos perfumes iguales -> misma huella)."""
    return "|".join(f"{k}:{v:g}" for k, v in sorted(accords.items()))


def clean(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Limpieza del dataset. Devuelve (dataframe limpio, estadisticas para el reporte).

    Pasos:
      1. Descartar perfumes sin acordes (o con una cadena sin pares validos).
      2. Descartar etiquetas de genero fuera de {female, male, unisex}.
      3. Deduplicar perfiles de acordes identicos. Si el mismo perfil aparece con
         generos distintos, se conserva la etiqueta con mas peso (suma de
         vote_count + 1), es decir la que mas gente respalda.
    """
    stats: dict = {"raw_rows": len(df), "raw_class_counts": df["gender"].value_counts().to_dict()}

    df = df.copy()
    stats["no_accords"] = int(df["accords"].isna().sum())
    df = df.dropna(subset=["accords"])

    df["accords_dict"] = df["accords"].map(parse_accords)
    empty = df["accords_dict"].map(len) == 0
    stats["empty_after_parse"] = int(empty.sum())
    df = df[~empty]

    bad_label = ~df["gender"].isin(CLASSES)
    stats["bad_gender"] = int(bad_label.sum())
    df = df[~bad_label]
    stats["rows_before_dedup"] = len(df)
    stats["class_counts_before_dedup"] = df["gender"].value_counts().to_dict()

    df["fp"] = df["accords_dict"].map(fingerprint)
    df["vote_count"] = df["vote_count"].fillna(0)
    df["weight"] = df["vote_count"] + 1

    weights = df.groupby(["fp", "gender"])["weight"].sum().unstack(fill_value=0)
    winner = weights.idxmax(axis=1)
    n_labels = (weights > 0).sum(axis=1)
    stats["fingerprints"] = int(len(weights))
    stats["conflicting_fingerprints"] = int((n_labels > 1).sum())
    stats["rows_in_conflicting_fingerprints"] = int(df["fp"].isin(n_labels[n_labels > 1].index).sum())

    keep = df[df["gender"] == df["fp"].map(winner)]
    keep = keep.sort_values("vote_count", ascending=False).drop_duplicates("fp")
    keep = keep.sort_index().reset_index(drop=True)

    stats["duplicates_removed"] = stats["rows_before_dedup"] - len(keep)
    stats["final_rows"] = len(keep)
    stats["final_class_counts"] = keep["gender"].value_counts().to_dict()
    return keep, stats
