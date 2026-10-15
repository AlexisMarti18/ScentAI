import pytest

from perfume_gender.predictor import InvalidAccordsError, lift, male_vs_female


def test_male_vs_female_ignores_unisex():
    r = male_vs_female(p_female=0.03, p_male=0.07)
    assert r == pytest.approx({"female": 0.3, "male": 0.7})


def test_male_vs_female_zero_total_is_even():
    assert male_vs_female(0.0, 0.0) == {"female": 0.5, "male": 0.5}


def test_lift_relative_to_base_rate():
    out = lift({"female": 0.03, "male": 0.30, "unisex": 0.67}, {"female": 0.33, "male": 0.15, "unisex": 0.52})
    assert out["male"] == pytest.approx(2.0)
    assert out["female"] < 0.1


def test_lift_missing_prior_is_zero():
    assert lift({"male": 0.5}, {}) == {"male": 0.0}


def test_predictor_rejects_empty(tiny_predictor):
    with pytest.raises(InvalidAccordsError):
        tiny_predictor.predict({})


def test_predictor_merges_aliases_and_case(tiny_predictor):
    out = tiny_predictor.predict({"Powder": 30, "powdery": 60})
    assert out["accords_used"] == {"powdery": 100.0}
