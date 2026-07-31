# Knowledge-vault instructions

This workspace contains guidance, not application code.

## Routing

- Python: read `00 Maps/Python Guidelines Context Map.md` and
  `10 Core/Workflow and Quality Gates.md`, then only the notes they select. For
  changes use `30 Playbooks/Implementation Playbook.md`; for reviews use
  `30 Playbooks/Review Checklist.md`. Consult `90 Sources/Interpretation Notes.md`
  only for unclear wording or precedence.
- Codex instruction design: read `00 Maps/Codex Instruction Map.md`, then
  `30 Playbooks/Codex Instruction Strategy.md`.
- Retrospectives or cross-task handoffs: also read
  `30 Playbooks/Codex Context Continuity.md`.

Do not load unrelated vault notes.

## Contract

- **Required** and **Forbidden** rules are strict unless the user approves a
  documented exception. Otherwise prefer compatible repository conventions.
- State assumptions affecting behavior, API, tests, or architecture.
- Make the smallest sufficient change; avoid speculative work and unrelated
  cleanup. Preserve unrelated user work.
- Behavior changes require behavior-focused tests. Run the narrowest relevant
  tests plus `ruff` and `mypy`; report skipped checks and remaining risk. Never
  weaken lint or type configuration.
- Git inspection is allowed; Git mutations are human-only.

Context maps control navigation. Upstream sources control exact wording unless
[[Interpretation Notes]] records a local interpretation.
