---
type: guideline
status: active
scope: python
verified: 2026-08-05
tags:
  - python
  - integration
  - compatibility
  - shared-libraries
  - observability
---

# Integration Boundaries

## Design target

Shared infrastructure should have one clear owner, one production construction
path, explicit compatibility boundaries, and end-to-end evidence.

## Required

- Identify the canonical owner and public entry point before changing shared
  infrastructure.
- Keep one authoritative construction or configuration path. It must return a
  complete, work-ready object, and both production code and tests must use it.
- Put reusable cross-service behavior in the owning shared library. Keep
  service-specific settings and runtime dependencies in each service.
- Inventory affected compatibility before editing: public arguments, manual
  overrides, headers, payloads, envelopes, naming, casing, and downstream
  consumers.
- For transport or observability changes, record each affected field's semantic
  meaning, owner, source, carrier or header, consumer, requiredness, manual
  override, fallback, and compatibility status before editing.
- When compatibility must change, define the migration boundary, affected
  consumers, transition behavior, and removal evidence.
- Do not infer one identity or security-principal field from another, make a
  required identity optional, or add a fallback without explicit contract
  evidence.
- Keep request-specific data request-scoped through the framework or
  instrumentation context. Do not store it in module-level or static
  variables.
- For a staged multi-repository change, implement and verify the owning layer
  before updating consumers.
- For a shared-library or contract change, publish and independently resolve
  the new artifact from the canonical registry before updating consumer
  versions or lockfiles.
- Define production acceptance evidence for infrastructure behavior. Cover the
  ingress, transport metadata, receiving service, and observable result with a
  canary or equivalent smoke test when practical.
- Reproduce cross-service defects through the sender, transport representation,
  and receiver behavior. A producer mock that only checks emitted arguments is
  insufficient when the reported failure occurs in the consumer.
- After behavior is verified, remove only redundant plumbing introduced or
  exposed by the requested change.

## Forbidden

- A local wrapper that merely duplicates a shared-library API without a
  repository-specific adaptation.
- A test-only construction path that bypasses the production factory or
  configuration entry point.
- Helper classes or functions whose only purpose is forwarding the same
  arguments to the canonical API.
- Removing a compatibility field because tracing or another metadata mechanism
  appears to carry similar information.
- Treating a business correlation identifier, distributed trace context, and
  tracer-provider configuration as the same responsibility.

## Review checklist

- Which layer owns the behavior?
- Does an existing public API already provide it?
- Is there exactly one production construction path?
- Do tests exercise that same path?
- Which compatibility surfaces and consumers are affected?
- For each affected field, what are its meaning, carrier, requiredness,
  overrides, fallback, and migration status?
- Are explicit overrides and transitional behavior preserved or deliberately
  migrated?
- Is request-specific state isolated to the active request or message?
- What focused test proves the invariant?
- Does defect evidence reach the boundary where the reported failure occurs?
- What production signal proves the cross-boundary flow?
- Can touched plumbing be simplified without broadening scope?

Related: [[Workflow and Quality Gates]] · [[Clean Code and Architecture]] ·
[[Testing Strategy]] · [[Implementation Playbook]] · [[Interpretation Notes]]
