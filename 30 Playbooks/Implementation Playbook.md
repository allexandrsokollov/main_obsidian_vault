---
type: playbook
status: active
scope: python
verified: 2026-08-05
tags:
  - python
  - codex
  - implementation
---

# Implementation Playbook

## 1. Frame the change

- Express success as observable behavior.
- State assumptions that could alter API, architecture, or tests.
- Select context through [[Python Guidelines Context Map]].
- Identify the smallest test, command, or inspection that can prove each step.
- Translate absolute requirements such as "every endpoint", "all operations",
  and "every step" into a finite acceptance matrix before editing.

## 2. Inspect locally

- Find the entry point, existing tests, domain types, error mapping, settings, and local conventions.
- Prefer an existing local pattern if it satisfies the strict guidance.
- Note unrelated defects but do not fix them without scope.

## 3. Establish evidence

- Bug fix: reproduce the bug with a focused failing test or command.
- New behavior: write a focused scenario that states the required outcome.
- Refactor: capture behavior before changing structure.

## 4. Implement minimally

- Make the smallest behavior-preserving or behavior-producing edit.
- Keep domain logic independent from framework and infrastructure details.
- Use explicit typed contracts for structured data.
- Centralize settings and transport error mapping at application boundaries.
- Avoid new abstraction until it removes repeated domain knowledge.
- When minimal code is required, compare a direct edit with the proposed
  abstraction and choose the smaller design that satisfies the acceptance
  matrix.

## 5. Verify progressively

1. Run the focused behavior test.
2. Run the related module or package tests.
3. Run broader tests when risk warrants it.
4. Run `ruff`, `mypy`, and `basedpyright` on the changed scope.
5. Inspect the final diff with read-only Git commands such as `git diff` and `git status`; confirm every changed line is in scope.

## 6. Hand off

Report:

- Observable outcome
- Files changed
- Tests and quality checks run
- Checks not run and exact reason
- Remaining risk or source ambiguity

Git mutations and history remain human-owned; read-only inspection is allowed as defined in [[Workflow and Quality Gates]].
