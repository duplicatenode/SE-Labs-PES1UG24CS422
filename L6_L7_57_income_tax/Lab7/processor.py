"""Hardened Lab 6 income tax application used as the Lab 7 fuzzing target."""


def _require_integer(value, name):
    """Reject floats and booleans where the tax rules require whole numbers."""
    if not isinstance(value, int) or isinstance(value, bool):
        raise TypeError(f"{name} must be an integer")


def taxable_income(gross, regime, investments):
    _require_integer(gross, "gross")
    _require_integer(investments, "investments")
    if not isinstance(regime, str):
        raise TypeError("regime must be a string")
    if gross < 0:
        raise ValueError("gross must be nonnegative")
    if investments < 0:
        raise ValueError("investments must be nonnegative")
    if regime == "new":
        deduction = 75000
    elif regime == "old":
        if investments > 150000:
            investments = 150000
        deduction = 50000 + investments
    else:
        raise ValueError("unknown regime")
    taxable = gross - deduction
    if taxable < 0:
        return 0
    return taxable


def tax_due(taxable, age):
    _require_integer(taxable, "taxable")
    _require_integer(age, "age")
    if taxable < 0:
        raise ValueError("invalid amount")
    if age < 0:
        raise ValueError("age must be nonnegative")
    if age >= 80:
        exempt = 500000
    elif age >= 60:
        exempt = 300000
    else:
        exempt = 250000
    if taxable <= exempt:
        return 0
    slab = taxable - exempt
    if slab <= 250000:
        return slab * 5 // 100
    return 12500 + (slab - 250000) * 20 // 100


def refund_status(tax_paid, tax_due_amount, filed_on_time):
    _require_integer(tax_paid, "tax_paid")
    _require_integer(tax_due_amount, "tax_due_amount")
    if not isinstance(filed_on_time, bool):
        raise TypeError("filed_on_time must be a boolean")
    if tax_paid < 0 or tax_due_amount < 0:
        raise ValueError("tax amounts must be nonnegative")
    difference = tax_paid - tax_due_amount
    if difference > 0:
        if filed_on_time:
            return "refund"
        return "refund delayed"
    elif difference < 0:
        if filed_on_time:
            return "pay balance"
        return "pay balance with penalty"
    return "settled"


def main():
    """Run a short demonstration with ordinary Lab 6 inputs."""
    print("Taxable income:", taxable_income(1000000, "new", 0))
    print("Tax due:", tax_due(600000, 30))
    print("Refund status:", refund_status(15000, 12500, True))


if __name__ == "__main__":
    main()
