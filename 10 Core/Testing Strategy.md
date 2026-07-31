---
type: guideline
status: active
scope: python
source_revision: 885b4e41af02a3c432de5086e74d3bd347cc70ca
tags:
  - python
  - testing
---

# Testing Strategy

## Testing target

Tests should prove externally observable behavior and remain useful through internal refactoring.

## Preferred entry points

- HTTP endpoints
- Message handlers
- CLI commands
- Public service interfaces

Exercise the path real callers use so routing, validation, business logic, serialization, and infrastructure integration are covered where relevant.

## Dependencies

- Use real internal databases, caches, brokers, and other owned infrastructure when the scope depends on them.
- Use isolated environments or test containers where practical.
- Mock boundaries outside your control: third-party APIs, providers, expensive systems, and hard-to-reproduce external failures.
- Do not mock core internal collaborators by default.

## Scenario requirements

- Keep tests deterministic, isolated, and independent of execution order.
- Control time and randomness explicitly.
- Use factories or builders for repeated entity and request setup.
- Structure each test as Arrange, Act, Assert.
- Name the scenario and expected outcome.
- Prefer one behavior scenario per test.
- Test several materially distinct success scenarios; a single happy-path
  scenario is insufficient.
- As the behavior under test becomes more complex, the number of success
  scenarios **MUST** increase substantially, not marginally. Cover each
  materially different branch, state, boundary value, and collaborator
  interaction.
- Test several materially distinct negative scenarios; one generic failure
  scenario is insufficient.
- As the behavior under test becomes more complex, the number of negative
  scenarios **MUST** increase substantially, not marginally. Cover each
  validation rule, failure source, invalid state, boundary failure, and
  relevant combination of failures.

Cover relevant negative paths:

- Invalid or missing input
- Permission failures
- Duplicates and conflicts
- Invalid state transitions
- Repeated delivery or duplicate events
- Empty or partial data
- Unexpected 500 behavior for API boundaries

## Assertions

- Assert persisted state, emitted messages, cache changes, audits, and queued work when relevant.
- Protect complete response and message contracts when consumers depend on their shape.
- Do not treat a status code or internal mock call count as sufficient evidence.

## Anti-patterns

- Tests coupled to private implementation or internal call order.
- Broad fixture magic that hides scenario intent.
- Weak partial assertions that allow contract drift.
- Hidden shared state, order dependence, or uncontrolled randomness.
- Repeated hand-built object graphs instead of a readable factory.

Related: [[Workflow and Quality Gates]] · [[Implementation Playbook]] · [[FastAPI Guidelines]] · [[Django and DRF Guidelines]]
