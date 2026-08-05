---
type: guideline
status: active
scope: python
verified: 2026-08-05
tags:
  - python
  - observability
  - logging
  - tracing
---

# Observability and Logging

## Design target

Observability should expose the requested semantic events with enough safe
context to diagnose behavior, without changing contracts or creating a second
instrumentation architecture.

## Before editing

Define an event matrix containing:

- operation and semantic step;
- start, result, rejection, and unexpected-failure events that are required;
- diagnostic fields and severity;
- fields that must be omitted, redacted, summarized, or represented only by
  presence, length, count, or key name;
- the test or production signal that proves each required event.

Translate "every step" and "all operations" into explicit rows. Do not infer
that operation-level start and finish events satisfy a step-level requirement.

## Required

- Prefer direct logging at existing semantic boundaries.
- Use a shared helper or decorator only for genuinely uniform event-envelope
  behavior. It must not hide required step-level results or collaborator
  outcomes.
- Preserve exception causes and tracebacks for unexpected internal failures
  while returning stable safe errors at public boundaries.
- Keep business correlation identifiers, distributed trace context, identity
  metadata, and tracer-provider configuration as separate responsibilities.
- For cross-service telemetry, also apply [[Integration Boundaries]] and prove
  the ingress, carrier, receiver, and observable result.
- Verify both event completeness and redaction through behavior-sensitive tests.

## Forbidden

- Logging secrets, credentials, tokens, private keys, or unrestricted request
  and response objects.
- Treating a decorator's generic start or finish event as evidence that every
  requested semantic step is observable.
- Removing compatibility metadata because tracing carries similar information.
- Adding a parallel wrapper, provider, context store, or construction path when
  the canonical framework or shared library already owns that responsibility.

## Review checklist

- [ ] The event matrix covers every requested operation and semantic step.
- [ ] Results, expected rejections, and unexpected failures expose the required safe context.
- [ ] Secrets and sensitive nested fields remain absent or redacted.
- [ ] Helpers reduce repeated event-envelope knowledge without hiding step-level behavior.
- [ ] Tests fail when a required event is removed or sensitive data is exposed.
- [ ] Cross-service evidence covers ingress, carrier, receiver, and observable result.

Related: [[Integration Boundaries]] · [[Testing Strategy]] ·
[[Test Quality Rubric]] · [[Workflow and Quality Gates]]
