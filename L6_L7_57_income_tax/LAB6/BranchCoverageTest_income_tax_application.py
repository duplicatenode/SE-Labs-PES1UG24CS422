"""Branch-coverage tests for the income tax calculator."""

import pytest

from income_tax import refund_status, tax_due, taxable_income


@pytest.mark.parametrize(
    ("gross", "regime", "investments", "expected"),
    [
        (1_000_000, "new", 0, 925_000),
        (1_000_000, "old", 100_000, 850_000),
        (1_000_000, "old", 150_000, 800_000),
        (1_000_000, "old", 150_001, 800_000),
        (10_000, "new", 0, 0),
        (10_000, "old", 0, 0),
    ],
)
def test_taxable_income_branches(gross, regime, investments, expected):
    assert taxable_income(gross, regime, investments) == expected


@pytest.mark.parametrize(
    ("gross", "regime", "investments", "message"),
    [
        (-1, "new", 0, "invalid income"),
        (500_000, "other", 0, "unknown regime"),
    ],
)
def test_taxable_income_error_branches(gross, regime, investments, message):
    with pytest.raises(ValueError, match=message):
        taxable_income(gross, regime, investments)


@pytest.mark.parametrize(
    ("taxable", "age", "expected"),
    [
        (200_000, 30, 0),
        (250_000, 30, 0),
        (300_000, 30, 2_500),
        (500_000, 30, 12_500),
        (500_001, 30, 12_500),
        (600_000, 30, 32_500),
        (300_000, 60, 0),
        (500_000, 60, 10_000),
        (500_000, 80, 0),
        (600_000, 80, 5_000),
    ],
)
def test_tax_due_branches(taxable, age, expected):
    assert tax_due(taxable, age) == expected


def test_tax_due_error_branch():
    with pytest.raises(ValueError, match="invalid amount"):
        tax_due(-1, 30)


@pytest.mark.parametrize(
    ("tax_paid", "due", "on_time", "expected"),
    [
        (2_000, 1_000, True, "refund"),
        (2_000, 1_000, False, "refund delayed"),
        (1_000, 2_000, True, "pay balance"),
        (1_000, 2_000, False, "pay balance with penalty"),
        (1_000, 1_000, True, "settled"),
    ],
)
def test_refund_status_branches(tax_paid, due, on_time, expected):
    assert refund_status(tax_paid, due, on_time) == expected
