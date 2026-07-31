# Knowledge-vault instructions

This workspace contains guidance, not application code.

## Routing

- Python: read `00 Maps/Python Guidelines Context Map.md` plus
  `10 Core/Workflow and Quality Gates.md`, then follow the map.
- Codex instruction design, planning, retrospectives, or handoffs: read
  `00 Maps/Codex Instruction Map.md`, then follow its task-routing table.

Load only routed context; do not follow `Related` links by default.

## Vault contract

- **Required** and **Forbidden** rules are strict unless the user approves a
  documented exception. Otherwise prefer compatible repository conventions.
- Preserve unrelated vault notes.
- Python behavior changes require behavior tests and the narrowest checks plus
  `ruff` and `mypy`. Never weaken quality configuration; report skipped checks
  and risk.
- Context maps control navigation. Upstream sources control exact wording
  unless [[Interpretation Notes]] records a local interpretation.
