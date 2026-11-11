"""Hypothesis fuzz tests for the three Lab 6 income tax functions."""

import pytest
from hypothesis import example, given, strategies as st

from processor import refund_status, tax_due, taxable_income


@given(
    gross=st.integers(min_value=0, max_value=5_000_000),
    regime=st.sampled_from(["new", "old"]),
    investments=st.integers(min_value=0, max_value=500_000),
)
def test_taxable_income_matches_regime_rule(gross, regime, investments):
    if regime == "new":
        deduction = 75_000
    else:
        deduction = 50_000 + min(investments, 150_000)
    assert taxable_income(gross, regime, investments) == max(0, gross - deduction)


@given(investments=st.integers(max_value=-1))
@example(investments=-1)
def test_taxable_income_rejects_negative_investments(investments):
    with pytest.raises(ValueError, match="investments must be nonnegative"):
        taxable_income(1_000_000, "old", investments)


@given(gross=st.floats(allow_nan=False, allow_infinity=False))
@example(gross=1.5)
def test_taxable_income_rejects_non_integer_gross(gross):
    with pytest.raises(TypeError, match="gross must be an integer"):
        taxable_income(gross, "new", 0)


@given(
    taxable=st.integers(min_value=0, max_value=2_000_000),
    age=st.integers(min_value=0, max_value=120),
)
def test_tax_due_matches_exemption_and_slab_rules(taxable, age):
    exemption = 500_000 if age >= 80 else 300_000 if age >= 60 else 250_000
    slab = max(0, taxable - exemption)
    expected = slab * 5 // 100 if slab <= 250_000 else 12_500 + (slab - 250_000) * 20 // 100
    assert tax_due(taxable, age) == expected


@given(age=st.integers(max_value=-1))
@example(age=-1)
def test_tax_due_rejects_negative_age(age):
    with pytest.raises(ValueError, match="age must be nonnegative"):
        tax_due(100_000, age)


@given(taxable=st.floats(allow_nan=False, allow_infinity=False))
@example(taxable=100_000.5)
def test_tax_due_rejects_non_integer_taxable_income(taxable):
    with pytest.raises(TypeError, match="taxable must be an integer"):
        tax_due(taxable, 30)


@given(
    tax_paid=st.integers(min_value=0, max_value=2_000_000),
    due=st.integers(min_value=0, max_value=2_000_000),
    on_time=st.booleans(),
)
def test_refund_status_matches_payment_difference(tax_paid, due, on_time):
    if tax_paid > due:
        expected = "refund" if on_time else "refund delayed"
    elif tax_paid < due:
        expected = "pay balance" if on_time else "pay balance with penalty"
    else:
        expected = "settled"
    assert refund_status(tax_paid, due, on_time) == expected


@given(tax_paid=st.integers(max_value=-1))
@example(tax_paid=-1)
def test_refund_status_rejects_negative_tax_paid(tax_paid):
    with pytest.raises(ValueError, match="tax amounts must be nonnegative"):
        refund_status(tax_paid, 0, True)


@given(due=st.integers(max_value=-1))
@example(due=-1)
def test_refund_status_rejects_negative_tax_due(due):
    with pytest.raises(ValueError, match="tax amounts must be nonnegative"):
        refund_status(0, due, True)


@given(on_time=st.integers())
@example(on_time=0)
def test_refund_status_requires_boolean_filing_flag(on_time):
    with pytest.raises(TypeError, match="filed_on_time must be a boolean"):
        refund_status(10_000, 9_000, on_time)


@given(tax_paid=st.floats(allow_nan=False, allow_infinity=False))
@example(tax_paid=1.5)
def test_refund_status_rejects_non_integer_tax_paid(tax_paid):
    with pytest.raises(TypeError, match="tax_paid must be an integer"):
        refund_status(tax_paid, 0, True)
