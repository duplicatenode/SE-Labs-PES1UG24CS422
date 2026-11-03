# Reflection

The handout refers to four reflection questions, but the supplied three-page
PDF does not include their wording. These answers address four prompts drawn
from the stated learning outcomes.

## 1. What does static analysis do, and what can it not prove?

Static analysis inspects source without running it. Pylint highlighted maintainability
and logic-risk patterns, Flake8 caught formatting issues, and Bandit found unsafe
transport, deserialization, and credential patterns. The tools helped focus the
review, but they could not determine whether the loan policy itself was sensible
or whether the EMI output was correct. Running the demo exposed the rate-unit bug
and the approval of an unsupported loan type.

## 2. Which findings mattered most, and why?

The incorrect EMI and maximum-loan calculation could misstate a customer's
repayment or affordable principal. The FTP transfer and embedded password could
expose application data and credentials. I fixed those alongside unsafe
deserialization and the invalid product approval because they affect correctness
or sensitive data, not just readability.

## 3. How did the tools complement each other?

Pylint assessed code quality and produced a score, Flake8 gave precise style
locations, and Bandit focused on security patterns. Their reports overlapped in
places but did not replace one another. Manual inspection was still needed to
interpret the business behavior and check the program's printed results.

## 4. What would I do differently in future development?

I would define units and valid input ranges at each function boundary, keep
credentials outside source code, and run the three scanners as part of a repeatable
development check. I would also keep a small set of expected calculation examples
so that a clean static-analysis report is paired with evidence that the program
still produces sensible results.
