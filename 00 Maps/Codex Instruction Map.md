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

Put each instruction at the narrowest scope where it remains true.

| Surface | Put here | Keep out |
|---|---|---|
| Personalization or personal `AGENTS.md` | Universal style and cross-repository defaults | Project rules or duplicates |
| Repository `AGENTS.md` | Layout, commands, architecture, language policy, done criteria | Personal style |
| Nested `AGENTS.md` or override | Genuine subtree differences | Repeated parent rules |
| Skill | Repeated specialized workflow and resources | One-off task state |
| Project note | Accepted architecture, compatibility, and handoffs | Logs and rejected options |
| Task prompt | Goal, relevant context, constraints, done condition | Durable rules |

Instruction chain: short global style → repository contract → mapped notes loaded
on demand → accepted decisions → compact task handoff. More specific
`AGENTS.md` files override broader ones; do not duplicate rules across layers.
Codex discovers them at task start, so use a fresh task after changing them.

Use [[Codex Context Continuity]] only for cross-task work, noisy exploration, or
reusable lessons.

## Language routing

- Python: point to [[Python Guidelines Context Map]] or a pinned local copy.
- Go: use a pinned repository map or skill; this vault does not mirror the
  [upstream guide](https://github.com/allexandrsokollov/guidelines-golang).
- Mixed: keep common rules at root and language rules in the nearest subtree.

For non-trivial tasks:

```text
Goal: <observable result>
Context: <relevant evidence>
Constraints: <material boundaries>
Done when: <verification>
```

To audit loading: “List active instruction sources in precedence order,
summarize only relevant rules, and identify conflicts.”

Related: [[Codex Instruction Strategy]] · [[Codex Context Continuity]] · [[Codex Product Sources]]
