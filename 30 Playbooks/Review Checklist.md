---
type: playbook
status: active
scope: python
verified: 2026-08-05
tags:
  - python
  - codex
  - review
---

# Review Checklist

Review for correctness and observable risk before style. Load the applicable notes from [[Python Guidelines Context Map]].

## Behavior and contracts

- [ ] The implementation matches the requested behavior and preserves unrelated behavior.
- [ ] Public signatures, response bodies, messages, and persisted effects are intentional.
- [ ] Failure paths have stable domain meaning and do not leak internals.
- [ ] Structured data uses explicit, precise types.

## Architecture

- [ ] Business rules are separate from HTTP, ORM, settings, and provider details.
- [ ] Functions and classes have cohesive responsibilities.
- [ ] When file structure is in scope, the module follows
  [[Python Module Organization]] and performs no surprising import-time work.
- [ ] Side effects are isolated from complex branching.
- [ ] Exception translation happens at a boundary and preserves cause.
- [ ] New abstractions remove repeated knowledge rather than anticipate future needs.

## Tests

- [ ] New, materially changed, or suspect tests are assessed with
  [[Test Quality Rubric]], with meaningful behavior and defect sensitivity
  reviewed before the total score.
- [ ] Tests prove observable behavior through a real entry point where practical.
- [ ] Relevant negative paths and side effects are asserted.
- [ ] Contract assertions are complete enough to detect drift.
- [ ] Internal collaborators are not mocked without a boundary reason.
- [ ] Tests are deterministic, isolated, and clearly structured.

## Framework-specific

- [ ] FastAPI settings and error handling follow [[FastAPI Guidelines]], if applicable.
- [ ] Django/DRF settings and error handling follow [[Django and DRF Guidelines]], if applicable.
- [ ] Endpoints/views remain thin.

## Integration boundaries

- [ ] Shared infrastructure uses its canonical owner and production entry point.
- [ ] Tests use the same construction or configuration path as production.
- [ ] Transport fields, overrides, fallbacks, and downstream consumers are
      inventoried before compatibility changes.
- [ ] Cross-service defect evidence reaches the boundary where the failure occurs.

## Quality gates

- [ ] Relevant tests pass.
- [ ] `ruff` passes without weakened rules.
- [ ] `mypy` passes without broad escapes.
- [ ] `basedpyright` passes with the required mode, paths, and invalid-cast diagnostic.
- [ ] Suppressions are local, specific, and explained.

Report actionable findings with file and line, expected impact, and the smallest credible correction. If there are no findings, state that explicitly and mention any verification gap.
