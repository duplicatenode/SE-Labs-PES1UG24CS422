# Lab 7 Fuzz Testing

This folder contains a three-function processor example, Hypothesis tests, a
pre-fix baseline for reproducing the initial failures, and the hardened
application. The destination repository did not contain a Lab 7 starter
`processor.py`, so this folder supplies a self-contained example matching the
handout's three-function fuzzing exercise.

## Run

Install the requirements and run the fixed application and tests from this
folder:

```powershell
python -m pip install -r requirements.txt
python processor.py
python -m pytest test_processor.py -q
```

The Hypothesis properties cover Unicode whitespace normalization, integer-list
round trips, empty inputs, and summary invariants. The fixed implementation
rejects unsupported types with clear errors and handles empty lists safely.

## Bugs found and fixed

- Text normalization split only on ordinary spaces, so tabs and newlines were
  left inside the output.
- Parsing an empty string attempted to convert an empty token to an integer;
  non-string inputs also leaked incidental exceptions.
- Summarizing an empty list divided by zero, and booleans or non-integer values
  were not rejected deliberately.

`processor_buggy.py` preserves the pre-fix baseline used for the failure run.
`Lab7_FuzzTesting_Report.pdf` contains the four run-output figures and the
fuzzing summary. The PNG figures render the saved command output; the adjacent
`.txt` files retain the complete output, including the full initial failure
trace.
