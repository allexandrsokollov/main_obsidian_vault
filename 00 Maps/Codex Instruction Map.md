---
type: map-of-content
status: active
scope: codex
verified: 2026-07-23
tags:
  - codex
  - personalization
  - agents
  - context-map
---

# Codex Instruction Map

Put each instruction at the narrowest scope where it remains true. This reduces repeated context, conflicts, and stale rules.

```mermaid
flowchart TD
    I["Instruction"] --> Q{"Where is it true?"}
    Q -->|"Across chats and repositories"| P["Personalization / personal AGENTS.md"]
    Q -->|"One repository"| R["Repository AGENTS.md"]
    Q -->|"One subtree"| N["Nested AGENTS.md or AGENTS.override.md"]
    Q -->|"One kind of repeated task"| S["Skill"]
    Q -->|"Accepted decisions reused across tasks"| C["Project context note"]
    Q -->|"One task only"| T["Task prompt"]
    R --> K["Knowledge maps and playbooks"]
    N --> K
    C --> K
```

## Placement rules

| Surface | Put here | Keep out |
|---|---|---|
| Settings → Personalization | Stable collaboration preferences that apply everywhere | Repository commands, language-specific details, long checklists |
| Personal `AGENTS.md` | Durable cross-repository defaults and routing | Duplicates of Personalization or project-only rules |
| Repository `AGENTS.md` | Layout, commands, architecture, language policy, definition of done | Personal tone preferences and unrelated repositories |
| Nested `AGENTS.md` or `AGENTS.override.md` | Rules for a specific package or service | General repository rules already stated above |
| Project context note | Accepted architecture, compatibility boundaries, current state, and compact handoffs | Exploration logs, rejected alternatives, raw command output |
| Skill | A repeated workflow with specialized references or scripts | One-off task context |
| Task prompt | Goal, relevant context, constraints, and done condition | Durable rules that should apply next time |

## Recommended chain

1. Personalization supplies a short working style.
2. Repository `AGENTS.md` supplies the concrete engineering contract.
3. The applicable context map loads deeper knowledge on demand.
4. A decision checkpoint settles material choices before substantial implementation.
5. A compact handoff carries only accepted decisions into implementation.
6. The task prompt names the result and completion evidence.

Codex discovers `AGENTS.md` once per run/session, from global scope through the repository path. More specific files appear later and override broader guidance. Avoid duplicating the same rule at several layers.

Use [[Codex Context Continuity]] when a plan spans multiple tasks, a long exploration
would pollute implementation context, or a retrospective reveals missing durable
guidance.

## Language routing

- Python repository: repository `AGENTS.md` points to [[Python Guidelines Context Map]] or to a pinned copy available inside that repository.
- Go repository: use a repository-local map or skill based on [guidelines-golang](https://github.com/allexandrsokollov/guidelines-golang). The current vault does not yet mirror that repository.
- Mixed repository: put common rules at the root and language-specific routing in the closest relevant subtree.

## Verification

At the start of a fresh Codex task, ask:

> List the active instruction sources in precedence order. Summarize only the rules relevant to this task and identify conflicts.

Then give the task using:

> Goal: …  
> Context: …  
> Constraints: …  
> Done when: …

Related: [[Codex Instruction Strategy]] · [[Codex Context Continuity]] · [[Codex Product Sources]]
