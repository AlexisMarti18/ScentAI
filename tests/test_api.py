import pytest
from fastapi.testclient import TestClient

from perfume_gender.predictor import Predictor


@pytest.fixture()
def client(monkeypatch, tiny_predictor):
    monkeypatch.setattr(Predictor, "load", classmethod(lambda cls, *a, **k: tiny_predictor))
    from app.backend.main import app

    with TestClient(app) as c:
        yield c


def _post(client, accords):
    return client.post("/api/predict", json={"accords": [{"name": n, "intensity": v} for n, v in accords]})


def test_health(client):
    assert client.get("/api/health").json() == {"status": "ok"}


def test_accords_endpoint(client):
    data = client.get("/api/accords").json()
    assert "woody" in data["accords"]
    assert data["max_accords"] == 8


def test_predict_new_schema(client):
    r = _post(client, [("aromatic", 100), ("woody", 70)])
    assert r.status_code == 200
    body = r.json()
    assert set(body) == {"index", "zone", "male_vs_female", "class_probabilities", "lift",
                         "accords_used", "influences"}
    assert 0 <= body["index"] <= 1
    assert body["zone"] in {"female", "unisex", "male"}
    assert abs(sum(body["class_probabilities"].values()) - 1) < 1e-3
    assert abs(sum(body["male_vs_female"].values()) - 1) < 1e-3
    assert set(body["lift"]) == {"female", "male", "unisex"}
    assert {i["accord"] for i in body["influences"]} == {"aromatic", "woody"}


def test_masculine_profile_lands_on_masculine_side(client):
    masc = _post(client, [("aromatic", 100), ("woody", 90), ("fresh spicy", 80)]).json()
    fem = _post(client, [("floral", 100), ("sweet", 90), ("powdery", 80)]).json()
    assert masc["index"] > 0.6 > 0.4 > fem["index"]
    assert masc["male_vs_female"]["male"] > 0.5 > fem["male_vs_female"]["male"]


def test_influences_signs(client):
    inf = {i["accord"]: i for i in _post(client, [("aromatic", 100), ("floral", 100)]).json()["influences"]}
    assert inf["aromatic"]["pushes_toward"] == "male" and inf["aromatic"]["index_effect"] > 0
    assert inf["floral"]["pushes_toward"] == "female" and inf["floral"]["index_effect"] < 0


def test_predict_rescales_relative_intensity(client):
    r = _post(client, [("woody", 40)])
    assert r.json()["accords_used"] == {"woody": 100.0}


def test_predict_unknown_accord_is_422(client):
    r = _post(client, [("inexistente", 50)])
    assert r.status_code == 422
    assert "inexistente" in r.json()["detail"]


def test_predict_validation_errors(client):
    assert client.post("/api/predict", json={"accords": []}).status_code == 422
    assert _post(client, [("woody", 0)]).status_code == 422
    assert _post(client, [(f"a{i}", 10) for i in range(9)]).status_code == 422


def test_model_info(client):
    body = client.get("/api/model/info").json()
    assert "classifier" in body["metadata"] and "index_model" in body["metadata"]


def test_frontend_served(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "ScentAI" in r.text
