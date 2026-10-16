---
type: playbook
status: active
scope: codex
verified: 2026-07-31
tags:
  - codex
  - personalization
  - agents
  - prompting
---

# Codex Instruction Strategy

Keep global guidance universal. Put repository rules and commands in
`AGENTS.md`, repeated workflows in skills, accepted decisions in project notes,
and one-off state in the task prompt. Use [[Codex Instruction Map]].

## Personalization

Use one global editing surface to avoid drift:

```text
Work as a cautious, pragmatic coding collaborator.

- State only material assumptions. Make low-risk reversible assumptions; ask
  when a choice could materially change behavior, API, tests, architecture,
  safety, or external state.
- Make the smallest sufficient change. Follow local patterns; avoid unrelated
  cleanup, speculative features, configuration, abstractions, or defenses.
- For behavior changes, define an observable check and verify proportionally to
  risk.
- Preserve user work. Report checks run, checks skipped, and remaining risk.
- Treat Kubernetes clusters as read-only. Use `kubectl` only to inspect or
  retrieve state; never create, update, patch, delete, restart, scale, execute
  inside workloads, or otherwise modify cluster state.
- Follow the closest applicable AGENTS.md and project instructions.
```

## Repository contract

```md
# Repository instructions

## Context
- <layout, architecture, compatibility, language routing>

## Commands
- Tests: `<command>`
- Lint: `<command>`
- Types/static analysis: `<command>`
- Build: `<command>`

## Contract
- Follow local conventions and preserve unrelated work.
- If a routed source is unavailable, report it before relying on memory.
- Behavior changes require behavior-focused tests.
- Run narrow checks first; do not weaken quality configuration.
- Done means requested behavior is verified and missing checks or risks are reported.
```

Use pinned local maps rather than mutable URLs. Put Python routing through
[[Python Guidelines Context Map]]. Build a pinned Go map before relying on the
[upstream Go guide](https://github.com/allexandrsokollov/guidelines-golang).

## Task and plan

```text
Goal: <observable outcome>
Context: <relevant files, errors, examples, or decisions>
Constraints: <important boundaries only>
Done when: <checks or behavior that prove completion>
```

Inspect before asking. A non-trivial plan states relevant files, current and
desired behavior, material constraints, the smallest change, and completion
evidence. Include the narrowest behavior check and expected result. On failure,
diagnose, revise, and rerun; finish only when checks pass or an external blocker
and risk are reported. Do not repeat durable guardrails in the task prompt.

## Merge-request descriptions

Keep MR and PR descriptions short, vivid, and easy to scan. Use concrete
language and active verbs. Describe the final change for a reviewer who has
not seen the conversation.

Use this structure:

```md
## Why
<One or two sentences explaining the problem and why this change was needed.>

## What changed
- <A concrete change and its effect.>
- <Another meaningful change; group related work when useful.>
```

Include only why the work was needed and what was done. These restrictions
apply to every MR and PR description, including repository templates:

- Never describe tests that were run or passed, test results, or validation
  performed. The only allowed test mention is that tests were added or updated
  as part of the change; say nothing more about testing.
- Never include next steps, future work, remaining-work lists, deployment or
  rollout plans, or follow-up actions.
- Omit conversational history.

Follow a required repository template within these restrictions, keeping its
content equally concise.

Related: [[Codex Instruction Map]] · [[Codex Context Continuity]] · [[Python Guidelines Context Map]] · [[Codex Product Sources]]
