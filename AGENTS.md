# Codex knowledge-vault instructions

This workspace is a knowledge vault, not an application repository.

## Context loading

1. Start at `00 Maps/Python Guidelines Context Map.md`.
2. Always read `10 Core/Workflow and Quality Gates.md` for Python work.
3. Load only the core and framework notes selected by the context map.
4. Use `30 Playbooks/Implementation Playbook.md` for changes and `30 Playbooks/Review Checklist.md` for reviews.
5. Consult `90 Sources/Interpretation Notes.md` when wording or precedence is unclear.

## Operating rules

- Treat rules marked **Required** or **Forbidden** as strict unless the user explicitly approves a documented exception.
- Prefer the existing repository's local conventions when they do not conflict with an applicable strict rule.
- State assumptions that affect behavior, API, tests, or architecture.
- Make the smallest change that satisfies the request; do not add speculative abstractions or unrelated cleanup.
- For behavior changes, add or update behavior-focused tests in the same change.
- Run the smallest relevant tests plus `ruff` and `mypy`; report any check that cannot run.
- Never weaken lint or type-check configuration to make checks pass.
- Do not run Git commands or alter Git history. Git operations are human-only under the source workflow policy.

The source of truth for navigation is the context map. The upstream repository remains authoritative for exact wording.
