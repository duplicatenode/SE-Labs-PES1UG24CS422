# Lab 7: Fuzz Testing for Input Validation Bugs

**Student:** SARTHKI VACHHANI  
**SRN:** PES1UG24CS422

Lab 7 uses the same income-tax application from Lab 6. `processor_buggy.py` preserves the original three functions as the pre-fix baseline. `processor.py` is the hardened version of those functions: `taxable_income`, `tax_due`, and `refund_status`.

## Run

```powershell
python -m pip install -r requirements.txt
python processor.py
python -m pytest test_processor.py -q
```

The Hypothesis suite exercises valid tax regimes, deductions, exemption thresholds, tax slabs, filing outcomes, and invalid values/types for each function. The initial fuzz run found eight failing input-validation properties; the corrected run passes all 11 tests.

## Evidence and report

`evidence/` stores the raw command output text and rendered output panels for the original run, initial failures, corrected run, and final tests. The PNGs are transcript renderings of the saved command output, rather than direct desktop screenshots. `Lab7_FuzzTesting_Report.pdf` consolidates these four evidence panels and includes the complete final `processor.py` and `test_processor.py` source listings.
