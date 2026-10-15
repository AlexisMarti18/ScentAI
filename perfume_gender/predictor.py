"""Predictor: modelo entrenado + vocabulario, listo para servir desde la API."""
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


class InvalidAccordsError(ValueError):
    """La entrada tiene acordes desconocidos, vacios o demasiados."""


@dataclass
class Predictor:
    model: object
    vocab: list[str]
    metadata: dict

    @classmethod
    def load(cls, model_path: Path = config.MODEL_PATH, vocab_path: Path = config.VOCAB_PATH,
             metadata_path: Path = config.METADATA_PATH) -> "Predictor":
        for p in (model_path, vocab_path, metadata_path):
            if not Path(p).exists():
                raise FileNotFoundError(
                    f"Falta {p}. Ejecuta el pipeline (pipeline/03_train.py) o descarga el modelo del repositorio.")
        model = joblib.load(model_path)
        meta = json.loads(Path(metadata_path).read_text(encoding="utf-8"))
        return cls(model=model, vocab=load_vocab(vocab_path), metadata=meta)

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
    def _proba(self, accords: Mapping[str, float]) -> np.ndarray:
        return self.model.predict_proba(vectorize(accords, self.vocab).reshape(1, -1))[0]

    def predict(self, accords: Mapping[str, float], explain: bool = True) -> dict:
        cleaned = self.clean_input(accords)
        proba = self._proba(cleaned)
        classes = [str(c) for c in self.model.classes_]
        result = {
            "label": classes[int(np.argmax(proba))],
            "probabilities": {c: round(float(p), 4) for c, p in zip(classes, proba)},
            "accords_used": {k: round(v, 1) for k, v in cleaned.items()},
        }
        if explain:
            result["influences"] = self._influences(cleaned, proba, classes)
        return result

    def _influences(self, cleaned: dict[str, float], proba: np.ndarray, classes: list[str]) -> list[dict]:
        """Efecto de cada acorde: cuanto cambia la probabilidad de cada clase si se lo quita.

        Valor positivo = ese acorde empuja el resultado hacia esa clase.
        """
        out = []
        for name in cleaned:
            rest = {k: v for k, v in cleaned.items() if k != name}
            if not rest:
                continue
            delta = proba - self._proba(rescale_to_max(rest))
            effect = {c: round(float(d), 4) for c, d in zip(classes, delta)}
            out.append({"accord": name, "effect": effect,
                        "pushes_toward": max(effect, key=lambda c: effect[c])})
        out.sort(key=lambda i: -max(abs(v) for v in i["effect"].values()))
        return out
