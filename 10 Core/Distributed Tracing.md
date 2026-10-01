---
type: guideline
status: active
scope: python
source_revision: tracing-standard-1.3
verified: 2026-10-01
tags:
  - python
  - tracing
  - observability
  - contextvars
---

# Distributed Tracing

## Scope and authority

Use for OpenTelemetry tracing design, implementation, and review in Python
microservices. This is scoped vault guidance adopted on 2026-10-01 from the
proposed standard indexed in [[Tracing Sources]]. It does not require an
unrelated project to adopt OpenTelemetry or certify an existing deployment.
Apply only the features used by the target service; load stack-specific rules
through [[Python Guidelines Context Map]].

Required and Forbidden rules are mandatory within their applicable scope.
Recommendations retain the source's SHOULD strength; options retain MAY.
Record supported choices, recommendation overrides, and mandatory exceptions
separately under [[Tracing Acceptance#Conformance and evidence states]]. Exact
wording and examples remain in the pinned source. Local adaptations are in
[[Interpretation Notes#Tracing standard integration]].

## Ownership and propagation

Required:

- Identify one instrumentation owner per HTTP, database, or messaging boundary
  and name its acceptance test. Manual spans describe meaningful application
  operations, not another owner of an already instrumented boundary.
- Let OpenTelemetry generate IDs and manage active trace/span state. Propagate
  context through W3C carriers, using the configured propagator for parsing,
  validation, extraction, and injection.
- Keep support/request IDs, business message/workflow/causation IDs,
  idempotency, authentication, and tenant authorization separate from tracing.
  Preserve established compatibility under [[Integration Boundaries]].
- Apply ingress trust policy before extraction. On trusted continuation,
  missing or invalid traceparent starts a valid root without an unrelated
  ambient worker parent. Invalid traceparent also discards associated
  tracestate; malformed tracestate or prohibited baggage must not invalidate
  an otherwise accepted valid traceparent.
- Continue valid unsampled context. Recording/export and propagation are
  separate: is_recording may guard expensive attribute preparation, never
  whether context propagates. Suppressed/excluded HTTP follows its separately
  selected propagation policy.
- For a new outgoing operation, inject the boundary owner's current client or
  message-creation context into a per-operation carrier. Enforce destination
  policy before sending; do not blindly forward a stale incoming carrier.

Forbidden:

- Generating trace IDs from UUIDs, request IDs, entity IDs, or message IDs;
  reusing a parent span ID; inventing IDs for startup logs.
- Replacing W3C context with X-Trace-ID, X-Span-ID, or X-Parent-Span-ID.
- Introducing tracing IDs into domain DTOs, business message bodies, database
  business records, query parameters, or business function signatures.
- Installing duplicate instrumentors, providers, tracing context stores, or
  construction paths. An approved filtering adapter may share the send path
  without creating another span.

## Application execution context

Required:

- Use the canonical shared typed ContextVars API for local execution metadata.
  A module-level ContextVar declaration holds execution-scoped bindings; it
  must not become a shared mutable request dictionary.
- Bind fresh, validated, immutable metadata for each request, message delivery,
  or job. Restore tokens in finally on normal exit, failure, and cancellation,
  in the same task/context that created them. Nested enrichment within one
  operation may replace immutable metadata and then restore the outer value.
- Read active trace/span/flags from OpenTelemetry at call time. Do not cache
  ingress-time IDs in application metadata or treat a snapshot as current
  after entering or leaving a nested span.
- Provide an optional accessor that returns empty metadata outside a scope
  and a strict accessor that reports an absent scope. Neither creates a trace
  nor proves authentication or required tenant identity.
- Validate untrusted fields before binding. Required identity fails closed at
  the authorization/data-access boundary; context is not authorization.
- Keep domain inputs explicit. Context must not act as a service locator for
  sessions, clients, locks, mutable dictionaries, credentials, or request bodies.
- Treat local metadata, OTel context, wire business metadata, baggage, log
  attributes, and process resources as distinct stores. Binding alone emits
  no telemetry and performs no implicit wire or log mapping.

### Concurrency and lifetime

| Boundary | Required treatment |
|---|---|
| Ordinary call or await | Read the current execution's bindings without tracing parameters |
| Child task | Bindings are snapshots at task creation; rebinding does not flow back or sideways; supervise work that outlives its parent |
| Scoped concurrent work | Prefer TaskGroup; finish operation-owned work before scope exit |
| to_thread | Context is copied when the coroutine runs; thread rebindings do not update the caller |
| Raw thread or custom executor | Do not assume propagation; use a fresh copy_context per submission when needed and test the actual executor |
| Process or service | Serialize approved carrier/business metadata and initialize fresh receiving state |
| Startup queue worker | Establish fresh state per job; never inherit an old request implicitly |
| Detached or linked-root work | Choose clean/captured application context and trace parent/link policy explicitly; task creation is not durable delivery |

Do not enter one Python Context concurrently or use copy_context.run on an
async function as if it runs its awaited body. Clearing OTel context does not
clear a separate application ContextVar. Resetting a parent token does not
revoke a child task's snapshot. Python 3.13 binders use explicit token reset;
do not copy later-runtime token context-manager syntax into that runtime.

## Asynchronous causality and reliability

| Operation | Relationship policy |
|---|---|
| Trusted synchronous HTTP | Continue client/server parentage within one trace |
| Single-message processing | Prefer a link to message creation; parentage is permitted only for exclusively single-message processing, with a recorded and tested choice |
| Fan-out | Each subscriber delivery owns a processing span; subscribers are not each other's children |
| Per-message batch | Separate processing operation and application scope per message, following its selected single-message policy |
| Combined batch or fan-in | Link contributing contexts; do not choose one unrelated input as parent; bound link counts and document truncation |
| Delayed work, replay, or long workflow | Prefer a new execution trace linked to origin; record any supported continuation policy |
| Unrelated scheduler tick | Start a new root with fresh application metadata |

Required:

- Every new message-creation operation obtains a fresh creation context.
  Explicit batch creation may use per-message or shared fresh batch context.
  A documented byte-for-byte relay may retain origin context; transformed
  events, application retries, dead letters, and outbox publications are new
  publications, not transparent relays.
- Broker redelivery reuses the stored message's creation context but creates a
  fresh processing span and application scope for each execution. Application
  message identity and deduplication are independent of tracing IDs.
- When an outbox is used, prefer persisting an approved serialized carrier in
  infrastructure metadata in the same transaction as the business message.
  A documented SHOULD override must define replacement causal evidence.
  Dispatch still injects a new publication context; saved origin is not a
  cached outbound header. Isolate each entry, including failures.
  A documented short-delay continuation is a permitted outbox-relay alternative
  to the default linked execution trace.
- Do not keep a request span open for a business workflow's lifetime. Context
  objects, live spans, and reset tokens do not cross durable/process boundaries.
- Tracing does not supply atomic commit/publication, exactly-once delivery,
  idempotency, durable jobs, dead-letter behavior, or acknowledgement guarantees.

A span has at most one parent. Links express additional causes without merging
trace IDs or automatically inheriting the linked context's sampling decision.

## Attributes, sampling, and trust

- Prefer meaningful business spans, stable operation/route-template names, and
  bounded attributes. Do not instrument every function or put IDs in span
  names or unbounded metric dimensions.
- Check the manifest's semantic-convention registry before adding attributes.
  Required: implement reserved namespaces only with their specified meaning
  and type; do not use app.* as a generic custom prefix. Prefer an
  organization-owned reverse-domain namespace. com.yourcompany is illustrative.
- High-cardinality trace/log attributes are permitted when approved for privacy,
  investigation value, and cost; they must not automatically become metrics.
- Required: bound dynamic messaging names and metric dimensions at or before
  SDK aggregation. Collector normalization is additional evidence, not a
  substitute for an SDK-side requirement.
- Required: honor parent-aware sampling within continued traces. Prefer a
  documented platform default; linked roots make their own root decision unless
  a reviewed sampler explicitly uses links.
- Tail sampling cannot recover spans discarded by head sampling. Route each
  trace to one sampling Collector and size windows, memory, queues, and late
  arrival handling. Do not promise all errors retained without path evidence.
- Required: declare public-ingress continue/reset and sampling trust policy;
  do not let untrusted sample flags force unlimited telemetry.
- Baggage is denied by default. An approved use needs keys, allowed values,
  encoded-value and total-size limits, destinations, retention, owner, and
  tests. It is never a source of authorization or tenant isolation.
- Required: redact at source where possible and add collection safeguards.
  Never capture secrets, tokens, cookies, credentials, personal data in baggage,
  or unrestricted bodies, message payloads, SQL values, and exception text.
  Trace identifiers are not credentials or integrity proofs.

## Outcomes and cancellation

These are defaults for application-owned spans, not overrides for automatic
HTTP/database/messaging conventions. Document domain-specific departures.

| Outcome | Application span treatment |
|---|---|
| Success or ordinary expected business rejection | UNSET; no error.type; optional bounded business outcome |
| Dependency timeout that fails the operation | ERROR; error.type=dependency_timeout; preserve deadline/failure contract |
| Missing required result or unexpected invariant failure | ERROR; canonical bounded error.type; preserve failure contract |
| Failed attempt followed by successful retry | Failed attempt retains evidence; successful logical operation stays UNSET without stale error.type |
| Positively identified expected cancellation | UNSET with bounded cancelled outcome/reason; re-raise cancellation |
| Deadline exhaustion or unexpected/unknown interruption | ERROR with bounded classification; re-raise cancellation/failure |

Required: use the same canonical error.type for equivalent handled and escaping
failures. Prefer a finite platform category, falling back to stable exception
class names; never messages, IDs, payloads, or raw URLs. Record an exception once
on a span, and log at the layer owning handling/final reporting. Do not manually
duplicate default SDK recording before re-raising. Specific handlers precede
a justified broad boundary fallback under [[Clean Code and Architecture]].

Catch CancelledError specifically only for classification/cleanup and re-raise.
A failed/cancelled consumer must not acknowledge success for prettier traces.
Test acknowledgement, cleanup, retries, and subsequent context isolation.

Related: [[Integration Boundaries]] · [[Observability and Logging]] ·
[[Tracing Acceptance]] · [[Tracing Sources]]
