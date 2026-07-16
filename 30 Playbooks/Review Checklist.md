---
type: playbook
status: active
scope: python
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
- [ ] Side effects are isolated from complex branching.
- [ ] Exception translation happens at a boundary and preserves cause.
- [ ] New abstractions remove repeated knowledge rather than anticipate future needs.

## Tests

- [ ] Tests prove observable behavior through a real entry point where practical.
- [ ] Relevant negative paths and side effects are asserted.
- [ ] Contract assertions are complete enough to detect drift.
- [ ] Internal collaborators are not mocked without a boundary reason.
- [ ] Tests are deterministic, isolated, and clearly structured.

## Framework-specific

- [ ] FastAPI settings and error handling follow [[FastAPI Guidelines]], if applicable.
- [ ] Django/DRF settings and error handling follow [[Django and DRF Guidelines]], if applicable.
- [ ] Endpoints/views remain thin.

## Quality gates

- [ ] Relevant tests pass.
- [ ] `ruff` passes without weakened rules.
- [ ] `mypy` passes without broad escapes.
- [ ] Suppressions are local, specific, and explained.

Report actionable findings with file and line, expected impact, and the smallest credible correction. If there are no findings, state that explicitly and mention any verification gap.
