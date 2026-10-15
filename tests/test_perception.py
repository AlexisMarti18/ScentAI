import numpy as np
import pandas as pd

from perfume_gender.perception import perception_index, perception_votes, vote_weight, zone


def _votes(**kw):
    base = {"perceived_female": 0, "perceived_female_leaning": 0, "perceived_unisex": 0,
            "perceived_male_leaning": 0, "perceived_male": 0}
    base.update(kw)
    return pd.DataFrame([base])


def test_only_male_is_one():
    assert perception_index(_votes(perceived_male=10)).iloc[0] == 1.0


def test_only_female_is_zero():
    assert perception_index(_votes(perceived_female=7)).iloc[0] == 0.0


def test_only_unisex_is_half():
    assert perception_index(_votes(perceived_unisex=3)).iloc[0] == 0.5


def test_mixed_votes_weighted():
    # 10 male (1.0) + 10 unisex (0.5) -> 0.75
    assert perception_index(_votes(perceived_male=10, perceived_unisex=10)).iloc[0] == 0.75


def test_zero_votes_is_nan():
    assert np.isnan(perception_index(_votes()).iloc[0])


def test_perception_votes_total():
    assert perception_votes(_votes(perceived_male=4, perceived_female_leaning=3)).iloc[0] == 7


def test_zone_limits():
    assert list(zone(np.array([0.0, 0.32, 0.33, 0.67, 0.68, 1.0]))) == [
        "female", "female", "unisex", "unisex", "male", "male"]


def test_vote_weight_sqrt_with_cap():
    w = vote_weight(np.array([1, 4, 100, 10_000]))
    assert w.tolist() == [1.0, 2.0, 10.0, 10.0]
