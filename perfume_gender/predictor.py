"""Predictor: modelos entrenados + vocabulario, listos para servir desde la API.

  * Modelo principal (regresor): posicion en el espectro femenino (0) - masculino (1).
  * Clasificador de la etiqueta `gender`: probabilidades por clase, lectura masculino vs.
    femenino (ignora unisex) y frecuencia base ("lift").
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

import joblib
import numpy as np

from . import config
from .features import load_vocab, rescale_to_max, vectorize
from .parsing import normalize_accord
from .perception import zone

NEUTRAL_EFFECT = 0.005  # por debajo de este cambio de indice un acorde se considera neutro


class InvalidAccordsError(ValueError):
    """La entrada tiene acordes desconocidos, vacios o demasiados."""


def male_vs_female(p_female: float, p_male: float) -> dict[str, float]:
    """Reparte 100 % entre femenino y masculino ignorando unisex. Si ambas son 0 -> 50/50."""
    total = p_female + p_male
    if total <= 0:
        return {"female": 0.5, "male": 0.5}
    return {"female": p_female / total, "male": p_male / total}


def lift(probabilities: Mapping[str, float], priors: Mapping[str, float]) -> dict[str, float]:
    """Probabilidad de cada clase dividida por su frecuencia base (1 = igual al promedio)."""
    return {c: p / priors[c] if priors.get(c) else 0.0 for c, p in probabilities.items()}


@dataclass
class Predictor:
    classifier: object
    index_model: object
    vocab: list[str]
    metadata: dict

    @classmethod
    def load(cls, model_path: Path = config.MODEL_PATH, index_path: Path = config.INDEX_MODEL_PATH,
             vocab_path: Path = config.VOCAB_PATH, metadata_path: Path = config.METADATA_PATH) -> "Predictor":
        for p in (model_path, index_path, vocab_path, metadata_path):
            if not Path(p).exists():
                raise FileNotFoundError(
                    f"Falta {p}. Ejecuta el pipeline (python pipeline/run_all.py) o usa los modelos del repositorio.")
        return cls(classifier=joblib.load(model_path), index_model=joblib.load(index_path),
                   vocab=load_vocab(vocab_path),
                   metadata=json.loads(Path(metadata_path).read_text(encoding="utf-8")))

    # ------------------------------------------------------------------ entrada
    def clean_input(self, accords: Mapping[str, float]) -> dict[str, float]:
        """Normaliza nombres, valida y reescala para que el acorde principal valga 100."""
        cleaned: dict[str, float] = {}
        for name, value in accords.items():
            key = normalize_accord(name)
            cleaned[key] = max(cleaned.get(key, 0.0), float(value))
        cleaned = {k: v for k, v in cleaned.items() if v > 0}
        if not cleaned:
            raise InvalidAccordsError("Ingresa al menos un acorde con intensidad mayor a 0.")
        if len(cleaned) > config.MAX_ACCORDS:
            raise InvalidAccordsError(
                f"Maximo {config.MAX_ACCORDS} acordes (el dataset usa los 8 principales de cada perfume).")
        unknown = sorted(set(cleaned) - set(self.vocab))
        if unknown:
            raise InvalidAccordsError(f"Acordes desconocidos: {', '.join(unknown)}")
        return rescale_to_max(cleaned)

    # --------------------------------------------------------------- prediccion
    def _x(self, accords: Mapping[str, float]) -> np.ndarray:
        return vectorize(accords, self.vocab).reshape(1, -1)

    def _index(self, accords: Mapping[str, float]) -> float:
        return float(np.clip(self.index_model.predict(self._x(accords))[0], 0.0, 1.0))

    def predict(self, accords: Mapping[str, float], explain: bool = True) -> dict:
        cleaned = self.clean_input(accords)
        index = self._index(cleaned)

        proba = self.classifier.predict_proba(self._x(cleaned))[0]
        classes = [str(c) for c in self.classifier.classes_]
        probs = {c: float(p) for c, p in zip(classes, proba)}
        priors = self.metadata.get("class_priors") or {c: 1 / len(classes) for c in classes}

        result = {
            "index": round(index, 4),
            "zone": str(zone(index)),
            "male_vs_female": {k: round(v, 4) for k, v in male_vs_female(probs["female"], probs["male"]).items()},
            "class_probabilities": {c: round(p, 4) for c, p in probs.items()},
            "lift": {c: round(v, 3) for c, v in lift(probs, priors).items()},
            "accords_used": {k: round(v, 1) for k, v in cleaned.items()},
        }
        if explain:
            result["influences"] = self._influences(cleaned, index)
        return result

    def _influences(self, cleaned: dict[str, float], index: float) -> list[dict]:
        """Cambio del indice si se quita cada acorde. Positivo = ese acorde empuja hacia masculino."""
        out = []
        for name in cleaned:
            rest = {k: v for k, v in cleaned.items() if k != name}
            if not rest:
                continue
            effect = index - self._index(rescale_to_max(rest))
            toward = "neutral" if abs(effect) < NEUTRAL_EFFECT else ("male" if effect > 0 else "female")
            out.append({"accord": name, "index_effect": round(effect, 4), "pushes_toward": toward})
        out.sort(key=lambda i: -abs(i["index_effect"]))
        return out
