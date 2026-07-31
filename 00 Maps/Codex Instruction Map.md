---
type: map-of-content
status: active
scope: codex
verified: 2026-07-31
tags:
  - codex
  - personalization
  - agents
  - context-map
---

# Codex Instruction Map

Put each instruction at its narrowest durable scope.

| Scope | Surface |
|---|---|
| Across tasks and repositories | Personalization or personal `AGENTS.md` |
| One repository | Repository `AGENTS.md` |
| One subtree | Nested `AGENTS.md` or override |
| Repeated workflow | Skill |
| Accepted architecture or handoff | Project note |
| One task | Task prompt |

Specific `AGENTS.md` files override broader ones. Do not duplicate rules. Codex
discovers them at task start, so start a fresh task after changing them.

## Task routing

| Task signal | Load | Stop when |
|---|---|---|
| Placement or personalization | [[Codex Instruction Strategy#Personalization]] | Surface and scope settled |
| Repository contract | [[Codex Instruction Strategy#Repository contract]] | Rules, commands, and done criteria settled |
| Task prompt or plan | [[Codex Instruction Strategy#Task and plan]] | Goal, context, constraints, and evidence known |
| Material open choice | [[Codex Context Continuity#Decision checkpoint]] | Choices accepted or explicitly open |
| Noisy exploration or handoff | [[Codex Context Continuity#Compact handoff]] | Truth, evidence, risks, and next action captured |
| Retrospective | [[Codex Context Continuity#Retrospective]] | Durable layer identified |
| Current Codex fact | [[Codex Product Sources]], then official docs if needed | Verified or bounded uncertainty |
| Loading audit | Use the prompt below | Sources, precedence, rules, and conflicts known |

## Language routing

Use [[Python Guidelines Context Map]] for Python and a pinned map or skill for
Go. Put mixed-repository language rules in the nearest subtree.

To audit loading: “List active instruction sources in precedence order,
summarize only relevant rules, and identify conflicts.”
