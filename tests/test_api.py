import pytest
from fastapi.testclient import TestClient

from perfume_gender.predictor import InvalidAccordsError, Predictor


@pytest.fixture()
def client(monkeypatch, tiny_predictor):
    monkeypatch.setattr(Predictor, "load", classmethod(lambda cls, *a, **k: tiny_predictor))
    from app.backend.main import app

    with TestClient(app) as c:
        yield c


def test_health(client):
    assert client.get("/api/health").json() == {"status": "ok"}


def test_accords_endpoint(client):
    data = client.get("/api/accords").json()
    assert "woody" in data["accords"]
    assert data["max_accords"] == 8


def test_predict_ok(client):
    r = client.post("/api/predict", json={"accords": [
        {"name": "aromatic", "intensity": 100}, {"name": "woody", "intensity": 70}]})
    assert r.status_code == 200
    body = r.json()
    assert body["label"] in {"female", "male", "unisex"}
    assert abs(sum(body["probabilities"].values()) - 1) < 1e-3
    assert body["accords_used"]["aromatic"] == 100.0
    assert {i["accord"] for i in body["influences"]} == {"aromatic", "woody"}


def test_predict_rescales_relative_intensity(client):
    r = client.post("/api/predict", json={"accords": [{"name": "woody", "intensity": 40}]})
    assert r.json()["accords_used"] == {"woody": 100.0}


def test_predict_unknown_accord_is_422(client):
    r = client.post("/api/predict", json={"accords": [{"name": "inexistente", "intensity": 50}]})
    assert r.status_code == 422
    assert "inexistente" in r.json()["detail"]


def test_predict_validation_errors(client):
    assert client.post("/api/predict", json={"accords": []}).status_code == 422
    assert client.post("/api/predict", json={"accords": [{"name": "woody", "intensity": 0}]}).status_code == 422
    too_many = [{"name": f"a{i}", "intensity": 10} for i in range(9)]
    assert client.post("/api/predict", json={"accords": too_many}).status_code == 422


def test_predictor_rejects_empty(tiny_predictor):
    with pytest.raises(InvalidAccordsError):
        tiny_predictor.predict({})


def test_frontend_served(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "ScentAI" in r.text
