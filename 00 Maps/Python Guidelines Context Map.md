---
type: map-of-content
status: active
scope: python
source_revision: 885b4e41af02a3c432de5086e74d3bd347cc70ca
tags:
  - python
  - codex
  - context-map
---

# Python Guidelines Context Map

Use this map to load only the context needed for the current task.

For deciding whether guidance belongs in Personalization, `AGENTS.md`, a prompt, or a skill, use [[Codex Instruction Map]].

## Always load

1. [[Clean Code and Architecture]]
2. [[Linting and Type Checking]]
3. [[Workflow and Quality Gates]]
4. The task-specific notes selected below

```mermaid
flowchart TD
    A["Python task"] --> C["Clean Code and Architecture"]
    A --> L["Linting and Type Checking"]
    A --> W["Workflow and Quality Gates"]
    A --> T{"Task context"}
    T -->|"Signatures, DTOs, queries"| Y["Typing and DTO Contracts"]
    T -->|"Behavior change or bug fix"| X["Testing Strategy"]
    T -->|"Shared library, integration, compatibility"| B["Integration Boundaries"]
    T -->|"FastAPI"| F["FastAPI Guidelines"]
    T -->|"Django or DRF"| D["Django and DRF Guidelines"]
    C --> I["Implementation Playbook"]
    Y --> I
    X --> I
    B --> I
    B --> X
    F --> I
    D --> I
    A -->|"Review request"| R["Review Checklist"]
```

## Routing table

| Task signal | Load | Key outcome |
|---|---|---|
| Any Python change | [[Clean Code and Architecture]] + [[Linting and Type Checking]] + [[Workflow and Quality Gates]] | Keep code clean; run Ruff, mypy, and BasedPyright with the required baseline or stricter configuration; use Git only for read-only inspection |
| New code, refactor, architecture | [[Typing and DTO Contracts]] | Readable boundaries and explicit contracts |
| Bug fix or behavior change | [[Testing Strategy]] + [[Implementation Playbook]] | Reproduce or specify behavior, then verify the fix |
| Shared library, canonical factory, dependency integration | [[Integration Boundaries]] + [[Implementation Playbook]] | One owner and one production construction path |
| Cross-service transport, compatibility, observability | [[Integration Boundaries]] + [[Testing Strategy]] | Preserve boundary behavior and prove the end-to-end flow |
| FastAPI endpoint, settings, errors | [[FastAPI Guidelines]] | Thin endpoints, typed settings, centralized errors |
| Django/DRF view, settings, errors | [[Django and DRF Guidelines]] | Thin views, Django settings, DRF exception mapping |
| Code review | [[Review Checklist]] plus relevant framework note | Findings tied to observable risk and strict rules |
| Unclear or conflicting rule | [[Interpretation Notes]] | Apply documented precedence; surface ambiguity |

## Precedence

Apply guidance in this order:

1. Explicit user requirements
2. Repository-local instructions and established patterns
3. Applicable framework note
4. Core notes in this vault
5. General preference

Do not use a local pattern to justify a behavior that an applicable strict rule explicitly forbids. If rules genuinely conflict or would change a public contract, stop and surface the conflict.

## Minimal context bundles

### Framework-agnostic change

[[Clean Code and Architecture]] → [[Linting and Type Checking]] → [[Workflow and Quality Gates]] → [[Typing and DTO Contracts]] → [[Testing Strategy]] → [[Implementation Playbook]]

### FastAPI change

Framework-agnostic bundle + [[FastAPI Guidelines]]

### Django or DRF change

Framework-agnostic bundle + [[Django and DRF Guidelines]]

### Shared infrastructure or cross-service integration

[[Clean Code and Architecture]] → [[Linting and Type Checking]] → [[Workflow and Quality Gates]] → [[Integration Boundaries]] →
[[Testing Strategy]] → [[Implementation Playbook]]

### Review only

[[Clean Code and Architecture]] → [[Linting and Type Checking]] → [[Workflow and Quality Gates]] → [[Review Checklist]] → relevant core/framework note

## Source boundary

These notes are a retrieval-oriented summary. For exact wording, examples, or a disputed interpretation, use [[Upstream Sources]] and [[Interpretation Notes]].
