---
type: playbook
status: active
scope: codex
verified: 2026-08-05
tags:
  - codex
  - context
  - agents
  - planning
  - handoff
---

# Codex Context Continuity

Persist current truth, not conversation history.

| Context | Store in |
|---|---|
| Repeated rule | `AGENTS.md` |
| Accepted architecture or compatibility | Focused project note |
| Material task choice | Decision checkpoint |
| Current work state | Compact handoff |
| Raw logs and history | Referenced archive, loaded only when needed |

Promote only facts likely to recur. Keep task-specific decisions local.

## Decision checkpoint

Use only when unresolved choices could materially change behavior, API,
compatibility, architecture, tests, safety, or external state.

```text
Goal: <observable result>
Scope: In <changes>; Out <non-goals>
Accepted decisions: <material choices already settled>
Assumptions: <material assumptions only>
Verification: <evidence required>
Open decisions: <user choice or None>
```

Pause only for open material decisions.

## Compact handoff

After noisy exploration or before a fresh task, replace history with:

```text
Goal: <one observable outcome>
Current state: <what is true now>
Accepted decisions: <choices not to reopen>
Constraints: <invariants and non-goals>
Evidence: <exact paths, results, identifiers, or links>
Verification: <passed and remaining checks>
Risks: <unresolved facts or None>
Next action: <one precise step>
```

Keep it under 500 words. Preserve the latest accepted state, uncertainty, exact
references, and anything that can affect behavior or verification. Drop
chronology, repeated instructions, raw output, resolved investigation, rejected
options without continuing consequences, and speculative follow-ups. Replace
the previous handoff; do not summarize summaries.

A fresh agent must be able to identify success, current state, fixed decisions,
boundaries, evidence, risks, and the next action from the handoff alone.

## Retrospective

After repeated correction, update the narrowest durable layer and remove broader
duplicates.

When a correction changes accepted behavior, architecture, environment, or
acceptance criteria, stop the superseded path. Restate the accepted replacement,
identify which plans, implementation, and evidence are now stale, and resume
from the earliest affected checkpoint.

Classify each correction before promoting it:

- An existing-rule violation needs a stronger execution or verification
  checkpoint, not duplicated wording.
- A missing rule belongs at the narrowest durable scope that would have
  prevented the failure.
- A task-local preference remains in the task or decision checkpoint and must
  not become universal guidance.

After two corrections on the same design axis, do not perform another
speculative rewrite. Capture the accepted behavior, rejected approaches, scope
limit, required evidence, and any genuinely open material decision. Pause only
when that decision could change behavior, compatibility, architecture, tests,
or safety; otherwise implement the most direct accepted design.

Related: [[Codex Instruction Map]] · [[Codex Instruction Strategy]] · [[Codex Product Sources]]
