---
type: map-of-content
status: active
scope: hyperdrive
verified: 2026-09-22
tags:
  - hyperdrive
  - context-map
  - delivery
  - acceptance
---

# Hyperdrive Context Map

Use the general language route first, then load only the Hyperdrive context
required by the task. Do not follow `Related` links by default.

| Task signal | Load | Stop when |
|---|---|---|
| Python implementation or review | [[Python Guidelines Context Map]] and [[Workflow and Quality Gates]] | Behavior, checks, and quality gates are known |
| Shared library, contract, cross-service, compatibility, transport, or consumer update | [[Integration Boundaries]] | Owner, artifact gate, consumers, compatibility, and evidence are known |
| Branch, worktree, push, or merge-request work | Active global `AGENTS.md` and closest repository instructions | Current authorization, base ref, task branch, and human-only merge boundary are known |
| Deployment, ArgoCD, Kubernetes, dev2, or live Hyperdrive testing | [[Hyperdrive Delivery and Acceptance]] | Exact target, artifact, rollout evidence, live behavior, and remaining gaps are known |

Keep task-specific URLs, revisions, credentials, inventory, and accepted
architecture in the task or a focused project note. Do not promote them into
this map.
