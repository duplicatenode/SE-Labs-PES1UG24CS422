# Static analysis findings

Findings below refer to the original `loan_calculator.py` scanned before fixes.
They are ordered with higher severity first. The before and after tool output is
saved under `reports/before/` and `reports/after/`.

| Issue | Type | Line(s) | Description | Fix Approach |
|-------|------|---------|-------------|--------------|
| Plaintext FTP bureau transfer | High / Bandit B402, B321 | 3, 67-71 | FTP sends credentials and report data without transport encryption. | Replaced FTP with HTTPS PUT, certificate validation, and a bearer token supplied through environment configuration. |
| EMI uses percentage as a whole rate | High / logic defect | 14, 95 | The demo passed `9` for 9%, producing an EMI of 375,000 instead of about 10,379 per month. | Standardized annual rates as decimals, used the monthly rate in the amortization formula, handled zero interest, and updated the demo. |
| Unknown product type could be approved | Medium / logic defect | 20-31, 96 | A high income or score returned approval before checking the loan type; the demo approved `crypto`. | Validate the supported product and input ranges before making an eligibility decision. |
| Maximum principal ignored interest | Medium / Pylint W0613 | 33-37, 97 | `annual_rate` was unused and the function multiplied available EMI by months, overstating affordable principal. | Use the present value of monthly payments at the supplied rate, with a separate zero-rate case. |
| Unsafe `marshal` deserialization | Medium / Bandit B302 | 64 | Loading a crafted binary file through `marshal.loads` uses an unsafe serialization format. | Store and load application records as JSON and verify the top-level value is an object. |
| Shared mutable default argument | Medium / Pylint W0102 | 20 | The default `history=[]` persisted changes between calls and had no clear purpose. | Removed the unused history parameter and its cross-call state. |
| Predictable application IDs | Low / Bandit B311 | 51 | `random.randint` is predictable and unsuitable for identifiers that should resist guessing. | Generate IDs with `secrets.randbelow`. |
| Hardcoded bureau password | Low / Bandit B107 | 67 | A password was embedded in source and used as a default argument. | Removed the password parameter and read an API token from the environment. |
| Shell mail dependency | Low / Bandit B404, B607, B603 | 6, 73-74 | The program invoked a platform-specific executable and ignored its exit status. | Replaced it with TLS SMTP and credentials supplied through environment configuration. |
| PEP 8 and naming violations | Style / Pylint and Flake8 | Throughout | The original had naming, line-length, spacing, docstring, and unused-import findings. | Renamed functions to snake_case, added documentation, removed unused code, and formatted lines to pass Flake8. |

## Outcome

The final scan reports a Pylint score of 10.00/10, no Bandit findings, and no
Flake8 violations. The demo now prints a monthly EMI of about 10,379 for a
500,000 loan at 9% over five years, rejects the unsupported product, calculates
maximum principal using interest, and labels a score of 950 invalid.
