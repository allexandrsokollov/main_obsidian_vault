---
type: playbook
status: active
scope: codex
verified: 2026-07-23
tags:
  - codex
  - context
  - agents
  - planning
  - handoff
---

# Codex Context Continuity

## Recommendation

Persist conclusions, not conversation history. Use three layers:

1. Repository `AGENTS.md` for the durable engineering contract.
2. A decision checkpoint for material choices before substantial implementation.
3. A compact handoff containing only accepted decisions and relevant evidence.

This keeps later tasks consistent without burying the current goal in exploration
notes, logs, rejected alternatives, or stale plans.

## What to persist

| Information | Destination | Do not include |
|---|---|---|
| Repeated repository-wide rule | Repository `AGENTS.md` | One-off preferences or task details |
| Detailed architecture or compatibility contract | Focused project context note linked from `AGENTS.md` | Generic collaboration style |
| Material choice for one substantial change | Decision checkpoint | File-by-file speculation |
| Accepted plan entering implementation | Compact handoff | Full exploration transcript |
| Failure that reveals a reusable rule | Narrowest responsible durable layer | A symptom with no established cause |

Promote a correction into durable context when it is likely to recur and remains
true outside the current task. Keep a decision task-local when it is specific to
one migration or implementation.

## Repository `AGENTS.md` template

Keep the repository file short. Route to deeper notes instead of copying their
contents.

```md
# Repository instructions

## Context routing

- For <language or task type>, read <pinned local context map>.
- For substantial or ambiguous work, use <decision-checkpoint note>.
- After decisions are settled, use <implementation-handoff note>.
- If a required source is unavailable, report it before relying on memory.

## Architecture and compatibility

- <stable ownership and dependency rules>
- <formats, interfaces, or legacy behavior that must remain compatible>
- <security or destructive-operation invariants>

## Verification

- Focused tests: `<command>`
- Full tests: `<command>`
- Lint: `<command>`
- Types/static analysis: `<command>`
- Build or smoke check: `<command>`

## Done

- Requested behavior is verified.
- Every changed line serves the request.
- Unrelated work remains untouched.
- Missing checks and remaining risk are reported.
```

Add a rule after repeated friction, not merely because it might become useful.
If the explanation is longer than the rule, put the explanation in a linked
project note.

## Decision checkpoint

Use this checkpoint after exploration and before implementation when a change is
substantial, cross-cutting, destructive, or materially ambiguous. Routine,
low-risk fixes do not need it when the prompt and durable project guidance
already settle the relevant choices.

Mark choices already specified by the user or repository as accepted. Ask only
about unresolved choices that could materially change behavior, public
interfaces, compatibility, architecture, tests, safety, or external state.

```text
Decision checkpoint

Goal:
- <observable outcome>

Relevant context:
- <files, guidance, examples, or failures inspected>

Scope:
- In: <behavior and components that will change>
- Out: <explicit non-goals>

Decisions:
- Configuration format and precedence: <accepted decision>
- Migration strategy: <accepted decision>
- Compatibility boundaries: <accepted decision>
- Architecture and ownership: <accepted decision>
- Security and destructive-operation safeguards: <accepted decision>
- Documentation audience and depth: <accepted decision>
- Completion evidence: <tests, checks, and smoke scenarios>

Assumptions:
- <only assumptions that materially affect the result>

Open decisions:
- <user choice needed, or "None">
```

If a material choice remains open, pause for acceptance. Do not pause for
low-risk, reversible implementation details.

## Compact implementation handoff

Create the handoff after the decision checkpoint is accepted. Use it as the
opening context of a separate implementation task when exploration was long or
noisy. If implementation continues in the same task, restate it immediately
before editing. Creating a separate task remains a user decision.

```text
Implementation handoff

Goal:
<one observable outcome>

Accepted decisions:
- <configuration and precedence>
- <migration and compatibility boundary>
- <architecture ownership>
- <security invariants>
- <documentation expectation>

Relevant paths:
- <path>: <why it matters>

Required behavior:
- <behavior that must become true>

Must remain unchanged:
- <compatibility contract and explicit non-goals>

Verification:
- <focused behavior test>
- <broader tests>
- <lint, type/static analysis, build, and relevant smoke checks>

Known risks or unresolved facts:
- <risk, or "None">
```

Keep the handoff under 500 words unless the accepted plan genuinely requires
more. Include requirements, exact paths, invariants, verification, and unresolved
risk. Exclude command transcripts, rejected designs, resolved investigations,
and speculative follow-up work.

## Retrospective loop

After a task, review user corrections and rework:

1. Identify which missing or unclear context caused the correction.
2. Decide whether it is durable, task-specific, or merely historical.
3. Update the narrowest responsible layer.
4. Remove duplicated wording from broader layers.
5. Start a fresh task when instruction discovery must be rebuilt.
6. Verify that Codex can list the active sources, relevant rules, and conflicts.

Related: [[Codex Instruction Map]] · [[Codex Instruction Strategy]] · [[Codex Product Sources]]
