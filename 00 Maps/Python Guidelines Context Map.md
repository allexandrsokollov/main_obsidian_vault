---
type: map-of-content
status: active
scope: python
source_revision: 885b4e41af02a3c432de5086e74d3bd347cc70ca
verified: 2026-10-01
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
    T -->|"New module or one-file organization"| M["Python Module Organization"]
    T -->|"Behavior change or bug fix"| X["Testing Strategy"]
    X --> Q["Test Quality Rubric"]
    T -->|"Shared library, integration, compatibility"| B["Integration Boundaries"]
    T -->|"Logging, tracing, diagnostic events"| O["Observability and Logging"]
    T -->|"Cross-service tracing"| V["Distributed Tracing"]
    V --> E["Tracing Acceptance"]
    T -->|"Matching OpenTelemetry stack"| P["Python OpenTelemetry Integration: selected sections"]
    T -->|"FastAPI"| F["FastAPI Guidelines"]
    T -->|"Django or DRF"| D["Django and DRF Guidelines"]
    C --> I["Implementation Playbook"]
    Y --> I
    M --> I
    X --> I
    B --> I
    B --> X
    O --> X
    O --> I
    F --> I
    D --> I
    A -->|"Review request"| R["Review Checklist"]
```

## Routing table

| Task signal | Load | Key outcome |
|---|---|---|
| Any Python change | [[Clean Code and Architecture]] + [[Linting and Type Checking]] + [[Workflow and Quality Gates]] | Keep code clean; run Ruff, mypy, and BasedPyright with the required baseline or stricter configuration; use Git only for read-only inspection |
| New code, refactor, architecture | [[Typing and DTO Contracts]] | Readable boundaries and explicit contracts |
| New module, one-file organization, module refactor | [[Python Module Organization]] + [[Typing and DTO Contracts]] | Predictable module order, visible public API, minimal import-time behavior, and a cohesive split when needed |
| Bug fix or behavior change | [[Testing Strategy]] + [[Test Quality Rubric]] + [[Implementation Playbook]] | Reproduce or specify behavior, prove the test is sensitive to the behavior, then verify the fix |
| Test creation or test-quality review | [[Testing Strategy]] + [[Test Quality Rubric]] | Score meaningful protection and defect sensitivity first, then use the total to guide improvement |
| Shared library, canonical factory, dependency integration | [[Integration Boundaries]] + [[Implementation Playbook]] | One owner and one production construction path |
| Logging or diagnostic observability | [[Observability and Logging]] + [[Testing Strategy]] + [[Test Quality Rubric]] + [[Implementation Playbook]] | Define the event matrix, preserve redaction, and prove required events with sensitive tests |
| Cross-service transport or compatibility | [[Integration Boundaries]] + [[Testing Strategy]] + [[Test Quality Rubric]] + [[Implementation Playbook]] | Preserve boundary behavior and prove the end-to-end flow with sensitive tests |
| Cross-service tracing or telemetry | [[Integration Boundaries]] + [[Observability and Logging]] + [[Distributed Tracing]] + [[Tracing Acceptance]] + [[Testing Strategy]] + [[Test Quality Rubric]] + [[Implementation Playbook]] | Preserve contracts, scoped context, causality, and evidence at the required observation points; also select matching stack rows below |
| OpenTelemetry execution context or native logging | [[Integration Boundaries]] + [[Observability and Logging]] + [[Distributed Tracing]] + [[Python OpenTelemetry Integration#Bootstrap and resources]] + [[Python OpenTelemetry Integration#Native logging and context enrichment]] + [[Python OpenTelemetry Integration#Dependencies and semantic conventions]] + [[Tracing Acceptance#Context isolation matrix]] + [[Tracing Acceptance#Native logging matrix]] | Canonical immutable context API, live OTel state, emission-time native bridge, and isolated execution |
| FastAPI or HTTPX tracing | [[Integration Boundaries]] + [[Distributed Tracing]] + [[Python OpenTelemetry Integration#Bootstrap and resources]] + [[Python OpenTelemetry Integration#FastAPI ingress and application scope]] + [[Python OpenTelemetry Integration#HTTPX egress and redirects]] + [[Python OpenTelemetry Integration#Dependencies and semantic conventions]] + [[Tracing Acceptance#Transport and boundary matrix]] | One HTTP owner, pre-extraction trust policy, real send-path filtering, redirects, and selected suppressed mode |
| FastStream or NATS tracing | [[Integration Boundaries]] + [[Distributed Tracing]] + [[Python OpenTelemetry Integration#Bootstrap and resources]] + [[Python OpenTelemetry Integration#FastStream and NATS boundaries]] + [[Python OpenTelemetry Integration#Dependencies and semantic conventions]] + [[Tracing Acceptance#Transport and boundary matrix]] | Every used publication API, fresh creation contexts, sampled/unsampled policy, baggage stores, and reliability separation |
| SQLAlchemy or database tracing | [[Integration Boundaries]] + [[Distributed Tracing]] + [[Python OpenTelemetry Integration#SQLAlchemy and database spans]] + [[Python OpenTelemetry Integration#Dependencies and semantic conventions]] + [[Tracing Acceptance#Transport and boundary matrix]] | One database owner, active parentage, applicable emitted schema, and privacy |
| Collector or SigNoz delivery and shutdown | [[Distributed Tracing]] + [[Python OpenTelemetry Integration#Bootstrap and resources]] + [[Python OpenTelemetry Integration#Collector delivery and shutdown]] + [[Python OpenTelemetry Integration#Dependencies and semantic conventions]] + [[Tracing Acceptance]] | Actual trace/log pipelines, bounded export, measured shutdown, native ingestion, and backend navigation |
| Tracing acceptance or service-template approval | [[Integration Boundaries]] + [[Distributed Tracing]] + [[Tracing Acceptance]] | Populated manifest, supported choices, overrides/exceptions, reproducible reference, and separate service/deployment evidence |
| FastAPI endpoint, settings, errors | [[FastAPI Guidelines]] | Thin endpoints, typed settings, centralized errors |
| Django/DRF view, settings, errors | [[Django and DRF Guidelines]] | Thin views, Django settings, DRF exception mapping |
| Code review | [[Review Checklist]] plus [[Test Quality Rubric]] when tests are in scope, [[Python Module Organization]] when file structure is in scope, and the relevant framework note | Findings tied to observable risk and strict rules |
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

[[Clean Code and Architecture]] → [[Linting and Type Checking]] → [[Workflow and Quality Gates]] → [[Typing and DTO Contracts]] → [[Testing Strategy]] → [[Test Quality Rubric]] → [[Implementation Playbook]]

### Module creation or organization

[[Clean Code and Architecture]] → [[Linting and Type Checking]] →
[[Workflow and Quality Gates]] → [[Python Module Organization]] →
[[Typing and DTO Contracts]] → [[Implementation Playbook]]

### FastAPI change

Framework-agnostic bundle + [[FastAPI Guidelines]]

### Django or DRF change

Framework-agnostic bundle + [[Django and DRF Guidelines]]

### Shared infrastructure or cross-service integration

[[Clean Code and Architecture]] → [[Linting and Type Checking]] → [[Workflow and Quality Gates]] → [[Integration Boundaries]] →
[[Testing Strategy]] → [[Test Quality Rubric]] → [[Implementation Playbook]]

### Logging or diagnostic observability

[[Clean Code and Architecture]] → [[Linting and Type Checking]] →
[[Workflow and Quality Gates]] → [[Observability and Logging]] →
[[Testing Strategy]] → [[Test Quality Rubric]] → [[Implementation Playbook]]

### Cross-service tracing or telemetry

[[Clean Code and Architecture]] → [[Linting and Type Checking]] →
[[Workflow and Quality Gates]] → [[Integration Boundaries]] →
[[Observability and Logging]] → [[Distributed Tracing]] →
[[Tracing Acceptance]] → [[Testing Strategy]] →
[[Test Quality Rubric]] → [[Implementation Playbook]]

Select additional OpenTelemetry stack rows only for features in scope. Logging
without OTel retains the logging bundle. Ordinary FastAPI/Django work does not
load tracing notes merely because the framework supports instrumentation.
For implementation or test changes, also select the behavior/test-quality row;
stack-specific rows do not replace those existing quality gates. Hyperdrive
uses this language route first and adds its delivery route only when needed.

### Review only

[[Clean Code and Architecture]] → [[Linting and Type Checking]] → [[Workflow and Quality Gates]] → [[Review Checklist]] → [[Test Quality Rubric]] when tests are in scope → relevant core/framework note

## Source boundary

These notes are a retrieval-oriented summary. For exact wording, examples, or a disputed interpretation, use [[Upstream Sources]] and [[Interpretation Notes]].
Tracing guidance has separate supplemental provenance in [[Tracing Sources]];
its supplied proposed standard is not part of the pinned Python source revision.
