import pytest
from fastapi.testclient import TestClient

from perfume_gender import config
from perfume_gender.perception import zone_center
from perfume_gender.predictor import InvalidAccordsError, InvalidTargetError, Predictor

FEMININE = {"floral": 100, "sweet": 80, "powdery": 60}


def test_zone_center_values():
    assert zone_center("female") == pytest.approx(0.165)
    assert zone_center("unisex") == pytest.approx(0.5)
    assert zone_center("male") == pytest.approx(0.835)
    with pytest.raises(ValueError):
        zone_center("otra")


def test_each_suggestion_moves_closer_to_target(tiny_predictor):
    out = tiny_predictor.suggest(FEMININE, "male")
    assert not out["reached"] and 1 <= len(out["suggestions"]) <= 3
    dist = abs(out["index"] - out["target_index"])
    for s in out["suggestions"]:
        assert abs(s["index_after"] - out["target_index"]) < dist
        assert s["delta"] > 0                      # hacia masculino el indice sube
        assert s["action"] in {"add", "remove", "increase", "decrease", "replace"}


def test_suggestions_sorted_and_one_per_accord(tiny_predictor):
    out = tiny_predictor.suggest(FEMININE, "male")
    after = [s["index_after"] for s in out["suggestions"]]
    assert after == sorted(after, reverse=True)
    names = [s["accord"] for s in out["suggestions"]]
    assert len(names) == len(set(names))


def test_toward_female_decreases_index(tiny_predictor):
    out = tiny_predictor.suggest({"aromatic": 100, "woody": 80}, "female")
    assert out["suggestions"] and all(s["delta"] < 0 for s in out["suggestions"])


def test_reached_zone_returns_no_suggestions(tiny_predictor):
    out = tiny_predictor.suggest({"aromatic": 100, "woody": 90, "fresh spicy": 80}, "male")
    assert out["reached"] and out["suggestions"] == []


def test_numeric_target_and_tolerance(tiny_predictor):
    base = tiny_predictor.suggest(FEMININE, 0.5)
    assert base["target_index"] == 0.5
    here = tiny_predictor.suggest(FEMININE, base["index"])  # ya esta en el objetivo
    assert here["reached"] and here["suggestions"] == []


def test_intensities_stay_in_user_scale(tiny_predictor):
    out = tiny_predictor.suggest({"floral": 40, "sweet": 30}, "male")  # el mas fuerte vale 40, no 100
    for s in out["suggestions"]:
        if s["to_intensity"] is not None:
            assert 1 <= s["to_intensity"] <= 100
        if s["action"] == "add":
            assert s["to_intensity"] <= 40         # relativo al acorde mas fuerte del usuario


def test_no_add_when_profile_is_full_but_replace_is_offered(monkeypatch, tiny_predictor):
    monkeypatch.setattr(config, "MAX_ACCORDS", 3)
    out = tiny_predictor.suggest(FEMININE, "male")
    assert out["suggestions"] and all(s["action"] != "add" for s in out["suggestions"])
    reps = [s for s in out["suggestions"] if s["action"] == "replace"]
    assert reps and all(s["replaces"] in FEMININE and s["accord"] not in FEMININE for s in reps)


def test_no_add_or_replace_when_not_full(tiny_predictor):
    out = tiny_predictor.suggest(FEMININE, "male")
    assert all(s["action"] != "replace" for s in out["suggestions"])


def test_suggestions_never_touch_the_same_accord_twice(monkeypatch, tiny_predictor):
    monkeypatch.setattr(config, "MAX_ACCORDS", 3)
    out = tiny_predictor.suggest(FEMININE, "male", top_k=3)
    touched = []
    for s in out["suggestions"]:
        touched += [x for x in (s["accord"], s["replaces"]) if x]
    assert len(touched) == len(set(touched))


def test_no_remove_with_single_accord(tiny_predictor):
    out = tiny_predictor.suggest({"floral": 100}, "male")
    assert all(s["action"] != "remove" for s in out["suggestions"])


def test_invalid_inputs(tiny_predictor):
    with pytest.raises(InvalidTargetError):
        tiny_predictor.suggest(FEMININE, "otra")
    with pytest.raises(InvalidTargetError):
        tiny_predictor.suggest(FEMININE, 1.5)
    with pytest.raises(InvalidAccordsError):
        tiny_predictor.suggest({"inexistente": 50}, "male")


# ---------------------------------------------------------------- API
@pytest.fixture()
def client(monkeypatch, tiny_predictor):
    monkeypatch.setattr(Predictor, "load", classmethod(lambda cls, *a, **k: tiny_predictor))
    from app.backend.main import app

    with TestClient(app) as c:
        yield c


def _body(**extra):
    return {"accords": [{"name": n, "intensity": v} for n, v in FEMININE.items()], **extra}


def test_api_suggest_ok(client):
    r = client.post("/api/suggest", json=_body(target="male"))
    assert r.status_code == 200
    body = r.json()
    assert set(body) == {"index", "zone", "target_index", "reached", "suggestions"}
    assert body["suggestions"] and set(body["suggestions"][0]) == {
        "action", "accord", "replaces", "from_intensity", "to_intensity", "index_after", "delta"}


def test_api_suggest_numeric_target(client):
    assert client.post("/api/suggest", json=_body(target_index=0.8)).status_code == 200


@pytest.mark.parametrize("extra", [{}, {"target": "male", "target_index": 0.8}, {"target": "otra"},
                                   {"target_index": 1.5}])
def test_api_suggest_target_validation(client, extra):
    assert client.post("/api/suggest", json=_body(**extra)).status_code == 422


def test_api_suggest_unknown_accord(client):
    r = client.post("/api/suggest", json={"accords": [{"name": "inexistente", "intensity": 50}], "target": "male"})
    assert r.status_code == 422 and "inexistente" in r.json()["detail"]
