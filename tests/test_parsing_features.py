import numpy as np

from perfume_gender.features import build_vocab, rescale_to_max, to_matrix, vectorize
from perfume_gender.parsing import normalize_accord, parse_accords


def test_parse_basic():
    assert parse_accords("woody:100|sweet:65") == {"woody": 100.0, "sweet": 65.0}


def test_parse_accord_names_with_spaces_and_case():
    assert parse_accords("Fresh Spicy:47|  WHITE floral : 26") == {"fresh spicy": 47.0, "white floral": 26.0}


def test_parse_merges_powder_alias():
    assert parse_accords("powder:30|powdery:50") == {"powdery": 50.0}


def test_parse_ignores_garbage_and_nulls():
    assert parse_accords(None) == {}
    assert parse_accords(float("nan")) == {}
    assert parse_accords("sin_dos_puntos|woody:abc|sweet:10") == {"sweet": 10.0}


def test_normalize_accord():
    assert normalize_accord("  Powder ") == "powdery"


def test_build_vocab_min_count():
    dicts = [{"a": 1, "b": 1}, {"a": 1}, {"a": 1, "c": 1}]
    assert build_vocab(dicts) == ["a", "b", "c"]
    assert build_vocab(dicts, min_count=2) == ["a"]


def test_vectorize_scales_to_unit_range_and_ignores_unknown():
    vocab = ["a", "b", "c"]
    v = vectorize({"a": 100, "c": 50, "zzz": 80}, vocab)
    assert v.dtype == np.float32
    assert v.tolist() == [1.0, 0.0, 0.5]


def test_to_matrix_shape():
    m = to_matrix([{"a": 100}, {"b": 20}], ["a", "b"])
    assert m.shape == (2, 2)


def test_rescale_to_max():
    assert rescale_to_max({"a": 50, "b": 25}) == {"a": 100.0, "b": 50.0}
    assert rescale_to_max({}) == {}
