"""Hypothesis fuzz tests for the processor helpers."""

import pytest
from hypothesis import example, given, strategies as st

from processor import normalize_text, parse_integer_list, summarize_numbers


@given(st.text(max_size=500))
@example("Ada\tLovelace")
@example(" line one\nline two ")
def test_normalize_text_collapses_all_whitespace(text):
    normalized = normalize_text(text)
    assert normalized == " ".join(text.split())
    assert normalize_text(normalized) == normalized


@pytest.mark.parametrize("value", [None, 42, ["word"], {"text": "word"}])
def test_normalize_text_rejects_non_strings(value):
    with pytest.raises(TypeError):
        normalize_text(value)


@given(st.lists(st.integers(), max_size=100))
@example([])
def test_parse_integer_list_round_trips_integer_lists(values):
    source = ",".join(str(value) for value in values)
    assert parse_integer_list(source) == values


@pytest.mark.parametrize("value", [None, 42, [1, 2]])
def test_parse_integer_list_rejects_non_strings(value):
    with pytest.raises(TypeError):
        parse_integer_list(value)


@pytest.mark.parametrize("source", ["1,,2", "1,", ",1", "one", "1, nope"])
def test_parse_integer_list_rejects_malformed_values(source):
    with pytest.raises(ValueError):
        parse_integer_list(source)


@given(st.lists(st.integers(), max_size=100))
@example([])
def test_summary_matches_list_properties(values):
    result = summarize_numbers(values)
    assert result["count"] == len(values)
    assert result["total"] == sum(values)
    if values:
        assert result["min"] == min(values)
        assert result["max"] == max(values)
        assert result["average"] == sum(values) / len(values)
    else:
        assert result["min"] is None
        assert result["max"] is None
        assert result["average"] == 0.0


@pytest.mark.parametrize("values", [None, "1,2", [1, "2"], [True]])
def test_summary_rejects_invalid_values(values):
    with pytest.raises(TypeError):
        summarize_numbers(values)
