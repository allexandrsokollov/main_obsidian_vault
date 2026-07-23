# Codex knowledge-vault instructions

This workspace is a knowledge vault, not an application repository.

## Context loading

1. For Python work, start at `00 Maps/Python Guidelines Context Map.md` and read `10 Core/Workflow and Quality Gates.md`.
2. Load only the core and framework notes selected by the Python context map.
3. Use `30 Playbooks/Implementation Playbook.md` for changes and `30 Playbooks/Review Checklist.md` for reviews.
4. Consult `90 Sources/Interpretation Notes.md` when Python wording or precedence is unclear.
5. For Codex configuration or instruction-design work, start at `00 Maps/Codex Instruction Map.md`, then read `30 Playbooks/Codex Instruction Strategy.md`.
6. For retrospectives, cross-task context persistence, or planning-to-implementation handoffs, also read `30 Playbooks/Codex Context Continuity.md`.

## Operating rules

- Treat rules marked **Required** or **Forbidden** as strict unless the user explicitly approves a documented exception.
- Prefer the existing repository's local conventions when they do not conflict with an applicable strict rule.
- State assumptions that affect behavior, API, tests, or architecture.
- Make the smallest change that satisfies the request; do not add speculative abstractions or unrelated cleanup.
- For behavior changes, add or update behavior-focused tests in the same change.
- Run the smallest relevant tests plus `ruff` and `mypy`; report any check that cannot run.
- Never weaken lint or type-check configuration to make checks pass.
- Agents may run read-only Git commands to inspect repository state and history, including `git status`, `git diff`, `git log`, `git show`, and `git blame`.
- Do not run Git commands that modify the working tree, index, refs, configuration, remotes, stash, history, or other local or remote state. All Git mutations remain human-only.

The source of truth for navigation is the context map. The upstream repository remains authoritative for exact wording except where [[Interpretation Notes]] documents a local interpretation or override.
