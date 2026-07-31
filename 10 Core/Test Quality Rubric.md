---
type: guideline
status: active
scope: python
verified: 2026-07-31
tags:
  - python
  - testing
  - review
  - quality-gates
---

# Test Quality Rubric

Use this local rubric to judge each new, materially changed, or specifically
reviewed test. It records the test-quality protocol supplied by the user on
2026-07-31.

## Scoring method

Score every criterion from **0 to 2**:

- **0 — absent or contradicted:** the test does not meet the criterion, or its
  design actively undermines it.
- **1 — partial or uncertain:** the test provides some protection, but has a
  meaningful gap or lacks evidence.
- **2 — strong:** the test clearly meets the criterion with credible evidence.

Judge the test as written and executed, not from its name or intended purpose.
Record a short reason for every score of 0 or 1 so the next improvement is
actionable.

## Criteria

| Criterion | What a strong test demonstrates |
|---|---|
| **Protects meaningful behavior** | Verifies a real requirement, business rule, boundary, or previously observed defect. |
| **Fails when the behavior is broken** | Changing or mutating the relevant production logic makes the test fail. |
| **Has strong assertions** | Verifies the important result and side effects, rather than merely “no exception,” “not null,” or status 200. |
| **Fails for the correct reason** | A failure indicates a defect in the behavior under test, not unrelated setup or infrastructure. |
| **Is deterministic** | The same code and inputs produce the same result without depending on uncontrolled time, ordering, randomness, shared state, or services. |
| **Tests observable behavior** | Verifies the public contract rather than private methods, internal call order, or implementation details. |
| **Uses realistic dependencies** | Uses real implementations or accurate fakes; mocks do not invent behavior that may differ from production. |
| **Tests one understandable scenario** | Has one clear purpose, and its name explains the situation and expected outcome. |
| **Covers meaningful edge conditions** | Represents an important happy path, boundary, invalid input, or failure case rather than an arbitrary example. |
| **Is readable and maintainable** | Makes setup, action, and expectation understandable without mentally executing the production code. |

The maximum score is **20**.

## Interpretation

| Total | Interpretation |
|---:|---|
| **17–20** | Strong test |
| **13–16** | Useful, but potentially improvable |
| **9–12** | Questionable; review assertions, mocks, and purpose |
| **0–8** | Weak; rewrite or remove |

The total is a review aid, not an automatic pass/fail gate. The two most
important criteria are **Protects meaningful behavior** and **Fails when the
behavior is broken**. A high total does not compensate for a test that lacks
credible protection on either one.

## Evidence and review workflow

1. Identify the requirement, rule, boundary, or defect the test claims to
   protect.
2. Run the test against the intended production behavior.
3. Establish sensitivity where practical: capture the pre-fix failure, use a
   targeted mutation tool, or temporarily introduce the relevant defect and
   confirm that the test fails. Restore the production logic before continuing.
4. Score all ten criteria and note the reason for every 0 or 1.
5. Use the two primary criteria first, then the total and score band, to decide
   whether to keep, improve, rewrite, or remove the test.

Do not manufacture a mutation that only breaks setup or an unrelated path.
Sensitivity evidence is valuable only when the test fails because the claimed
behavior changed.

Related: [[Testing Strategy]] · [[Workflow and Quality Gates]] ·
[[Review Checklist]]
