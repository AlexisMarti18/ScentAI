"""API del predictor de genero. Levantar con:  uvicorn app.backend.main:app"""
from __future__ import annotations

import json
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from perfume_gender import config
from perfume_gender.predictor import InvalidAccordsError, InvalidTargetError, Predictor

from .schemas import PredictRequest, PredictResponse, SuggestRequest, SuggestResponse

log = logging.getLogger("perfume_gender")
FRONTEND_DIR = Path(__file__).resolve().parents[1] / "frontend"


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        app.state.predictor = Predictor.load()
        log.info("Modelo cargado: %s", app.state.predictor.metadata.get("model_name"))
    except FileNotFoundError as exc:  # la app arranca igual y avisa en /api/health
        app.state.predictor = None
        app.state.load_error = str(exc)
        log.warning("%s", exc)
    yield


app = FastAPI(
    title="Predictor de genero de perfumes",
    description="Dado un perfil de acordes (con intensidad) ubica el perfume en el espectro "
                "femenino - masculino (indice 0-1) y devuelve ademas las probabilidades por clase.",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"^http://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


def get_predictor() -> Predictor:
    predictor = getattr(app.state, "predictor", None)
    if predictor is None:
        raise HTTPException(503, "Modelo no disponible. Ejecuta el pipeline o descarga models/model.joblib.")
    return predictor


@app.get("/api/health")
def health():
    ok = getattr(app.state, "predictor", None) is not None
    return {"status": "ok" if ok else "model_missing"}


@app.get("/api/accords")
def accords():
    p = get_predictor()
    return {"accords": p.vocab, "max_accords": config.MAX_ACCORDS}


@app.post("/api/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    p = get_predictor()
    try:
        return p.predict({a.name: a.intensity for a in req.accords})
    except InvalidAccordsError as exc:
        raise HTTPException(422, str(exc)) from exc


@app.post("/api/suggest", response_model=SuggestResponse)
def suggest(req: SuggestRequest):
    """Cambios simples (agregar, quitar, subir o bajar un acorde) que acercan el indice al objetivo."""
    p = get_predictor()
    target = req.target if req.target is not None else req.target_index
    try:
        return p.suggest({a.name: a.intensity for a in req.accords}, target)
    except (InvalidAccordsError, InvalidTargetError) as exc:
        raise HTTPException(422, str(exc)) from exc


@app.get("/api/model/info")
def model_info():
    """Metadatos del modelo y resultados del pipeline (leidos de reports/, nada hardcodeado)."""
    p = get_predictor()
    info = {"metadata": p.metadata}
    for key, fname in (("classifier_metrics", "metrics.json"), ("index_metrics", "index_metrics.json"),
                       ("experiments", "experiments.json"), ("vote_weights", "vote_weights.json"),
                       ("eda", "eda.json")):
        path = config.REPORTS_DIR / fname
        if path.exists():
            info[key] = json.loads(path.read_text(encoding="utf-8"))
    return info


app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
