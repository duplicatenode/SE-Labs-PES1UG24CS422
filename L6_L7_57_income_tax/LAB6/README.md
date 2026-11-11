# L6_L7_57 — Income Tax Calculator

Lab 6: Code and Branch Coverage

## About

A small Python module that works out taxable income under two tax regimes, calculates the tax due by age group and reports whether a refund or balance is owed.

## Files

| File | Description |
|------|-------------|
| `income_tax.py` | The module under test |
| `test_income_tax.py` | Starter test file |
| `CodeCoverageTest_income_tax_application.py` | Tests for line/code coverage |
| `BranchCoverageTest_income_tax_application.py` | Tests for decision branch coverage |
| `Lab6_Income_Tax_Coverage_Report.pdf` | Coverage summary with both command output figures |

Keep all Lab 6 work in this `LAB6` folder. Lab 7 is in the sibling folder [`Lab7`](../Lab7/README.md).

Refer to the lab handout for instructions.

## Code coverage

From this folder, run:

```powershell
python -m coverage erase
python -m coverage run --source=income_tax -m pytest CodeCoverageTest_income_tax_application.py -q
python -m coverage report -m
```

The tests exercise valid inputs, error handling, tax brackets, and all refund
outcomes. `CodeCoverageResults.txt` records the verified test and coverage
output: 21 tests passed and `income_tax.py` reached 100% line coverage.

## Branch coverage

From this folder, run:

```powershell
python -m coverage erase
python -m coverage run --branch --source=income_tax -m pytest BranchCoverageTest_income_tax_application.py -q
python -m coverage report -m
```

The branch suite checks both outcomes for each decision, including boundary
values for investment caps, age exemptions, and tax brackets.
`BranchCoverageResults.txt` records the verified output: 24 tests passed,
with 100% coverage across all 28 branches in `income_tax.py`.

The PDF report summarizes both runs and includes a rendered image of each saved
coverage transcript. The PNGs are also included as separate files:
`code_coverage_output.png` and `branch_coverage_output.png`.
