# Distributed Tracing Standard for Python Microservices

**Stack:** Python 3.13 · FastAPI · FastStream · NATS / JetStream · HTTPX · SQLAlchemy · OpenTelemetry · OTLP · SigNoz  
**Document date:** 2026-10-01  
**Revision:** 1.3 — semantic-convention naming, deterministic policy selection, and rule-consistency corrections  
**Status:** Proposed platform standard; deployment conformance requires recorded test evidence.  
**Purpose:** One shared tracing, execution-context, and logging contract for independently deployed HTTP services and message-processing workers.

> Propagate OpenTelemetry **context**, not individual tracing identifiers. Read application metadata through a scoped `ContextVar` API. Application code uses standard Python `logging`; the startup-configured OpenTelemetry bridge supplies native correlation and export. OpenTelemetry remains the source of truth for active trace/span state.

## How to read this standard

**MUST / MUST NOT** are requirements of this proposed platform standard. **SHOULD / SHOULD NOT** are defaults that require a documented reason to override. **MAY** describes an optional choice. These requirements are not all requirements imposed by OpenTelemetry itself.

Conformance uses three distinct mechanisms:

| Mechanism | Meaning | Evidence treatment |
| --- | --- | --- |
| **Supported policy choice** | Selects one alternative already permitted by this standard. | Record the selected alternative and run the assertions for that alternative. It is not a deviation. |
| **Documented `SHOULD` override** | Departs from a recommendation for a stated reason. | Record the reason, owner, scope, and replacement/affected assertions. |
| **Approved `MUST` exception** | Explicitly waives one named mandatory rule for a bounded scope. | Record the rule ID/text, affected paths, approving authority, owner, validity/review date, replacement assertions, and approval impact. A waived assertion is reported as `exception`, never as `passed`. |

A supported policy choice MUST NOT be recorded as an exception merely because another permitted alternative is the platform default. Acceptance is evaluated against applicable requirements, the selected supported alternatives, documented `SHOULD` overrides, and explicit `MUST` exceptions.

Revision 1.3 builds on revision 1.2. It retains the typed ContextVars API and native logging-bridge rules, applies the naming/semantic-convention corrections reviewed against OpenTelemetry Semantic Conventions 1.44.0, and resolves the rule/acceptance inconsistencies identified in the consistency audit. The original 22-section structure and source provenance remain in force:

- **[S1]** `python_tracing_rules(1).md` — Python implementation rules, original sections 1–49.
- **[S2]** `signoz_tracing_integration_rules(1).md` — general distributed tracing contract, original sections 1–18.

Sections marked **Baseline** retain or deduplicate the inherited rules. **Microservice extension** marks platform policy. **Clarification** identifies corrections or qualifications. **Revision 1.1** identifies retained changes made after review. **Revision 1.2** identifies the local-context and logging-bridge requirements. **Revision 1.3** identifies semantic-convention naming corrections and deterministic conformance rules; it supersedes conflicting earlier wording. Appendix A retains the reconciliations, Appendix B the inherited source-coverage map, Appendix C technical references, and Appendix D the revision/verification record. The two earlier source files were not separately re-audited for revision 1.3.

A platform requirement, a library observation, and a verified implementation are different things. A version-specific observation does not establish the behavior of every release. Code examples are composable fragments unless explicitly stated otherwise; alternatives MUST NOT be installed together for the same boundary.

Service names, subjects, infrastructure addresses, and business operations below are illustrative. The supplied files do not establish your actual topology, dependency versions, gateway configuration, retry policy, or Collector configuration. This is a stack-specific standard, not a claim that your deployments already implement it.

## Contents

1. [Architecture and ownership](#1-architecture-and-ownership)
2. [The cross-service propagation contract](#2-the-cross-service-propagation-contract)
3. [Trace IDs, span IDs, and HTTP relationships](#3-trace-ids-span-ids-and-http-relationships)
4. [Service identity and telemetry initialization](#4-service-identity-and-telemetry-initialization)
5. [FastAPI ingress and gateways](#5-fastapi-ingress-and-gateways)
6. [Outgoing HTTP with HTTPX](#6-outgoing-http-with-httpx)
7. [FastStream and NATS boundaries](#7-faststream-and-nats-boundaries)
8. [Asynchronous trace boundaries, fan-out, and batches](#8-asynchronous-trace-boundaries-fan-out-and-batches)
9. [Retries, redelivery, and replay](#9-retries-redelivery-and-replay)
10. [Transactional outboxes and durable jobs](#10-transactional-outboxes-and-durable-jobs)
11. [SQLAlchemy and databases](#11-sqlalchemy-and-databases)
12. [Python execution context and concurrency](#12-python-execution-context-and-concurrency)
13. [Manual business spans and attributes](#13-manual-business-spans-and-attributes)
14. [Errors, exceptions, and cancellation](#14-errors-exceptions-and-cancellation)
15. [Python logging to OpenTelemetry and SigNoz](#15-python-logging-to-opentelemetry-and-signoz)
16. [Sampling across the architecture](#16-sampling-across-the-architecture)
17. [Baggage, security, and trust boundaries](#17-baggage-security-and-trust-boundaries)
18. [Collector delivery and graceful shutdown](#18-collector-delivery-and-graceful-shutdown)
19. [Dependencies and semantic conventions](#19-dependencies-and-semantic-conventions)
20. [Integration tests and acceptance criteria](#20-integration-tests-and-acceptance-criteria)
21. [Repository structure and rollout](#21-repository-structure-and-rollout)
22. [Compact implementation contract](#22-compact-implementation-contract)

[Appendix A — Reconciliations](#appendix-a-explicit-reconciliations-and-additions) · [Appendix B — Coverage](#appendix-b-coverage-of-the-supplied-files) · [Appendix C — References](#appendix-c-external-references) · [Appendix D — Revision and verification](#appendix-d-revision-history-and-verification-scope)

---

## 1. Architecture and ownership

**Baseline:** [S1, §§3–5, 33–35, 45]; [S2, §§1, 16, 18].  
**Microservice extension:** Shared ownership and deployment boundaries.

Tracing follows business traffic; exporting telemetry is a separate path:

```text
BUSINESS TRAFFIC

Client -> [Gateway / ingress] -> order-service (FastAPI)
                                  |
                                  +-- HTTPX -> payment-service (FastAPI)
                                  |
                                  +-- SQLAlchemy -> PostgreSQL
                                  |
                                  +-- FastStream -> NATS / JetStream
                                                       |
                                                       +-> notification-worker
                                                       +-> inventory-worker

TELEMETRY

Each service / worker -- OTLP traces --> OpenTelemetry Collector --> SigNoz
Each service / worker -- logging bridge / OTLP logs --> Collector -> SigNoz
```

A Collector may be the one deployed with SigNoz; a separate extra Collector tier is not inherently required. The native OTLP logs pipeline must be explicitly configured, not inferred from tracing setup; stdout collection must not duplicate that application stream.

Each process MUST initialize its own telemetry. Services MUST NOT share in-memory `Span` or `Context` objects across processes. A shared package MAY distribute configuration and helpers, but it is not a shared runtime context store.

Each operation MUST have one instrumentation owner:

| Boundary or responsibility | Owner |
| --- | --- |
| Incoming HTTP | `FastAPIInstrumentor` |
| Outgoing HTTP | One OpenTelemetry HTTPX integration: `HTTPXClientInstrumentor` **or** an explicit OpenTelemetry transport |
| Database operations through SQLAlchemy | `SQLAlchemyInstrumentor` |
| FastStream NATS publishing and processing | `NatsTelemetryMiddleware`, or one approved extension/replacement that passes section 7’s compatibility gate |
| Meaningful application operations | Application-owned manual spans |
| Local application context | Shared typed ContextVars API and one scope per request/message/job |
| Application log conversion and enrichment | One startup-configured stdlib-to-OpenTelemetry bridge; allowlisted metadata filter |
| Optional console formatting | Separate console handler, not the native OTLP body |
| Ingress context trust and baggage filtering | Gateway / outer ingress adapter, before tracing extraction |
| Egress propagation policy | Approved transport or messaging boundary adapter at the actual send path |
| Export routing, ingestion, retention, sampling infrastructure | Platform / observability configuration |

Do not combine framework auto-instrumentation with another manual or launcher-based instrumentor for the same boundary. In particular, do not add manual `SERVER`, HTTP `CLIENT`, or messaging spans around operations already covered by their instrumentors merely to obtain IDs. A filtering adapter MAY share the transport path without creating spans; it does not become a second tracing owner.

**Revision 1.1 — evidence ownership:** Every mandatory boundary behavior MUST name its implementation component and acceptance test. The presence of an instrumentor, configuration variable, or span in SigNoz is not sufficient evidence of conformance.

## 2. The cross-service propagation contract

**Baseline:** [S1, §§1, 6–7, 13–16, 24]; [S2, §§1–4, 7–8, 15].  
**Clarification:** Required tracing metadata is conditional on valid context; authentication and business metadata are separate.

| Metadata | HTTP | NATS / JetStream | Rule |
| --- | --- | --- | --- |
| `traceparent` | Request header | Message header | Inject for instrumented outbound operations with valid context; extract at ingress. |
| `tracestate` | Request header | Message header | Preserve through the propagator when present and permitted by trust policy. |
| `baggage` | Optional header | Optional header | Only approved keys, when intentionally enabled. |
| `X-Request-ID` or equivalent | Optional application contract | Not automatically a message ID | A support/request identifier, not an OpenTelemetry identifier. |
| Message ID, causation ID, workflow ID | Where the application needs them | Business envelope or application metadata | Independent application identifiers; never substituted for tracing IDs. |
| Authentication, tenant authorization, idempotency keys | Existing application/security contract | Existing application/security contract | Tracing does not supply or validate these. |

Canonical W3C wire format:

```http
traceparent: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01
```

The `trace_id` is 32 hexadecimal characters; the wire `parent-id` is 16 hexadecimal characters. The latter identifies the sending span, which the receiver can use as a remote parent. All-zero IDs are invalid. Validation and formatting MUST be delegated to the propagator, not implemented in application middleware. [W1]

Services MUST NOT introduce `X-Trace-ID`, `X-Span-ID`, or `X-Parent-Span-ID` as replacements for W3C context. Tracing identifiers MUST NOT be added to domain DTOs or business message bodies.

At incoming boundaries, absence of context is valid. Apply trust policy first, then delegate parsing to the configured propagator. At a boundary whose policy is trusted continuation:

| Received metadata | Required outcome |
| --- | --- |
| No `traceparent` | Start a new trace for the receiving operation; do not inherit an unrelated ambient worker span. |
| Invalid `traceparent` | Ignore the invalid parent and its associated `tracestate`; start a new valid trace. |
| Valid `traceparent`, malformed `tracestate` | Preserve the valid trace ID and remote parent span ID; discard invalid vendor state according to the propagator. |
| Valid unsampled `traceparent` | Continue valid context, including downstream propagation, even when spans are not exported. |
| Invalid or prohibited baggage | Discard/filter baggage independently; do not invalidate a valid trace parent because of baggage. |

**Revision 1.1:** Failure to parse `tracestate` MUST NOT invalidate an otherwise accepted, valid `traceparent`. Invalid trace metadata alone MUST NOT fail the business operation. Transport-level size limits, abuse controls, and an intentional public-ingress trace reset remain separate policies. [W1]

On ordinary instrumented outgoing paths, let the single tracing owner inject the HTTP client or new message-creation context into a per-operation carrier. Enforce destination policy before bytes leave the process. Suppressed/excluded HTTP paths follow the explicitly selected section 17.3 propagation mode rather than pretending a client span exists. Do not copy the original incoming `traceparent` unchanged into a new HTTP operation or newly created application message. Section 7 defines the compatibility gate for messaging libraries; broker redelivery of the same stored message is different from a new publication.

**Important:** A valid unsampled context is still valid context. Do not drop propagation or manufacture a new trace just because the current span is not recording. Logs may reference a trace that sampling does not retain. [W2]

## 3. Trace IDs, span IDs, and HTTP relationships

**Baseline:** [S1, §§9–10, 13, 17, 35, 40–41]; [S2, §§3–8].

OpenTelemetry MUST generate `trace_id` and `span_id`. Application code MUST NOT use UUIDs, request IDs, entity IDs, or message IDs as tracing identifiers. Every span in a trace has its own span ID; it does not reuse its parent's ID.

For normal trusted HTTP propagation:

```text
order-service
  SERVER: POST /orders                       span A
    INTERNAL: orders.create                  span B
      CLIENT: POST payment-service/payments  span C
        |
        | traceparent carries span C
        v
payment-service
  SERVER: POST /payments                     span D, parent C
    INTERNAL: payments.authorize             span E, parent D
```

All five spans share the trace ID. The span ID sent to `payment-service` is **C**, not A or B.

For a concrete incoming header:

```http
traceparent: 00-aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa-bbbbbbbbbbbbbbbb-01
```

an illustrative receiving server span is:

```text
trace_id        aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
span_id         cccccccccccccccc
parent span ID  bbbbbbbbbbbbbbbb
```

Those literals illustrate relationships; production IDs come from the SDK.

A root span has no parent. A span has at most one parent; additional causal relationships use links. `parent_span_id` describes a span relationship, not another independently generated identifier or a required field in the active `SpanContext`. [W3]

> The “same trace ID” rule applies within one trace. A long-running business workflow can deliberately consist of several linked traces; see sections 8–10.

## 4. Service identity and telemetry initialization

**Baseline:** [S1, §§3–5, 31, 38, 44–45].  
**Microservice extension:** Consistent resource identity and worker initialization.

Every service MUST set `service.name`. All services SHOULD also set `service.namespace`, `service.version`, and `deployment.environment.name`.

```text
service.namespace=commerce
service.name=order-service
service.version=a94ce12
deployment.environment.name=production
```

Replicas of the same logical service MUST use the same `service.name`. Never use `order-service-pod-abc` as the service name. Infrastructure identity belongs in separate resource attributes, such as Kubernetes pod metadata and, where configured, `service.instance.id`. When `service.instance.id` is used to identify a running service instance, it MUST identify one running instance and MUST NOT be shared by concurrently running replicas with the same `service.namespace` and `service.name`. [W47]

**Proposed naming policy:** Independently deployed HTTP and worker components MAY use distinct stable names, such as `order-api` and `order-worker`. Make that decision consistently; do not vary it by replica, tenant, request, or deployment rollout.

Initialize one `TracerProvider` per worker process, before serving requests or consuming messages. Initialize once after worker creation rather than relying on a provider created in a prefork master. Do not create a provider per request, per connection, or per task. Tests that need different provider configurations SHOULD use isolated processes or explicit test providers.

### 4.1 Example deployment configuration

This example uses explicit Python **gRPC** trace/log exporters. Section 15 configures the standard-library logging bridge and its batch log processor. Replace resource values and the Collector endpoint with your deployment configuration.

```bash
export OTEL_SERVICE_NAME=order-service
export OTEL_RESOURCE_ATTRIBUTES='service.namespace=commerce,service.version=a94ce12,deployment.environment.name=production'

# Example plaintext endpoint inside a controlled network.
# Use TLS and appropriate authentication wherever the deployment requires it.
export OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4317
export OTEL_EXPORTER_OTLP_PROTOCOL=grpc

export OTEL_PROPAGATORS=tracecontext
export OTEL_TRACES_SAMPLER=parentbased_traceidratio
export OTEL_TRACES_SAMPLER_ARG=0.1

# Manual bridge in section 15 owns OTLP logs; disable a second automatic bridge.
export OTEL_PYTHON_LOG_AUTO_INSTRUMENTATION=false
unset OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED
export OTEL_PYTHON_LOG_CORRELATION=false
```

The 10% root sampling ratio is an example, not a universal production recommendation. Start validation with 100% sampling on controlled test traffic.

`OTEL_PROPAGATORS=tracecontext` configures the global propagator. Verify that every framework integration follows the intended baggage policy; a library may also use a dedicated propagator.

### 4.2 Minimal explicit tracing bootstrap

```python
# infrastructure/telemetry.py
import os

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor


def configure_tracing() -> TracerProvider:
    """Call exactly once in each worker process before instrumentation."""
    service_name = os.environ.get("OTEL_SERVICE_NAME", "").strip()
    if not service_name:
        raise ValueError("OTEL_SERVICE_NAME must identify the logical service")

    # Resource.create also incorporates configured resource attributes.
    resource = Resource.create({"service.name": service_name})
    provider = TracerProvider(resource=resource, shutdown_on_exit=False)
    provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
    trace.set_tracer_provider(provider)
    return provider
```

This function configures **traces only**. At the same startup boundary, call `configure_logging(tracer_provider)` from section 15 to install native log export using the same resource; retain its returned `logging_runtime`. Metrics are configured separately. Explicit lifecycle shutdown is required because the reference providers disable automatic exit shutdown. Framework snippets below assume the tracing value is named `tracer_provider`.

The Python SDK reads sampler environment configuration when no explicit sampler is supplied. An explicit sampler overrides that choice. [W2]

**Clarification:** Importing the gRPC exporter chooses gRPC. Setting `OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf` does not turn that explicitly constructed class into an HTTP exporter. To use OTLP/HTTP, change the exporter implementation and endpoint configuration together. Do not mix manual bootstrap with an auto-configuring launcher without a deliberate ownership plan. [W4]

## 5. FastAPI ingress and gateways

**Baseline:** [S1, §§6–8, 33]; [S2, §§3–4, 16].  
**Microservice extension:** Gateway continuity and public ingress policy.

Use the FastAPI instrumentor to extract context, create and activate the `SERVER` span, and finish it. Do not parse `traceparent` or create an additional manual server span. Separately bind fresh application metadata using the pure-ASGI context boundary in section 12.3; application context is not another tracing instrumentor.

```python
from fastapi import FastAPI
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

app = FastAPI()

FastAPIInstrumentor.instrument_app(
    app,
    tracer_provider=tracer_provider,
    excluded_urls=r"^https?://[^/?#]+/(?:health|healthz|ready|readyz|metrics)/?$",
    exclude_spans=["receive", "send"],
)
```

Register instrumentation before the application starts accepting requests, not after its middleware stack is already serving traffic. Excluding ASGI `receive` / `send` spans is optional; it does not mean excluding the HTTP server operation. [W5]

**Revision 1.1 — precise exclusions:** The example excludes only the listed top-level diagnostic paths. It does not exclude `/orders/metrics` or `/tenants/acme/health`. Adapt it to explicitly approved mounted prefixes. The reviewed ASGI implementation matches a URL constructed from scheme, host, and path; its exclusion input does not include the query string. Verify that behavior against the locked version, including reverse-proxy prefixes. Do not use an unanchored suffix expression unless business routes with those suffixes are intentionally excluded. [W24]

Public-ingress header filtering or trace reset MUST run before the tracing owner extracts a remote parent. A request hook that runs after server-span creation is too late to change that span’s parent. Register and test the real middleware order rather than relying on file order.

A transparent, uninstrumented proxy SHOULD preserve approved context headers. An instrumented gateway MUST propagate its own outbound operation's context, not blindly forward the original inbound header.

At public ingress, choose and document whether to continue client-provided context or establish a new internal trace. The normal service-to-service rule is continuation inside the trusted platform. A gateway reset is an explicit trust-boundary exception, not permission for every internal service to create unrelated roots.

Trace context MUST NOT be treated as authentication or proof of a caller's identity. The platform must control whether untrusted clients can influence sampling; see sections 16–17.

**Optional support convention:** An API may expose a trace identifier or request identifier in its response under an approved API contract. This is not required for downstream propagation and does not replace outbound instrumentation. Do not describe response `traceparent` as a universal W3C requirement.

## 6. Outgoing HTTP with HTTPX

**Baseline:** [S1, §§13–14, 41]; [S2, §§7–8].  
**Microservice extension:** Shared client safety and untrusted destinations.

Select **one** HTTPX instrumentation mode per process/client strategy. The following global mode is appropriate only when every relevant outgoing path is covered by an approved egress-enforcement design. The explicit transport mode in section 17.3 is an alternative; do not combine it with this global mode:

Configure global HTTPX instrumentation once:

```python
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor

HTTPXClientInstrumentor().instrument(tracer_provider=tracer_provider)
```

Application code then uses HTTPX normally. The instrumentor creates the `CLIENT` span and injects its context. [W6]

```python
import httpx


async def authorize_payment(
    client: httpx.AsyncClient,
    payload: dict[str, object],
) -> None:
    response = await client.post(
        "http://payment-service/payments",
        json=payload,
    )
    response.raise_for_status()
```

The application lifecycle SHOULD own a reusable `AsyncClient` with explicit timeout and connection limits. Do not store request-specific trace headers in shared client defaults or a global dictionary: concurrent requests could then reuse another request's context.

Do not pass `trace_id`, `span_id`, or a home-grown `TracingContext` into this function. Do not forward incoming headers wholesale; authentication forwarding and tracing propagation have separate policies.

Third-party calls MUST remain covered by the approved client instrumentation. Recording and export remain subject to the configured sampler; a valid unsampled context need not produce a recording/exported client span. Destination policy controls wire propagation independently of recording. Do not assume global instrumentation implements an egress allowlist for you. Tests MUST distinguish instrumentation coverage, valid context, recording/export, and actual outgoing headers, including redirects to a differently trusted origin.

**Revision 1.1 — hook ordering:** In the reviewed HTTPX OpenTelemetry implementation, the instrumentation’s request hook runs before propagation headers are injected. Removing headers there is therefore not a reliable egress control. Use a reviewed transport layer after injection, an approved destination-aware integration, or an egress gateway with equivalent guarantees. Section 17.3 provides a transport pattern for a deny-baggage-by-default policy. [W23]

HTTPX clients that use the explicit transport pattern MUST have all application mounts and proxy routes reviewed. An alternate transport path that bypasses the policy wrapper is not conformant. Setting `follow_redirects=False` reduces automatic forwarding but does not replace policy checks when the application follows redirects itself. Suppressed/excluded tracing is a distinct mode, not ordinary unsampled tracing: the reference policy omits W3C propagation on those paths, while an explicitly approved propagation-only alternative may be selected and tested as described in section 17.3.

## 7. FastStream and NATS boundaries

**Baseline:** [S1, §§15–17, 42]; [S2, §15].  
**Clarification:** Actual messaging spans and relationships depend on middleware behavior and its semantic-convention version.

Use FastStream’s NATS OpenTelemetry integration as the default boundary owner, **subject to the compatibility gate below**. This setup fragment does not certify fresh-publication semantics:

```python
from faststream import FastStream
from faststream.nats import NatsBroker
from faststream.nats.opentelemetry import NatsTelemetryMiddleware

broker = NatsBroker(
    "nats://nats:4222",
    middlewares=(
        NatsTelemetryMiddleware(tracer_provider=tracer_provider),
    ),
)

worker_app = FastStream(broker)
```

This is an instrumentation fragment, not a complete durable consumer configuration. JetStream stream, durable consumer, acknowledgement, and retry settings are separate application concerns. When FastAPI and FastStream share a process, use the same process-local provider and one lifecycle owner. [W7]

The middleware owns message context injection/extraction and its producer/consumer tracing. The approved dispatch adapter separately binds per-delivery `AppContext` as required by section 12.4; it must not add duplicate messaging spans. Instrument all publisher and subscriber paths, including scheduled publishers and HTTP handlers that publish messages. Do not also instrument the same NATS operation through another tracing middleware or manually generated span.

The contract is:

```text
message headers / transport metadata:
    traceparent
    tracestate, when present
    baggage, only when approved

business envelope / body:
    event type, schema version, business data
    application message / workflow / causation IDs, when needed
    no manually managed trace_id, span_id, or parent_span_id
```

Headers MUST survive serialization, forwarding adapters, and broker delivery. For this platform, every **new message-creation operation** MUST obtain a fresh creation/publication context supplied by its boundary owner. A non-batch publication therefore creates a new context for that message. Messages produced by one explicitly declared batch-creation operation MAY share that batch creation context when the selected instrumentation model does so; the batch context MUST still be fresh relative to any consumed input. Derived events, application-created retries, dead-letter publications, and outbox dispatches MUST NOT accidentally reuse a previously received message’s creation context.

A byte-for-byte transport relay of an existing message MAY retain its original creation context under a documented forwarding policy. Classify such relays explicitly; do not label a new business event or retry as a relay just to avoid the new-publication requirement.

For a simple single-message continuation, the conceptual shape is:

```text
order-service: orders.create                    INTERNAL
  message creation / publication               PRODUCER
    |
    | NATS headers carry message creation context
    v
notification-worker: process orders.created     CONSUMER
  notification.send                            INTERNAL
```

Some instrumentors separate message creation and sending, or add receive/settle spans. The propagated creation context may therefore differ from the last span whose name contains “publish”. Verify the emitted carrier and graph rather than requiring an invented exact span sequence.

**Clarification:** A consumer need not always be a direct child of a producer or even share its trace ID. OpenTelemetry messaging conventions use links as the general correlation mechanism and permit parent-child continuation for individual messages. Section 8 defines how this platform uses those alternatives. The fresh-publication policy above is a platform requirement, not a claim that every alternative library model violates OpenTelemetry. [W8]

### 7.1 Version-specific compatibility gate

**Revision 1.1 — source observation:** FastStream **0.7.7** has a `publish_scope()` branch that, when an existing consumer span is recording, injects `_origin_context`. That branch can propagate the incoming message’s creation context rather than a fresh context for a newly created application message. Other paths create a new creation span. The source also uses dedicated trace/baggage propagators and middleware-local baggage. These observations apply to that tagged implementation; they do not establish behavior for your installed release or every publisher path. [W22]

Before approving a FastStream integration, capture the actual outgoing carrier for every path used by the service:

| Publication path | Evidence required |
| --- | --- |
| Direct publish from an HTTP handler | The emitted carrier identifies the fresh message-creation context. |
| Direct publish from a scheduler | The emitted carrier identifies the fresh creation context; parent/link relationship follows that execution’s policy. |
| Approved transparent byte-for-byte relay | The original message creation context MAY be retained under the documented forwarding policy; prove that the message is not transformed into a new application event. |
| Relay that creates/transforms a new application event | The emitted carrier identifies a fresh creation context; it MUST NOT reuse the relayed input’s creation context. |
| Publish inside a subscriber | Outgoing context is not the incoming message’s creation context for a newly created message. |
| Decorated publisher / handler-return publication | Verify separately; do not infer its behavior from direct publish. |
| New retry or dead-letter publication | Fresh creation context; application causation and idempotency remain separate. |
| Batch publish, when used | Declare whether the owner creates one fresh context per message or one fresh context for the explicit batch; verify that choice and the downstream link model. |

Run each applicable path with both sampled and unsampled incoming parents. The approved identity/relationship policy MUST NOT depend accidentally on `is_recording()`. Unsampled contexts are inspected at the carrier/API level, not by requiring exported spans.

If stock middleware fails this platform contract, the owner MUST use a reviewed upgrade or extension/replacement that passes the matrix, or obtain an approved `MUST` exception under the conformance mechanism defined above. The exception record MUST name the violated rule, version, affected paths, alternative causal model, owner, approving authority, replacement assertions, validity/review date, and approval impact. Do not edit middleware-private state from business handlers. Do not add a second producer span and assume that changes the injected headers.

### 7.2 Messaging semantic-convention contract

The approved messaging integration MUST be evaluated against the semantic-convention version recorded in the compatibility manifest. For the revision 1.3 baseline, use OpenTelemetry Semantic Conventions **1.44.0** as the review target and verify the actual attributes emitted by the locked integration rather than assuming support from an environment variable alone. [W8, W43]

For every approved create/send/receive/process/settle path that the selected instrumentation emits, capture the SDK-exported span and verify the applicable semantic-convention contract, including:

```text
semantic-convention span name
SpanKind
messaging.system
messaging.operation.name
messaging.operation.type
messaging.destination.name and/or messaging.destination.template
messaging.message.id when semantically available
messaging.message.conversation_id when semantically available
server.address / server.port when available and applicable
error.type on failed operations
absence of error.type on successful operations
parent/link relationship selected by policy
```

For the current generic messaging convention, operation kinds are expected to follow the convention used by the locked instrumentation: creation operations use `PRODUCER`; send operations use `PRODUCER` or `CLIENT` as applicable; receive operations use `CLIENT`; process operations use `CONSUMER`; settle operations use `CLIENT`. `messaging.system` and `messaging.operation.name` MUST be present where the selected 1.44.0 operation convention requires them. NATS-specific instrumentation MAY use the custom `messaging.system` value `nats` when no well-known registry value exists, provided the remaining generic messaging contract is satisfied. [W8, W45]

### 7.3 Messaging policy ownership

The approved messaging boundary owner MUST enforce the ingress and egress baggage policy against all relevant stores: transport headers, extracted OpenTelemetry context, and middleware-local baggage. Global `OTEL_PROPAGATORS` is not an override for every dedicated library propagator. A pre-handler filter that leaves the original headers or middleware-local baggage intact does not establish egress safety. No universal FastStream filtering switch is assumed by this standard. [W22]

A NATS integration is **not approved** merely because the constructor above succeeds. Section 20 requires actual carrier evidence, and section 21 defines the versioned reference implementation used to approve it.

## 8. Asynchronous trace boundaries, fan-out, and batches

**Microservice extension:** Proposed defaults for asynchronous workflow design, beyond the two original files.

A trace describes an execution episode; a business workflow may span many episodes. Do not try to keep one span open for an entire order lifetime, a human approval, or hours of delayed processing.

| Workflow shape | Proposed relationship policy |
| --- | --- |
| Synchronous internal HTTP call | Continue the current trace through client/server parentage. |
| One promptly processed message | Consumer processing SHOULD correlate to the message creation context using a span link. For an exclusively single-message processing operation, the approved instrumentation MAY instead use the creation context as the parent. The selected model MUST be documented and tested. |
| One event delivered to multiple independent subscribers | Each delivery owns its own processing span. All correlate with the message creation context; subscribers are not chained to one another. |
| Multiple messages processed in one batch | Either process each message under its own processing span using that message’s approved single-message parent/link policy, or use one combined batch operation linked to the contributing contexts. A combined operation MUST NOT choose one unrelated input as the parent. |
| Fan-in or aggregation across unrelated messages | Use links to the contributing contexts; retain application workflow identifiers separately. |
| Delayed job, replay, or long-running workflow step | Prefer a new execution trace linked to the initiating message or operation. |
| Scheduler tick unrelated to a request | Start a new root operation; never inherit a random previous request. |

A span has only one parent. For multi-input operations, span links express the additional causes without falsifying parentage. Link targets may belong to different traces. [W3, W8]

**Implementation rule:** These are policies, not undocumented FastStream configuration switches. A linked-root processing mode requires a supported middleware option or a reviewed replacement/extension of the existing boundary owner. Starting an extra root span inside an already instrumented consumer handler does not change the middleware's consumer span and can create duplicate or misleading operations.

For a custom, otherwise uninstrumented worker boundary, the SDK pattern is:

```python
from collections.abc import Awaitable, Callable

from opentelemetry import context as context_api
from opentelemetry import propagate, trace
from opentelemetry.context import Context
from opentelemetry.trace import Link, SpanKind

from shared_observability.context import AppContext, bind_context

tracer = trace.get_tracer(__name__)


async def run_linked_job(
    headers: dict[str, str],
    process: Callable[[], Awaitable[None]],
) -> None:
    # Adapter supplies a canonical string carrier, not a live Span object.
    origin = propagate.extract(headers, context=Context())
    origin_span = trace.get_current_span(origin).get_span_context()
    links = [Link(origin_span)] if origin_span.is_valid else []

    # Attach a clean context to avoid inheriting scheduler baggage as well
    # as its parent span. This example deliberately drops all baggage.
    token = context_api.attach(Context())
    try:
        with (
            bind_context(AppContext()),
            tracer.start_as_current_span(
                "jobs.process",
                kind=SpanKind.CONSUMER,
                links=links,
            ),
        ):
            await process()
    finally:
        context_api.detach(token)
```

This example also binds fresh empty application metadata; a real job adapter supplies its validated job/workflow fields. Clearing the OpenTelemetry context alone does not clear application ContextVars. This snippet is **not** an extra wrapper to add around `NatsTelemetryMiddleware`. Keep link counts bounded for large batches, and document truncation. A link does not merge trace IDs or automatically inherit the linked trace's sampling decision.

## 9. Retries, redelivery, and replay

**Microservice extension:** Proposed retry observability policy.

### 9.1 HTTP retries

A logical operation MAY own an `INTERNAL` span covering the complete retry budget. Each actual network attempt SHOULD have its own client span with a new span ID.

```text
payments.authorize              INTERNAL
  POST payment-service          CLIENT attempt 1, timeout
  POST payment-service          CLIENT attempt 2, success
```

Do not reuse the first attempt's span ID or cached `traceparent`. Keep the application idempotency key stable when retrying the same business operation; it is not a tracing identifier.

Instrumentation may observe one library invocation while lower-level transports retry internally. Verify retry visibility with the selected HTTPX transport and retry library. Do not promise one span per network attempt unless the instrumented boundary actually observes those attempts. Keep a single owner when adding missing attempt instrumentation.

For an HTTP `CLIENT` span representing a resend, use `http.request.resend_count` when the instrumentation exposes the standard attribute. A custom retry-attempt attribute MUST NOT replace `http.request.resend_count` on an HTTP span when that semantic-convention field is applicable. An enclosing application-owned span MAY additionally use the organization-owned `com.yourcompany.retry.attempt` attribute when that bounded business-level counter is useful. Do not put attempt numbers into the span name. A successful logical operation need not be marked failed merely because a child attempt failed. [W14]

### 9.2 Broker redelivery

Each handler execution MUST get a fresh processing span, including redeliveries of the same message. Preserve the broker-delivered creation context and apply the selected parent/link policy; never reuse an old consumer span.

Distinguish these cases:

| Case | Context rule |
| --- | --- |
| Broker redelivers the same stored message | Extract its existing creation context again; create a new processing span. |
| Application publishes a new retry message | Create a new publication context; preserve business causation and idempotency metadata separately. |
| Operator replays historical messages | Prefer a new replay execution trace with links to available original contexts. |

JetStream can redeliver messages when acknowledgements are not received within the configured policy. Trace success is not evidence that a message was acknowledged, and publication is not evidence that a consumer completed it. [W9]

Use approved metadata for delivery count and processing outcome, for example `com.yourcompany.delivery.attempt` and `com.yourcompany.processing.outcome`. Do not invent a parent relationship to a previous attempt whose span context you do not actually have.

### 9.3 Dead-letter and replay workflows

Instrument explicit publications to a dead-letter subject or stream. Keep a non-sensitive failure category and application message identity for diagnosis. Do not assume JetStream automatically creates a dead-letter queue when a delivery limit is reached; the dead-letter workflow must be implemented and verified separately.

Never use `trace_id` or `span_id` as a deduplication key. Where the application uses JetStream publication deduplication, `Nats-Msg-Id` belongs to the messaging reliability contract, not the tracing contract. [W10]

## 10. Transactional outboxes and durable jobs

**Microservice extension:** Proposed context preservation policy for deferred work. This does not require every service to adopt an outbox.

A database commit and a broker publication are separate effects. The original `repository.save()` followed by `broker.publish()` example illustrates tracing flow; it does not by itself define an atomic delivery strategy.

When an outbox is used, its infrastructure envelope SHOULD persist a serialized propagation carrier alongside the business message in the same database transaction. Keep this metadata separate from domain payloads. Persist strings such as approved `traceparent` / `tracestate`, not a live `Span`, Python `Context`, or SDK object.

```text
request trace
  orders.create
    database transaction:
      order row
      outbox row:
        business envelope
        propagation metadata

later, outbox relay
  outbox.dispatch: new execution trace linked to saved context
    NATS publication: new publication context in outgoing headers
      consumer: chosen parent/link policy
```

**Proposed default:** Deferred relays start short execution traces linked to stored origin context. A documented short-delay continuation policy is also acceptable. Never leave the original request span open while waiting for the relay.

After restoring context, let the outbound instrumentor create and inject the **new publication context**. Do not bypass it by copying the saved `traceparent` directly onto the wire. The saved carrier explains causality; it is not necessarily the final outbound carrier.

Treat each outbox entry independently. A relay batch that contains unrelated entries MUST NOT attach all of them to the first entry's trace. Use per-entry operations or a batch span with links. Both OpenTelemetry and application context must be restored after each entry even when dispatch fails. Bind a fresh `AppContext` for each entry; persist only approved business fields, never live ContextVars or reset tokens.

Retention of propagation metadata, baggage allowlists, retry limits, idempotency, and delivery guarantees belong in the outbox design. Tracing does not make a workflow durable or exactly-once.

**Durability clarification:** Publishing important work through NATS is not enough on its own. Core NATS and a configured durable JetStream workflow are different delivery choices. Business-critical jobs that must survive restarts need an explicitly configured durable mechanism, not an unawaited task or an assumption about the broker. [W11]

## 11. SQLAlchemy and databases

**Baseline:** [S1, §18].  
**Clarification:** “DB” describes an operation, not an OpenTelemetry span kind.

Instrument the highest useful database abstraction once. For an async SQLAlchemy engine:

```python
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

SQLAlchemyInstrumentor().instrument(
    engine=engine.sync_engine,
    tracer_provider=tracer_provider,
)
```

The snippet assumes `engine` is the application's existing `AsyncEngine`. Async SQLAlchemy instrumentation targets its synchronous engine interface. [W12]

Do not normally instrument both SQLAlchemy and asyncpg for the same query path. Separate layers are justified only when their additional visibility is intentional and tested; otherwise they create duplicate query spans.

Queries executed inside `orders.create` SHOULD be children of the span active during query execution. Do not flatten them under the HTTP server span when a more specific operation is active.

Database operations commonly use `SpanKind.CLIENT`. There is no `SpanKind.DB`; the original diagrams used “DB” as an informal label.

Do not add trace identifiers to database business records or query parameters merely to connect spans. Outbox propagation metadata is the explicit infrastructure exception described in section 10.

Disable parameter capture unless specifically approved. Parameterization alone does not guarantee safe telemetry: literal SQL, comments, connection strings, and exception messages can contain sensitive values.

### 11.1 Database semantic-convention contract

For database paths used by the service, acceptance MUST inspect SDK-exported database spans against the semantic-convention mode recorded in the manifest. Verify applicable stable fields such as `db.system.name`, `db.namespace`, `db.operation.name`, `db.query.summary`, `db.query.text`, `db.collection.name`, `db.response.status_code`, `error.type`, `server.address`, and `server.port`. A field that is not semantically applicable or not available from the instrumented operation need not be fabricated. [W46]

`db.query.parameter.<key>` remains opt-in. Do not enable query-parameter capture or unsanitized literal query text by default merely to satisfy an observability test. Privacy requirements take precedence over optional detail.

## 12. Python execution context and concurrency

**Baseline:** [S1, §§2, 19–23]; [S2, §§6, 15].  
**Revision 1.2 — required context-access contract:** Services MUST provide a small, typed `contextvars` API so infrastructure and application code can read current execution metadata without passing a context parameter through every layer.

“Available anywhere” means **any code executing inside the initialized request, message, or job context**, including its ordinary function calls and supported child tasks. It does not mean a process-wide dictionary, automatic cross-process sharing, or access to another request’s data.

### 12.1 Two contexts, separate responsibilities

| Concern | Source of truth | Access and ownership |
| --- | --- | --- |
| Current trace, span, flags, parentage | OpenTelemetry active context | Instrumentation owns activation. Read with `trace.get_current_span()` or the read-only helpers below. |
| Application request/workflow/message metadata | One module-level `ContextVar` holding an immutable `AppContext` | Boundary adapter binds it; application/infrastructure code reads it through helpers. |
| Cross-service trace propagation | Approved W3C transport carriers | Existing HTTP/NATS instrumentation, not the application `ContextVar`. |
| Cross-service business metadata | Validated application headers/envelopes; approved baggage only for its documented purpose | Explicit sender/receiver contract, independent of Python-local state. |
| Service name/version/environment | Process resource | Shared by trace and log providers; never request-context values. |

The default Python OpenTelemetry runtime uses `contextvars` internally. Application metadata and OpenTelemetry context therefore follow the same supported Python execution-context boundaries, but they are **different stores**. Neither is automatically copied into the other. Application `AppContext` values are not automatically baggage, span attributes, log attributes, or message headers. [W35, W36]

All consumers MUST import the same canonical context module. Creating another `ContextVar("app_context")` elsewhere creates a different key; matching variable names do not connect stores. The local Python variable name `app_context` is not an OpenTelemetry attribute namespace and is unaffected by the prohibition on custom `app.*` telemetry attributes.

Services MUST NOT introduce a second mutable tracing state store. In particular, do not save `trace_id`, `span_id`, `parent_span_id`, `Span`, or `SpanContext` in `AppContext` at ingress and later treat that snapshot as current. Nested spans change the active span. A read helper must consult OpenTelemetry **at the time it is called**.

### 12.2 Typed local access API

This reference module is import-safe: it declares helpers but does not initialize providers, add handlers, open connections, or bind a request. `ContextVar` declarations belong at module scope. The immutable default avoids a shared mutable dictionary. Python 3.13 uses explicit token reset in `finally`; do not use the token-as-context-manager syntax introduced in later Python versions. [W35]

```python
# shared_observability/context.py
from collections.abc import Iterator
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass

from opentelemetry import trace


@dataclass(frozen=True, slots=True)
class AppContext:
    request_id: str | None = None
    tenant_id: str | None = None
    user_id: str | None = None
    workflow_id: str | None = None
    message_id: str | None = None


_EMPTY = AppContext()
_app_context: ContextVar[AppContext | None] = ContextVar(
    "app_context", default=None
)


def get_context() -> AppContext:
    """Read local application metadata; return empty metadata outside a scope."""
    value = _app_context.get()
    return value if value is not None else _EMPTY


def require_context() -> AppContext:
    """Require an initialized scope, not a particular identity or permission."""
    value = _app_context.get()
    if value is None:
        raise LookupError("Application context is not initialized")
    return value


@contextmanager
def bind_context(value: AppContext) -> Iterator[AppContext]:
    """Bind in this execution context and restore on success or failure."""
    token = _app_context.set(value)
    try:
        yield value
    finally:
        _app_context.reset(token)


@dataclass(frozen=True, slots=True)
class TraceInfo:
    trace_id: str
    span_id: str
    trace_flags: str
    sampled: bool


def get_trace_context() -> TraceInfo | None:
    """Read the CURRENT OpenTelemetry span, including valid unsampled spans."""
    current = trace.get_current_span().get_span_context()
    if not current.is_valid:
        return None
    return TraceInfo(
        trace_id=f"{current.trace_id:032x}",
        span_id=f"{current.span_id:016x}",
        trace_flags=f"{int(current.trace_flags):02x}",
        sampled=bool(current.trace_flags.sampled),
    )


def get_trace_id() -> str | None:
    current = get_trace_context()
    return current.trace_id if current is not None else None


def get_span_id() -> str | None:
    current = get_trace_context()
    return current.span_id if current is not None else None
```

Application code can read metadata without adding tracing parameters to business signatures:

```python
from shared_observability.context import get_context, get_trace_context

# Anywhere INSIDE the current initialized execution:
metadata = get_context()
request_id = metadata.request_id
workflow_id = metadata.workflow_id

# Optional diagnostics/support response use, not normal log enrichment:
active = get_trace_context()
trace_id = active.trace_id if active is not None else None
```

`get_context()` returns empty metadata outside an initialized scope; `require_context()` raises in that case. Neither creates tracing identifiers or a new trace. `require_context()` only proves that a scope exists: it does not prove that `tenant_id` is present, a user is authenticated, or access is authorized.

A returned `TraceInfo` is a point-in-time snapshot. Read again after entering/leaving a span rather than caching it on a service instance. Keep normal calls such as `await order_service.create_order(command)`; do not add `trace_id`, `span_id`, or `tracing_context` arguments.

**Binding rules:** Every incoming request/message/job MUST start with freshly constructed metadata, not `replace(get_context(), ...)` based on unrelated ambient worker state. Nested enrichment inside the **same** operation MAY use immutable replacement:

```python
from dataclasses import replace

from shared_observability.context import bind_context, get_context

# Example: only after this operation's identity/tenant has been validated.
with bind_context(replace(get_context(), tenant_id=verified_tenant_id)):
    await application_service.execute(command)
```

Adapters MUST validate lengths, character sets, provenance, and privacy before binding untrusted fields. `AppContext` type annotations do not validate a request. Missing required tenant identity MUST fail closed at the authorization/data-access boundary, never fall back to an ambient default. Do not trust tenant/user identifiers merely because they appear in context.

Keep domain entities independent of this mechanism. Context MAY supply cross-cutting metadata in application/infrastructure code, but required domain inputs and security contracts must remain explicit and testable. Do not turn it into a service locator for database sessions, clients, mutable dictionaries, locks, credentials, or request bodies. Frozen dataclasses are only shallowly immutable; this example deliberately contains strings and `None`, not mutable nested objects.

### 12.3 FastAPI request lifetime: pure ASGI middleware

Use pure ASGI middleware for the application-context boundary, not `BaseHTTPMiddleware` or a synchronous dependency that sets a token in a worker thread. Starlette documents `BaseHTTPMiddleware` limitations for upward context propagation. Register and test actual ordering, including any existing middleware that creates tasks. [W37]

This middleware owns **only application metadata**. It creates no span, parses no W3C trace header, and does not replace `FastAPIInstrumentor`.

```python
# shared_observability/asgi_context.py
import re
from uuid import uuid4

from starlette.types import ASGIApp, Receive, Scope, Send

from shared_observability.context import AppContext, bind_context

_REQUEST_ID = re.compile(r"[A-Za-z0-9._:-]{1,128}")


class AppContextMiddleware:
    def __init__(
        self,
        app: ASGIApp,
        *,
        accept_incoming_request_id: bool = False,
    ) -> None:
        self.app = app
        self.accept_incoming_request_id = accept_incoming_request_id

    async def __call__(
        self, scope: Scope, receive: Receive, send: Send
    ) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request_id: str | None = None
        if self.accept_incoming_request_id:
            values = [
                value for key, value in scope.get("headers", [])
                if key.lower() == b"x-request-id"
            ]
            if len(values) == 1 and len(values[0]) <= 128:
                try:
                    candidate = values[0].decode("ascii")
                except UnicodeDecodeError:
                    candidate = ""
                if _REQUEST_ID.fullmatch(candidate):
                    request_id = candidate

        # This is an APPLICATION request ID, never an OpenTelemetry trace ID.
        metadata = AppContext(request_id=request_id or uuid4().hex)
        with bind_context(metadata):
            await self.app(scope, receive, send)
```

`accept_incoming_request_id` is a deployment policy, not a decision made from a caller-provided “trusted” header. The default generates a fresh application support ID. Accept an existing ID only under the approved ingress contract; it remains a correlation label, not an identity or uniqueness guarantee. A malformed/duplicated support ID here is replaced, not treated as invalid trace context. This example does not automatically echo or forward it.

Example composition with the existing instrumented FastAPI instance:

```python
from shared_observability.asgi_context import AppContextMiddleware

# `app` is the FastAPI instance instrumented in section 5.
# Serve `application` as the ASGI entry point; lifespan scopes pass through.
application = AppContextMiddleware(app, accept_incoming_request_id=False)
```

The intended nesting is ingress trust filtering → application context → OpenTelemetry HTTP boundary → authentication/validated enrichment → endpoint/application/repository. Trace trust filtering must still precede OpenTelemetry extraction. If your framework composes these differently, prove the resulting scope and parentage rather than installing a second instrumentor.

Bind context for the full awaited ASGI request invocation, including streaming response work that remains inside it; restore it even on exceptions and cancellation. This snippet scopes HTTP requests only. WebSockets require an explicit connection-versus-message scope policy. Framework access logs outside this invocation need their own tested adapter; they cannot be assumed to share its context.

Populate additional identity metadata in an **async** authenticated boundary scope that encloses the code using it. Do not set a `ContextVar` inside a sync FastAPI dependency and expect that change to appear back in the async endpoint. Likewise, do not transfer a reset token into a different task, thread, or dependency finalizer context. [W38]

### 12.4 FastStream / NATS message lifetime

The approved subscriber adapter MUST bind fresh `AppContext` metadata for **each delivery**, including retries and redelivery, in the same execution context that runs downstream handler code. Decode and validate application metadata first; obtain tenant/user information only from the application’s authenticated, authorized contract. Do not infer it from `traceparent` or caller-controlled baggage.

Use one common dispatch wrapper or approved middleware hook rather than global assignments or per-function context plumbing. The following reusable runner is independent of FastStream version:

```python
# shared_observability/message_context.py
from collections.abc import Awaitable, Callable
from typing import TypeVar

from shared_observability.context import AppContext, bind_context

T = TypeVar("T")


async def run_with_message_context(
    value: AppContext,
    handler: Callable[[], Awaitable[T]],
) -> T:
    """Scope one delivery without creating spans or changing acknowledgements."""
    with bind_context(value):
        return await handler()
```

The FastStream adapter calls this runner with a **new** `AppContext(message_id=..., workflow_id=...)` and the current handler callback. The runner does not extract tracing context, create a producer/consumer span, catch handler failures, acknowledge messages, or copy incoming tracing headers. `NatsTelemetryMiddleware` or its single approved replacement remains responsible for those tracing boundaries.

Place the scope around all work that needs the metadata, including post-handler/decorated publication and final reporting where applicable. A wrapper only around the Python handler body may end too early for framework-managed publishers or acknowledgement logs. The exact middleware hook and ordering are part of the locked FastStream adapter and must be tested; this runner is not a claim that a particular middleware hook has been implemented or certified.

Broker message metadata does not automatically populate `AppContext`, and binding `AppContext` does not automatically populate a new outgoing message. Forward only approved business fields through the documented envelope/headers. A batch of unrelated messages must use per-message scopes or a separate batch context, not the first message’s tenant/request identity.

### 12.5 Tasks, threads, executors, and context lifetime

| Execution boundary | Required behavior |
| --- | --- |
| Normal synchronous call / `await` | Read the caller’s active execution context; no tracing parameters. |
| `asyncio.create_task()` / `TaskGroup.create_task()` | By default, child work gets a snapshot of bindings at task creation; subsequent parent/child rebinding is not shared. |
| `asyncio.TaskGroup` | Prefer for scoped concurrent work whose lifetime belongs to the operation; ensure it finishes before scope exit. |
| `asyncio.to_thread()` | Copies current context when the `to_thread` coroutine runs; changes in the thread do not flow back. |
| Raw threads / `run_in_executor()` / custom executors | Do not assume propagation. Use a fresh `copy_context()` per submission when needed and test the actual executor. |
| Process pool / subprocess / another service | Local `ContextVar` state is not a transport contract. Serialize approved carrier/business metadata and initialize the receiving execution explicitly. |
| Long-lived startup worker consuming a queue | It does not dynamically acquire the submitting request’s context. Establish fresh state per job. |
| Detached or separately rooted work | Explicitly choose clean or captured context and parent/link policy; supervise its lifecycle. Never treat `create_task()` as a durable queue. |

Python task snapshots and thread handoffs are one-way propagation of bindings, not a shared mutable context. Resetting the parent’s token does **not** erase an already created child task’s copy. Resetting in `finally` prevents leaks in the owning execution; it is not a revocation mechanism for spawned work. Return results explicitly instead of expecting child-task/thread `ContextVar.set()` calls to update the parent. [W13, W38]

For a custom executor, copy context per submission, including both OpenTelemetry and application bindings:

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor
from contextvars import copy_context


def read_request_metadata() -> str | None:
    from shared_observability.context import get_context
    return get_context().request_id


async def read_in_executor(pool: ThreadPoolExecutor) -> str | None:
    loop = asyncio.get_running_loop()
    copied = copy_context()
    return await loop.run_in_executor(pool, copied.run, read_request_metadata)
```

Do not enter the same `Context` concurrently in multiple threads. Do not use `copy_context().run(async_function)` as a substitute for creating an async task in that context: calling an async function produces a coroutine; it does not run its awaited body there. [W35, W13]

For deliberately independent, supervised work, an empty **Python** context removes inherited application and OpenTelemetry bindings:

```python
import asyncio
import contextvars


async def run_independent_work() -> None:
    async with asyncio.TaskGroup() as group:
        group.create_task(independent_job(), context=contextvars.Context())
```

`independent_job()` is application-defined and must establish its new job metadata/span as needed. This example does not preserve causality; work caused by a prior operation may instead need an explicitly carried origin and linked trace. Choose that policy at the boundary, not inside arbitrary business functions.

**Do not confuse the two `Context` classes:** `contextvars.Context()` controls all Python context-variable bindings in that execution. `opentelemetry.context.Context()` contains only OpenTelemetry context values; attaching an empty OpenTelemetry context does **not** clear a separate application `ContextVar`. Linked jobs, outbox relays, and replay adapters must therefore reset/rebind application metadata independently. Do not replace the entire Python context in ordinary request code, where doing so would also discard legitimate tracing and library state. [W35, W36]

### 12.6 Unsupported transport adapters

Keep transport propagation in the single boundary owner. The existing propagator pattern is retained below; pair it with a fresh application-context scope if the adapter also invokes application code. Context objects and reset tokens never go on the wire.

```python
from opentelemetry import context as context_api
from opentelemetry import propagate, trace
from opentelemetry.context import Context
from opentelemetry.trace import SpanKind

tracer = trace.get_tracer(__name__)

# Sender: inside the one boundary owner's outbound operation.
with tracer.start_as_current_span("jobs.publish", kind=SpanKind.PRODUCER):
    headers: dict[str, str] = {}
    propagate.inject(headers)
    # Send business payload and headers through the unsupported transport here.

# Receiver: headers come from one received message, not a global dictionary.
parent_context = propagate.extract(headers, context=Context())
# Apply the approved baggage policy to the extracted context here.
# Activate the complete context, not only the span used for parentage.
token = context_api.attach(parent_context)
try:
    with tracer.start_as_current_span(
        "jobs.process",
        kind=SpanKind.CONSUMER,
    ):
        # Execute this message's handler here.
        pass
finally:
    context_api.detach(token)
```

Use the transport’s correct carrier getter/setter for byte-valued, case-sensitive, or multi-valued headers. An empty extraction base prevents parentless messages from inheriting stale worker trace context. Selecting a span parent with `context=` does not activate all extracted baggage by itself; attach the complete approved OpenTelemetry context when needed, and detach in `finally`. This remains separate from binding `AppContext`. [W21]

## 13. Manual business spans and attributes

**Baseline:** [S1, §§10–12, 34–36, 45–46]; [S2, §6].

Manual spans SHOULD explain meaningful latency, failures, dependencies, or business operations. They SHOULD NOT mirror every function call.

```python
import logging

from opentelemetry import trace

logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)


async def create_order(command: "CreateOrder") -> "Order":
    with tracer.start_as_current_span("orders.create") as span:
        span.set_attribute("com.yourcompany.payment.method", command.payment_method)
        order = await order_repository.create(command)
        logger.info("Order created")
        return order
```

This application sketch assumes the named DTOs and repository already exist. The active span automatically supplies parentage. Domain entities SHOULD stay independent of OpenTelemetry; instrument the application/service layer that coordinates the operation.

| Good span names | Avoid |
| --- | --- |
| `orders.create` | `orders.create.9827381` |
| `payments.authorize` | `payment-user-12345` |
| `inventory.reserve` | `reserve-item-<uuid>` |
| `users.resolve_permissions` | Spans for every DTO mapping or UUID parse |
| Route-template HTTP names | Raw URLs containing user IDs or query strings |

Prefer bounded attributes such as payment method, provider, cache hit, job type, and processing outcome. Before defining a custom attribute, check the semantic-convention registry for the version recorded in the compatibility manifest. Custom attributes MUST NOT use an OpenTelemetry semantic-convention namespace unless they implement that convention with its specified meaning and type. In particular, platform/application-defined attributes MUST NOT use `app.*` merely as a generic application prefix. Organization-specific attributes SHOULD use an organization-owned namespace, preferably reverse-domain based. This document uses `com.yourcompany.*` only as an illustrative placeholder; a production platform MUST substitute a namespace it controls. [W43, W44]

Identifiers MAY be recorded as attributes when investigation value, privacy, and storage costs justify them. High-cardinality trace attributes are not categorically prohibited, but IDs MUST NOT become span names or unbounded metric dimensions.

Never capture complete request/response bodies, message payloads, SQL values, or user text by default. `span.is_recording()` MAY guard expensive attribute preparation; it MUST NOT guard whether context gets propagated.

### 13.1 Messaging cardinality

**Revision 1.1 — platform policy:** Cardinality controls apply to auto-generated messaging span names and metric dimensions, not just manual business spans. A dynamic subject such as `orders.<order_id>.created` MUST NOT generate unbounded operation names or metric-label values in the approved integration.

Where the locked instrumentation supports it, use a stable messaging destination template, for example `orders.{order_id}.created`, following its supported semantic convention. Do not rename the real subject or pretend a template is the actual destination. If template support is absent, the approved application/instrumentation path MUST still bound relevant metric dimensions at or before SDK aggregation, using supported instrumentation, views, or another reviewed SDK-side mechanism. Collector transformations MAY additionally normalize backend-visible telemetry, but they do not satisfy the application-side metric-cardinality requirement. Trace attributes may retain the actual destination only when approved for privacy and storage cost. [W8]

Test spans **and** metrics emitted by the actual middleware with many distinct subjects. Acceptance for the application-side requirement observes SDK-exported span names and the SDK metric stream before Collector normalization. If a Collector transformation is also configured, test its output separately. A manual span around an automatically named publication does not fix the automatic span’s or metric’s cardinality.

## 14. Errors, exceptions, and cancellation

**Baseline:** [S1, §§29–30]; [S2, §14].  
**Revision 1.1:** Explicit application-span outcomes, bounded error classification, and cancellation handling.

Record failures where they add diagnostic value. Log an exception at the layer that owns its handling or final reporting, not at every layer that re-raises it. Error log severity, technical span status, business outcome, and broker acknowledgement are distinct decisions.

### 14.1 Application-span outcome policy

The following defaults are **platform policy for application-owned spans**, not overrides for automatic HTTP/database/messaging conventions. Services MUST document domain-specific exceptions.

| Outcome | Application-span status and attributes | Exception / control-flow behavior |
| --- | --- | --- |
| Operation completes normally | Leave status `UNSET`; omit `error.type`. Optionally record `com.yourcompany.operation.outcome=success`. | No synthetic exception event. |
| Expected negative business result, such as an ordinary payment decline | Leave status `UNSET`; record a bounded outcome such as `declined`. | Prefer a typed result; do not let an exception escape the observed operation and accidentally become a technical failure. |
| Missing required dependency result or unexpected validation/invariant failure | `ERROR`; bounded `error.type`; outcome `failed`. | Preserve the application’s failure contract. A 404 or validation label alone does not decide the business outcome. |
| Dependency timeout fails the operation | `ERROR`; `error.type=dependency_timeout`; outcome `failed`. | Return/raise the intended failure; preserve deadline semantics. |
| An attempt fails but a retry completes the logical operation | Keep failure evidence on the attempt span; leave the successful logical span `UNSET` without `error.type`. | Do not record recovered-attempt exceptions again on the successful logical operation. |
| Known expected client cancellation / orderly shutdown cancellation | Leave status `UNSET`; record outcome `cancelled` and a bounded reason. | Re-raise cancellation; `UNSET` is not a claim that the business action completed. |
| Deadline exhaustion, unexpected cancellation, or unknown cancellation that interrupts required work | `ERROR`; outcome `cancelled` or `failed`; bounded `error.type`. | Re-raise cancellation or preserve the owner’s timeout conversion. |

Use an approved finite error vocabulary or stable exception class names, not messages, IDs, URLs, or payloads. Equivalent application-owned failures MUST use the same canonical `error.type` classification whether the exception escapes the span scope or is handled inside it. Platform-defined categories take precedence when a category exists; for example, a dependency timeout that fails the operation uses `dependency_timeout`. Stable exception class names are the fallback for failures without a platform category. General OpenTelemetry error guidance recommends `error.type` for failed operations and distinguishes recovered attempts from final failure. That guidance is marked **Development** in the reviewed source; this document adopts the chosen behavior as explicit platform policy. [W25]

### 14.2 Escaping and handled exceptions

An ordinary `Exception` escaping a default SDK span context manager is normally recorded and marks that span as failed. Do not also call `record_exception()` before re-raising inside that same context manager. Add classification without duplicating the exception event. [W3, W21]

```python
from typing import Protocol

from opentelemetry import trace

tracer = trace.get_tracer(__name__)


class PaymentProvider(Protocol):
    async def authorize(self) -> None: ...


def classify_application_error(exc: Exception) -> str:
    if isinstance(exc, TimeoutError):
        return "dependency_timeout"
    return type(exc).__qualname__


async def authorize_with_failure_classification(
    payment_provider: PaymentProvider,
) -> None:
    with tracer.start_as_current_span("payments.authorize") as span:
        try:
            await payment_provider.authorize()
        except Exception as exc:
            span.set_attribute("error.type", classify_application_error(exc))
            span.set_attribute("com.yourcompany.operation.outcome", "failed")
            # The default context manager records the escaping exception once.
            raise
```

This is an application sketch; replace the provider with the service’s typed interface. An expected business decline must be handled as a business outcome within the operation, not routed through this generic failure path.

When an exception is handled inside an operation that nevertheless failed, record it once and set status explicitly:

```python
from opentelemetry.trace import Status, StatusCode

with tracer.start_as_current_span("payments.authorize") as span:
    try:
        await payment_provider.authorize()
    except TimeoutError as exc:
        span.set_attribute("error.type", "dependency_timeout")
        span.set_attribute("com.yourcompany.operation.outcome", "failed")
        span.record_exception(exc)
        span.set_status(Status(StatusCode.ERROR))
        logger.exception("Payment authorization timed out")
        # Return the application's explicit handled-failure result here.
```

This is not permission to swallow every exception. Recording exception messages, status descriptions, and stack traces requires an approved redaction policy. Where default automatic exception capture is unsuitable, the single owner must configure a safe alternative rather than record and redact later only.

For automatically instrumented HTTP spans, preserve HTTP conventions: server-side 4xx responses generally have different status guidance from client-side 4xx/5xx responses. Do not impose the business-span table globally on instrumentor-owned spans. [W14]

### 14.3 Cancellation and deadlines

`asyncio.CancelledError` is a `BaseException`, not an ordinary `Exception`. Catch it explicitly only to perform necessary classification/cleanup, then re-raise it. Do not catch it and return a successful handler result. Timeout scopes may translate their own cancellation into `TimeoutError`; classify at the layer that knows the deadline’s meaning. [W13]

The reviewed Python **1.42.1** API implementation’s span context path catches `Exception`, so an escaping `CancelledError` does not automatically receive the same error recording. Do not rely on that default to implement the table above. [W33]

```python
import asyncio

from opentelemetry.trace import Status, StatusCode

with tracer.start_as_current_span("inventory.reserve") as span:
    try:
        await inventory.reserve()
    except asyncio.CancelledError:
        # Conservative policy for an interruption whose cause is not known.
        span.set_attribute("com.yourcompany.operation.outcome", "cancelled")
        span.set_attribute("com.yourcompany.cancellation.reason", "unknown")
        span.set_attribute("error.type", "cancelled")
        span.set_status(Status(StatusCode.ERROR))
        raise
```

For a positively identified expected shutdown or client cancellation, record the approved reason and cancelled outcome without automatically marking a business failure. Do not infer the reason from an arbitrary exception message or mark every interruption as expected.

Consumer cancellation and failure MUST remain aligned with acknowledgement, negative acknowledgement, retry, and shutdown policy. A cancelled/failed handler MUST NOT become an acknowledged success solely to make traces appear successful. Test interrupted work, successful retries, cleanup, and subsequent message-context isolation together.

## 15. Python logging to OpenTelemetry and SigNoz

**Baseline:** [S1, §§25–28, 43]; [S2, §§9–14].  
**Revision 1.2 — required logging integration rules, reviewed 2026-10-01:** Application code uses normal Python logging; the startup-configured OpenTelemetry bridge handles native log conversion and trace correlation. This supersedes revision 1.1’s JSON-stdout-first example for this application log stream.

### 15.1 Application code uses standard logging

All request handlers, application services, repositories, database adapters, and message handlers MUST use standard library `logging` for application logs. Use a module logger; do not construct an OTLP exporter, call an exporter, or emit through the low-level OpenTelemetry Logs API from business code. Exporter/provider APIs belong in observability bootstrap and lifecycle code.

```python
import logging

logger = logging.getLogger(__name__)


def report_order_created(order_id: str, payment_method: str) -> None:
    logger.info(
        "Order created",
        extra={
            "com.yourcompany.order.id": order_id,
            "com.yourcompany.payment.method": payment_method,
        },
    )
```

The handler bridges standard `LogRecord` objects into OpenTelemetry records. Modules need no per-call trace-enrichment code, no special logger API, and no `trace_id`/`span_id` arguments passed down through their layers. Existing calls participate when their records reach the configured handler through the logging hierarchy. Logging below an effective level, `disabled` loggers, and `propagate=False` paths still require deliberate configuration. [W41]

Application code MUST NOT repeat trace/span IDs inside the log message or provide them through `extra`. Do not use `logger.info("trace=%s ...", get_trace_id())`, `extra={"trace_id": ...}`, a context argument on every log call, or a custom “tracing logger” in each repository. `extra` is for approved **business/event metadata**, not native tracing fields, resource identity, authorization claims, or unbounded payload dumps.

Keep event messages stable and human-readable. Application identifiers MAY be high-cardinality log attributes when privacy and investigation value justify them; they must not automatically become metric labels. Avoid reserved `LogRecord` names such as `message`, `name`, and `levelname` in `extra`. Use the organization-owned custom namespace defined in section 13 and supported, bounded values. `com.yourcompany.*` in this document is a placeholder, not a production namespace. [W41, W43]

### 15.2 Native correlation is separate from console formatting

The bridge reads OpenTelemetry’s active execution context when it handles the Python log record, creating native trace/span/flags fields. This covers ordinary calls throughout a request or message execution, including nested application spans, without duplicating the tracing state in `AppContext`. Valid unsampled/non-recording contexts still supply correlation identifiers. The bridge does not create a span merely because code logs a message. [W27, W40]

```text
logger.info(...) in handler / service / repository / adapter
    -> application metadata filter, in the emitting task/thread
    -> ONE OpenTelemetry logging bridge, in that same execution context
    -> native OTel log record with active trace/span/flags and service resource
    -> BatchLogRecordProcessor queue
    -> OTLP log exporter
    -> Collector logs pipeline
    -> SigNoz
```

`LoggingInstrumentor` record-factory enrichment (`otelTraceID`, `otelSpanID`, etc.) and `OTEL_PYTHON_LOG_CORRELATION` are **formatting/enrichment options**, not prerequisites for native correlation in the explicit bridge below. Current instrumentation can also install a bridge; therefore it is not safe to add it indiscriminately on top of a manually installed handler. [W15, W26]

The native bridge MUST keep the log body as the event message, not a JSON document or a console line decorated with timestamp, service name, and trace IDs. Do not put a trace-enriched formatter on the native handler. Optional console rendering is a separate handler concern, described in section 15.6.

No active span is a valid state, especially for startup and shutdown logs. Native records may carry absent/all-zero tracing fields to represent no correlation; presentation code should omit invalid IDs rather than display them as a real trace. Do not manufacture IDs or start a span just to fill a log field. A valid log trace ID does not guarantee that sampling/retention/export preserved the referenced trace.

### 15.3 Startup-only bridge and exporter configuration

Choose one logging-wiring owner per process. **This standard’s reference mode is explicit bootstrap:** create the log provider and batch processor once, then attach one bridge handler. A managed auto-instrumentation deployment MAY satisfy the same contract, but replaces this bootstrap rather than supplementing it. Initialize in each worker after worker creation, before serving or consuming work.

As checked on 2026-10-01, the SDK documentation deprecates `opentelemetry.sdk._logs.LoggingHandler` in favor of the handler in `opentelemetry-instrumentation-logging`. The reference uses the contrib handler import below. Pin and test a release exposing that API; do not silently fall back to the deprecated handler or combine both. The Python Logs SDK remains version-sensitive. [W39, W40]

This explicit mode disables **automatic handler installation**, not logging export:

```bash
# Exactly one manually installed bridge from configure_logging().
export OTEL_PYTHON_LOG_AUTO_INSTRUMENTATION=false
unset OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED

# No global console-format injection needed for native OTLP correlation.
export OTEL_PYTHON_LOG_CORRELATION=false

# Same resource identity and approved OTLP endpoint as section 4.
# OTEL_EXPORTER_OTLP_LOGS_* may override the general OTLP settings when needed.
```

The application metadata filter below is independent of trace enrichment. It executes on the bridge handler before native record conversion, even when no span is active. It includes only the approved request/workflow/message fields and deliberately does not copy tenant/user identity, secrets, arbitrary `ContextVar` values, or baggage. Context-owned keys cannot be overridden by ordinary `extra` fields.

```python
# shared_observability/log_context.py
import copy
import logging

from shared_observability.context import get_context

# Platform-owned log fields. Do not set these keys through application extra.
_CONTEXT_FIELDS = ("com.yourcompany.request.id", "com.yourcompany.workflow.id", "com.yourcompany.message.id")


class AppContextFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> logging.LogRecord:
        # Python 3.13 supports returning a replacement record from a filter.
        # A copy keeps enrichment local to this handler.
        enriched = copy.copy(record)
        for key in _CONTEXT_FIELDS:
            enriched.__dict__.pop(key, None)
        metadata = get_context()
        for key, value in (
            ("com.yourcompany.request.id", metadata.request_id),
            ("com.yourcompany.workflow.id", metadata.workflow_id),
            ("com.yourcompany.message.id", metadata.message_id),
        ):
            if value is not None:
                enriched.__dict__[key] = value
        return enriched
```

Attach this filter to the **handler**, not only the root logger: ancestor logger filters do not run for records propagated from descendant loggers. Returning a replacement `LogRecord` is supported on Python 3.13 and keeps this enrichment local to its handler. This filter is an allowlisted context mapper, not a general redaction engine. Validate inputs before binding; separately redact sensitive messages, `extra`, and exception diagnostics. [W41]

The returned runtime object owns log-provider shutdown:

```python
# shared_observability/log_lifecycle.py
import logging
from dataclasses import dataclass, field

from opentelemetry.sdk._logs import LoggerProvider


@dataclass(slots=True)
class LoggingRuntime:
    provider: LoggerProvider
    bridge: logging.Handler
    _closed: bool = field(default=False, init=False)

    def shutdown(self) -> None:
        """Run once after business work and its final logs have been drained."""
        if self._closed:
            return
        self._closed = True
        logging.getLogger().removeHandler(self.bridge)
        try:
            # Best effort; not a SigNoz-ingestion acknowledgement or hard deadline.
            self.provider.force_flush(timeout_millis=5_000)
        finally:
            try:
                self.provider.shutdown()
            finally:
                self.bridge.close()
```

Install the native bridge using the same resource as the trace provider:

```python
# shared_observability/logging_bootstrap.py
import logging
import os

from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.instrumentation.logging.handler import LoggingHandler
from opentelemetry.sdk._logs import LoggerProvider
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.trace import TracerProvider

from shared_observability.log_context import AppContextFilter
from shared_observability.log_lifecycle import LoggingRuntime


def configure_logging(tracer_provider: TracerProvider) -> LoggingRuntime:
    """Call once per worker in the explicit-bootstrap deployment mode."""
    root = logging.getLogger()
    if any(isinstance(handler, LoggingHandler) for handler in root.handlers):
        raise RuntimeError("An OpenTelemetry logging bridge is already installed")
    if os.getenv("OTEL_PYTHON_LOG_AUTO_INSTRUMENTATION", "").lower() != "false":
        raise ValueError("Disable automatic bridge installation in explicit mode")
    if os.getenv("OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED", "").lower() == "true":
        raise ValueError("Disable the deprecated SDK automatic logging handler")

    provider = LoggerProvider(
        resource=tracer_provider.resource,
        shutdown_on_exit=False,
    )
    try:
        provider.add_log_record_processor(
            BatchLogRecordProcessor(OTLPLogExporter())
        )
        bridge = LoggingHandler(level=logging.INFO, logger_provider=provider)
        bridge.addFilter(AppContextFilter())
        # No trace-ID/JSON formatter: the bridge creates native correlation fields.
        root.setLevel(logging.INFO)
        root.addHandler(bridge)
    except Exception:
        provider.shutdown()
        raise
    return LoggingRuntime(provider=provider, bridge=bridge)
```

Composition at the service’s existing worker startup:

```python
# Inside the process startup owner, before requests/messages begin:
tracer_provider = configure_tracing()
logging_runtime = configure_logging(tracer_provider)
```

The named functions are the modules in sections 4 and 15. Import them in the service composition root. The explicit handler receives its provider directly; the example does not require a global log provider. A deployment using `LoggingInstrumentor` to install the handler instead must configure the provider that instrumentor actually uses and prove identical ownership/correlation behavior.

The duplicate-handler check in this fragment is a guard, not a complete inspection of launcher configuration, deprecated handlers, child loggers, or server log configuration. Audit those once at startup. A child logger with its own OTLP handler and `propagate=True` can duplicate records. Later `dictConfig`/`basicConfig(force=True)` calls can change logging routing; framework/server configuration must preserve the approved handler and propagation policy. Do not initialize handlers per request or repeatedly reconfigure root logging.

`BatchLogRecordProcessor` queues native records after correlation has been captured. It avoids making an OTLP network round-trip a requirement for every log call. Keep queue sizes, exporter timeouts, retry behavior, and drop/error monitoring bounded. Process-level export failure must not deliberately turn otherwise valid business work into a failure. [W42]

### 15.4 Service resources and business attributes

Use one trusted process resource for both trace and log providers. `service.name` is required; include stable `service.namespace`, deployment version, `deployment.environment.name`, and instance metadata as configured in section 4. Never change service identity per request or copy it from a user-supplied log field.

| Information | Source | Native OpenTelemetry destination |
| --- | --- | --- |
| Event time | Python `LogRecord.created` through the bridge | Timestamp |
| Severity | Standard logging level | Severity number/text |
| Event message | Standard logging message/arguments | Body |
| Current trace ID/span ID/flags | Active OpenTelemetry context at bridge execution | Native correlation fields, not business attributes |
| Service name/version/namespace/environment | Process `Resource` shared with tracing | Resource attributes |
| Approved event-specific metadata | `extra={"com.yourcompany.*": ...}` using the organization-controlled production prefix | Log attributes |
| Approved local request/workflow/message metadata | `AppContextFilter` at emission | Allowlisted log attributes |
| Exception diagnostics | `logger.exception()` / `exc_info`, after approved redaction | Exception attributes as supported by the bridge |

Adding `service.name` to `extra` does not set the log’s resource. Adding `trace_id` to `extra` does not establish correct native trace correlation. Both are prohibited substitutes under this standard. Reserved context-owned fields (`com.yourcompany.request.id`, `com.yourcompany.workflow.id`, `com.yourcompany.message.id`) are supplied centrally; event-specific fields such as `com.yourcompany.order.id` remain available through `extra`. Replace the illustrative `com.yourcompany` prefix with the organization-controlled production namespace. [W27, W40, W43]

The bridge may include exception messages and stack traces. `logger.exception()` is appropriate at the error-reporting owner, not at every layer that re-raises. Apply section 14’s error ownership and section 17’s privacy rules; context enrichment alone provides no automatic protection against secrets in exception text.

### 15.5 Queueing and thread boundaries

**Required default:** Run the OpenTelemetry bridge directly on the emitting task/thread, then let `BatchLogRecordProcessor` queue the already-correlated native record. Do not put a standard `QueueHandler`/`QueueListener` in front of the bridge unless a reviewed adapter explicitly captures and restores the originating context before native conversion.

A listener thread has its own context. Even an enriched Python record containing `otelTraceID` and `otelSpanID` is not proof that the bridge will use those values for native fields: the reviewed handler looks up active OpenTelemetry context during conversion. Simply preserving extra strings is insufficient for a queued native bridge. [W31, W40]

Application metadata must likewise be captured before any off-thread enrichment would consult another execution’s `AppContext`. Our `AppContextFilter` is designed for the direct-bridge path, not for reading context later in a listener. A console-only queue may use its own emission-time snapshot, but must not cause native logs to be exported again. Retaining a full copied Python context in an unbounded queue can retain unrelated objects and sensitive state; prefer bounded, approved metadata when no native-context restoration is necessary.

### 15.6 Optional console output; no duplicate backend delivery

Console output is optional and independent of OTLP export. Plain console logs need no trace-ID formatting. When local troubleshooting requires console IDs, configure emission-time enrichment and the console formatter centrally; never change application log calls or concatenate IDs into their messages.

A console-only handler can enrich a **copy** of its record so those display fields do not leak into native log attributes. With console queueing, capture context on the emitting side and format the captured snapshot later. Formatters outside the originating execution must not call `get_context()` or `get_trace_context()` and assume they will retrieve the request’s values.

Do not collect the same application records from stdout/files and export them through the native bridge to the same backend. During migration, choose one backend delivery route, disable or route away the overlapping collector stream, and test record counts. Other streams, such as container/runtime logs, can keep their own collection pipeline. Revision 1.1’s JSON Trace Parser/filelog example is no longer the default or an additional pipeline for this application stream.

### 15.7 Collector / SigNoz ingestion and shutdown

The Collector must have an OTLP receiver enabled in its **logs** pipeline, with approved processors, resource handling, destination, authentication, and TLS. A traces-only pipeline does not receive logs merely because both use the same endpoint. Native OTLP records already carry correlation fields and resources; they do not need a JSON Trace Parser to manufacture them. A JSON-to-native mapping is relevant only to separate, explicitly chosen JSON collection streams. [W27]

Acceptance requires inspecting native log fields and testing trace-to-log and log-to-retained-trace navigation in SigNoz. Include multiple service resources, nested spans, unsampled context, no-span logs, and actual backend delivery. A missing trace may be due to sampling, retention, delayed export, or telemetry loss; do not “repair” it with invented IDs. [W17]

Drain business work and emit final application logs before shutting down the log provider. Keep logging available while trace shutdown may report diagnostics, then invoke `logging_runtime.shutdown()` in the single lifecycle owner. `logging.shutdown()` only handles Python logging and is **not a replacement** for `LoggerProvider.shutdown()`. The provider must be shut down so its processors/exporter are drained and closed. Section 18 defines the combined sequence. Shutdown/flush remain best effort: abrupt termination, queue overflow, and exporter failure can lose records; a return value is not a SigNoz-ingestion acknowledgement. [W42]

## 16. Sampling across the architecture

**Baseline:** [S1, §31].  
**Microservice extension:** Separate head sampling, tail sampling, and trust policy.

Within a continued trace, use parent-aware sampling. Downstream services MUST NOT make unrelated root decisions at every hop.

```bash
# Example head-sampling configuration:
export OTEL_TRACES_SAMPLER=parentbased_traceidratio
export OTEL_TRACES_SAMPLER_ARG=0.1
```

All services SHOULD share a documented default policy. Root rates can differ for explicitly different workloads, but the platform must understand which components start roots and which honor parents.

Do not remove `traceparent` on unsampled traffic. Propagation and recording are separate concerns. A new linked trace makes a new root sampling decision unless a custom sampler deliberately uses links; parent-based sampling does not automatically follow a linked context. [W2]

Public-client sample flags are untrusted input. Do not accidentally allow arbitrary callers to force unlimited telemetry. Apply an explicit ingress sampling/trust policy without breaking continuation randomly inside the platform.

### Tail sampling

Tail sampling decides after observing exported spans. It cannot reconstruct spans already discarded by head sampling. A design that aims to retain errors based on late outcomes must export enough spans for that decision and budget the corresponding traffic. [W18]

When scaling a tail-sampling tier, route all spans of a trace to the same sampling Collector. An ordinary load balancer that distributes batches arbitrarily is insufficient. Size decision windows, memory, queues, and late-span handling for real asynchronous delays. [W19]

Do not promise “all errors retained” unless the entire collection path, timing assumptions, and capacity justify it. Avoid very long continuation traces when they exceed practical tail-sampling windows; linked execution traces are often easier to operate.

## 17. Baggage, security, and trust boundaries

**Baseline:** [S1, §§12, 24, 37]; [S2, §§1–2].  
**Revision 1.1:** Named enforcement owners and an executable default HTTP egress pattern.

Local `AppContext` is not baggage. Only explicit approved boundary adapters may map its business metadata onto the wire; trace/log providers must not indiscriminately export its fields. Never rely on a tenant/user value being trustworthy merely because it is available through `get_context()`.

Default global propagation configuration:

```bash
export OTEL_PROPAGATORS=tracecontext
```

Enable baggage only for a documented use case, with a corresponding enforcement implementation:

```bash
export OTEL_PROPAGATORS=tracecontext,baggage
```

Baggage is cross-service data, not automatically a span attribute or log field, and its values are not inherently trustworthy. It MUST NOT contain secrets, tokens, passwords, cookies, personal data, or credentials. Authorization and tenant isolation MUST NOT depend on caller-controlled baggage. [W20]

### 17.1 Required boundary policy

The service/deployment configuration MUST identify the component and tests that enforce each applicable boundary:

| Boundary | Required enforcement | Owner / ordering |
| --- | --- | --- |
| Public ingress | Apply the declared continue/reset policy; strip prohibited baggage and unapproved vendor state. | Gateway or outer ingress adapter **before** tracing extraction and server-span creation. |
| Trusted internal ingress | Continue approved trace context; filter baggage independently; do not inherit unrelated ambient context. | Ingress tracing/propagation adapter. |
| Trusted HTTP egress | On ordinary instrumented paths, inject current client context; send only approved baggage/vendor state. Suppressed/excluded paths follow the manifest-selected propagation mode. | HTTP boundary owner plus final transport policy. |
| Unapproved HTTP origin | Keep the path covered by client instrumentation; remove W3C propagation fields by default. Span recording/export remains sampler-dependent. | Policy layer after injection and before network I/O. |
| Redirect | Re-evaluate the actual target origin for each request. | The same enforced send path; no bypassing mounts/proxies. |
| NATS consume and publish | Apply approved policies to carrier headers, extracted context, and middleware-local baggage. | The approved FastStream boundary adapter; verify its hook ordering. |
| Durable storage / outbox | Persist only the approved carrier; reapply destination policy on dispatch. | Outbox adapter and sending boundary. |
| Telemetry export | Authenticate/encrypt as required; redact and limit captured data. | SDK configuration and collection pipeline. |

If the platform chooses to allow trace propagation to a third-party origin, record that origin and which of `traceparent`, `tracestate`, and baggage are allowed. Approval of one field is not approval of all fields. Match normalized scheme, host, and effective port; do not use a suffix check such as `endswith("trusted.example")`.

### 17.2 Baggage allowlists and source data

Baggage is denied by default. An exception MUST define approved keys, value types/allowed values, maximum encoded value size, maximum total carrier size, permitted destinations, retention, and an owner. Fixed, non-sensitive categories are preferable to arbitrary free text. Limits are platform choices, not fabricated universal OpenTelemetry limits.

Filter before use and before propagation. Remove disallowed entries from all context stores the selected integration can consult, and remove stale baggage already present in outgoing carriers. Checking only `OTEL_PROPAGATORS` or only the current OpenTelemetry context is insufficient for libraries with dedicated propagators or local baggage. FastStream 0.7.7 is a version-specific example; see section 7. [W22]

Telemetry MUST NOT indiscriminately capture authorization headers, cookies, bodies, SQL parameters, connection credentials, or message payloads. Review exception messages, status descriptions, and logs too. Redact at the source where possible and add collection-side safeguards. Trace identifiers are not credentials or integrity proofs. [W1, W20]

### 17.3 HTTPX default egress enforcement pattern

The following async composition implements the default: **no baggage to any destination**, trace context only to approved origins, and no caller-supplied/cached W3C carrier state. The outer cleaner removes pre-existing propagation fields **before** the OpenTelemetry owner can inject; the inner destination policy runs **after** injection and before network I/O:

```text
AsyncClient
  -> CleanPropagationInputTransport   removes caller-supplied/cached trace fields
    -> AsyncOpenTelemetryTransport     creates CLIENT span when not suppressed; injects context
      -> PropagationPolicyTransport    removes fields prohibited for the actual destination
        -> AsyncHTTPTransport          sends the actual request
```

For suppressed/excluded tracing, the reference policy is **omit propagation**: the cleaner still removes pre-existing W3C fields, the tracing owner may create no client span and inject nothing, and the destination policy still executes. A platform MAY select a propagation-only alternative for trusted destinations, but that is a supported policy choice that requires an explicit reviewed adapter, manifest entry, and acceptance assertions; it MUST NOT be inferred from ordinary unsampled tracing.

The explicit OpenTelemetry transport is an alternative to section 6’s global `HTTPXClientInstrumentor().instrument()` setup. Do not install both for this client or globally instrument the inner transport. The order matters: an outer stripping wrapper could run before injection and let prohibited fields be re-added. [W6, W23]

```python
# infrastructure/http/propagation_policy.py
import httpx
from opentelemetry.instrumentation.httpx import AsyncOpenTelemetryTransport
from opentelemetry.sdk.trace import TracerProvider

type Origin = tuple[str, str, int]


class CleanPropagationInputTransport(httpx.AsyncBaseTransport):
    def __init__(self, transport: httpx.AsyncBaseTransport) -> None:
        self._transport = transport

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        # Business/request code is not allowed to pre-populate tracing carriers.
        # Removing them here also prevents stale tracestate from surviving when
        # instrumentation is suppressed and therefore injects no replacement.
        for name in ("traceparent", "tracestate", "baggage"):
            if name in request.headers:
                del request.headers[name]
        return await self._transport.handle_async_request(request)

    async def aclose(self) -> None:
        await self._transport.aclose()


class PropagationPolicyTransport(httpx.AsyncBaseTransport):
    def __init__(
        self,
        transport: httpx.AsyncBaseTransport,
        trusted_origins: frozenset[Origin],
    ) -> None:
        self._transport = transport
        self._trusted_origins = trusted_origins

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        scheme = request.url.scheme.lower()
        host = request.url.host.lower()
        port = request.url.port
        if port is None:
            port = 443 if scheme == "https" else 80
        trusted = (scheme, host, port) in self._trusted_origins
        blocked = ("baggage",) if trusted else (
            "traceparent", "tracestate", "baggage"
        )
        for name in blocked:
            if name in request.headers:
                del request.headers[name]
        return await self._transport.handle_async_request(request)

    async def aclose(self) -> None:
        await self._transport.aclose()


def build_http_client(provider: TracerProvider) -> httpx.AsyncClient:
    limits = httpx.Limits(max_connections=100, max_keepalive_connections=20)
    network = httpx.AsyncHTTPTransport(limits=limits, retries=0, trust_env=False)
    policy = PropagationPolicyTransport(
        network,
        trusted_origins=frozenset({("http", "payment-service", 80)}),
    )
    traced = AsyncOpenTelemetryTransport(policy, tracer_provider=provider)
    clean_input = CleanPropagationInputTransport(traced)
    return httpx.AsyncClient(
        transport=clean_input,
        timeout=httpx.Timeout(10.0, connect=2.0),
        follow_redirects=False,
        trust_env=False,
    )
```

HTTPX supports custom transport wrapping and explicit transport/proxy configuration; this fragment uses that extension point. [W34]

Origins, timeouts, limits, and the plaintext internal example are deployment choices; substitute approved values. The application lifecycle owns `await client.aclose()`. This pattern controls W3C propagation headers, not all HTTP data, network access, SSRF, or authorization forwarding. Do not enable additional propagation formats without extending and testing the policy. It deliberately disables implicit environment proxies; an approved proxy/mount configuration must preserve the same wrapper order.

Enabling baggage requires an explicit reviewed extension; changing an environment variable alone must not disable the deny-all baggage behavior. Approved `tracestate` handling within trusted origins is carried only from the context injected after `CleanPropagationInputTransport` removes caller-supplied/cached state; add a per-vendor policy where needed. Continue to prohibit caller-supplied/cached trace headers in business request code.

Test this exact composition with an actual receiving HTTP server, including redirects, concurrent callers, valid unsampled context, excluded/suppressed tracing paths, and manually supplied prohibited headers. Under the reference suppressed/excluded mode, assert that no tracing propagation fields reach the receiver and that the security filters still run. If the manifest selects the propagation-only alternative, assert that explicitly instead. A transport-only test proves filtering logic, not the full deployed instrumentor/proxy chain.

## 18. Collector delivery and graceful shutdown

**Baseline:** [S1, §§3–4, 38].  
**Microservice extension:** Independent failure domains and multi-service operations.

Use OTLP, `BatchSpanProcessor` for traces, and `BatchLogRecordProcessor` behind the logging bridge for application logs. A standard OpenTelemetry SDK is sufficient; business code SHOULD NOT depend on a SigNoz-specific tracing SDK.

Telemetry export MUST NOT become a synchronous requirement for each business request. Configure bounded exporter queues, timeouts, retries, and operational alerts. Collector unavailability should degrade observability, not deliberately make otherwise valid requests fail.

The platform SHOULD monitor export failures, dropped telemetry, queue pressure, and missing resource identity. Do not use an exporter failure as a reason to reset trace IDs or disable context propagation.

Only one lifecycle owner should shut down process-local telemetry. Drain business work first, then flush telemetry after the relevant spans have ended:

```text
stop accepting new HTTP requests / message deliveries
    -> finish or cancel in-flight work according to application policy
    -> close clients and workers while telemetry is still available
    -> emit final business logs and end operation spans
    -> flush/shut down tracing while the log bridge remains available
    -> detach the bridge, flush/shut down the log provider
    -> close remaining local logging outputs and terminate
```

The following helper shuts down **traces only**; the combined helper below is the application lifecycle entry point:

```python
import asyncio

from opentelemetry.sdk.trace import TracerProvider


def _shutdown_tracing_sync(provider: TracerProvider) -> bool:
    try:
        # Best-effort SDK drain request, not an ingestion acknowledgement.
        return provider.force_flush(timeout_millis=5_000)
    finally:
        provider.shutdown()


async def shutdown_tracing(tracer_provider: TracerProvider) -> bool:
    # Keep sequential flush/shutdown work together off the event loop.
    return await asyncio.to_thread(_shutdown_tracing_sync, tracer_provider)
```

### 18.1 Combined trace and log shutdown

Use one owner, after HTTP handlers, message handlers, supervised tasks, and their final logs have drained. Keep sequential shutdown work in one thread, rather than launching concurrent provider shutdown calls:

```python
import asyncio

from opentelemetry.sdk.trace import TracerProvider

from shared_observability.log_lifecycle import LoggingRuntime


def _shutdown_telemetry_sync(
    tracer_provider: TracerProvider,
    logging_runtime: LoggingRuntime,
) -> None:
    try:
        _shutdown_tracing_sync(tracer_provider)
    finally:
        # Called even if trace flush/shutdown raises.
        logging_runtime.shutdown()


async def shutdown_telemetry(
    tracer_provider: TracerProvider,
    logging_runtime: LoggingRuntime,
) -> None:
    await asyncio.to_thread(
        _shutdown_telemetry_sync, tracer_provider, logging_runtime
    )
```

This builds on `_shutdown_tracing_sync` immediately above. Call the combined entry point once, not it and the traces-only helper independently. Log-provider shutdown drains/closes its processors and exporter; Python `logging.shutdown()` alone does not replace it. Do not emit new application records after the bridge has been detached. Provider error diagnostics need a non-recursive local fallback route. The lifecycle owner serializes shutdown; `LoggingRuntime` is not a concurrently callable shutdown coordinator.

### 18.2 Delivery and timeout qualifications

**Revision 1.1 — limits of `force_flush()`:** Its boolean is an SDK flush result, not proof of successful exporter delivery, Collector acceptance, or SigNoz ingestion. The requested timeout is not automatically a hard wall-clock bound. In the reviewed SDK **1.42.1** batch-processor implementation, the flush path does not enforce its timeout and returns `True` after the export path without interpreting the exporter’s success/failure result. This is a tagged implementation observation, not a promise about every version. [W32]

The example’s five seconds is therefore a requested budget, not a guarantee for even the flush call itself. Configure exporter transport timeouts and retries independently, and measure flush plus shutdown with real queue sizes. Account for the sequential log-provider flush/shutdown and any metrics provider too. Apply the same best-effort interpretation to buffered log delivery; verify the locked implementation rather than treating a flush boolean as an ingestion acknowledgement.

Moving work to `asyncio.to_thread()` keeps it off the event loop; it does not make synchronous exporter code forcibly cancellable. Timing out or cancelling the awaiting coroutine does not reliably stop the underlying thread. Do not start a second concurrent shutdown after an async timeout. The lifecycle owner must coordinate graceful termination, with the process supervisor supplying the final termination boundary. [W13]

Acceptance MUST cover a slow exporter, an exporter returning failure, a Collector outage, and process termination with in-flight work. Record elapsed time and observed export/drop behavior separately from the flush return value. Do not infer successful ingestion from that return value.

Flush once during shutdown, not after every request. A flush only exports spans already ended. Abrupt termination can still lose buffered telemetry.

For Kubernetes, set `terminationGracePeriodSeconds` to cover the measured drain and export budget. Use infrastructure time synchronization so cross-service timestamps remain useful; parent relationships are not inferred from clock order.

## 19. Dependencies and semantic conventions

**Baseline:** [S1, §§32, 44].  
**Clarification:** Shared compatibility policy, not unverified “latest” pins.

Typical dependency set:

```bash
uv add \
  opentelemetry-api \
  opentelemetry-sdk \
  opentelemetry-exporter-otlp \
  opentelemetry-instrumentation-fastapi \
  opentelemetry-instrumentation-httpx \
  opentelemetry-instrumentation-sqlalchemy \
  opentelemetry-instrumentation-logging \
  "faststream[nats,otel]"
```

Use project lockfiles and test the resolved set on Python 3.13. Do not independently force the same numeric version onto the SDK, contrib instrumentors, and FastStream; their version schemes differ. The dependency command is a package inventory, not a reproducible installation recipe or complete application dependency list. Add the application’s actual web server, database driver, and test dependencies to its own project.

**Revision 1.1 — approval artifact:** Before declaring a service template conformant, publish a runnable reference implementation and its committed lockfile. That lockfile, exact runtime/container versions, approved boundary adapters, and passing acceptance evidence form the implementation contract. The Markdown file does not substitute for them.

Record Python’s exact patch version; resolved API/SDK/exporter/contrib/FastStream versions; the lockfile hash; reference-project commit; Collector distribution/version/image digest; NATS/JetStream and SigNoz versions; semantic-convention mode; and deviations. Do not treat the review’s FastStream 0.7.7 or SDK 1.42.1 observations as recommended production pins or as a tested full stack.

The following is a **manifest schema example**, deliberately not an approval record. Populate it with actual artifacts and CI results; `null`, empty mappings, or `not_run` must block approval:

```yaml
standard_revision: "1.2"
validation_status: "not_run"
python_version: null
reference_commit: null
lockfile_sha256: null
resolved_packages: {}
container_images: {}
semantic_conventions:
  version: "1.44.0"
  http: null                 # stable | legacy | duplicate | not_applicable
  database: null             # stable | legacy | duplicate | not_applicable
  messaging: null            # actual emitted mode | not_applicable
  stability_opt_in: null     # migration mechanism; not the SemConv version
feature_usage:
  http: null                 # used | not_applicable
  database: null
  messaging: null
  outbox: null
http_instrumentation_mode: null
suppressed_http_propagation: "omit"  # omit | approved_propagation_only
messaging_adapter_version: null
messaging_consumer_correlation: null # links | single_message_parent | not_applicable
batch_publication_context: null      # per_message | shared_batch | not_applicable
context_api_version: null
logging_bridge_mode: "explicit"
logging_bridge_version: null
log_ingestion_config_sha256: null
boundary_policy_config_sha256: null
acceptance_report: null
policy_choices: {}
should_overrides: []
must_exceptions: []
not_applicable: {}
```

A populated approval manifest MUST replace every applicable `null` with a concrete value. The literal `not_applicable` is permitted only when `feature_usage` marks that capability unused and the `not_applicable` map records a justification and evidence owner. A supported policy choice goes in `policy_choices` and the dedicated mode fields; a `SHOULD` override goes in `should_overrides`; a `MUST` waiver goes in `must_exceptions`. Do not hide an exception in a free-form “deviations” list.

The `contextvars` module is part of Python 3.13; do not install a backport package for this runtime. Lock the actual logging bridge package/API and context-adapter implementation along with other dependencies.

Library, Collector, middleware, or semantic-convention upgrades MUST rerun the applicable tests. A dependency resolver completing successfully is not evidence that propagation semantics remain unchanged.

Retain one approved semantic-convention policy across services and align SigNoz queries, dashboards, and alerts with emitted attributes. Record the semantic-convention **version** and the actual HTTP/database/messaging mode separately in the manifest. `OTEL_SEMCONV_STABILITY_OPT_IN` is a migration mechanism, not the semantic-convention version itself. For instrumentations that support these migrations, migration opt-ins may include:

```bash
export OTEL_SEMCONV_STABILITY_OPT_IN=http,database,messaging
```

For a controlled migration, supported duplicate modes may be used temporarily:

```bash
export OTEL_SEMCONV_STABILITY_OPT_IN=http/dup,database/dup,messaging/dup
```

**Clarification:** These settings are not proof that every installed instrumentor emits every stable convention or honors every listed token. Check support and actual output for each locked component. Messaging conventions and middleware implementation choices must be checked separately; the manifest records the actual emitted mode. Do not silently rename attributes or assert that an environment variable establishes compliance by itself. [W8, W43]

## 20. Integration tests and acceptance criteria

**Baseline:** [S1, §§39–43].  
**Microservice extension:** Architecture-level correctness rather than single-service span existence.

Use an in-memory exporter for focused span assertions and a real Collector/SigNoz path for ingestion tests. Use real HTTP and real NATS/JetStream in integration tests; a mocked publisher cannot establish that headers survive actual transport and redelivery. Isolated containers or processes keep global instrumentation from leaking between services and tests.

Acceptance assertions MUST identify their observation point. Unless a row says otherwise: carrier assertions are observed at the actual receiver; current-context assertions use the active API context; span-name/attribute assertions inspect SDK-exported spans before Collector transformation; metric-cardinality assertions inspect the SDK metric stream before Collector transformation; Collector-output assertions are explicitly labeled; native-log assertions use the native exporter/Collector/backend path named by the test. A downstream transformation MUST NOT be used to claim that an upstream SDK requirement passed.

Test behavior, not randomly generated literal IDs. Fixed inbound IDs are useful test inputs, but SDK-generated child IDs must be compared relationally.

### 20.1 Required test matrix

| Scenario | Assertions |
| --- | --- |
| HTTP with no context | A valid root server span is created; the business request succeeds. |
| HTTP with invalid `traceparent` | Invalid parent and associated vendor state are ignored; a fresh valid trace is used; business request succeeds. |
| Valid `traceparent`, malformed `tracestate` | Valid incoming trace ID and remote parent remain; local span ID is new; invalid vendor state is discarded. |
| Invalid / prohibited baggage | Filter baggage independently; retain an otherwise valid accepted trace parent. |
| HTTP with valid trusted context | Same trace ID; remote parent preserved; new server span ID. |
| Unsampled inbound context | Context still propagates; absence of exported spans is not treated as broken propagation. |
| A → B → C over HTTP | Each server has the corresponding outbound client as parent; all remain in one continued trace. |
| Gateway → API | Intended preserve/reset trust policy is observable on the real wire. |
| Manual business operation | Database and outbound spans are under the context actually active during the operation. |
| NATS single-message delivery | Carrier is present; processing correlates through the configured parent or link; no tracing IDs in business payload. |
| Each FastStream publication API in section 7 | Classify the path as new publication, approved transparent relay, or explicit batch creation; capture emitted headers and prove the applicable creation-context rule. Do not infer decorated publisher behavior from direct publish. |
| FastStream sampled / unsampled consume-to-publish | Approved creation-context policy holds in both cases; use carrier/API assertions for unsampled traffic. |
| Concurrent messages / HTTP requests | Neither AppContext nor OpenTelemetry context leaks between requests, tasks, or handlers; reset occurs on failure/cancellation too. |
| Fan-out | Separate processing spans; subscribers do not become each other's children. |
| Per-message batch processing | Each message has its own processing operation and application-context scope; that operation follows the approved single-message parent/link policy for that message. |
| Combined batch / fan-in operation | Relevant contributing inputs are linked; no unrelated inputs falsely share one selected parent. |
| HTTP retries | Attempt visibility matches the approved instrumentation design; attempt span IDs are distinct. |
| JetStream redelivery | Same application message identity; new processing span for each attempt. |
| New retry publication | New publication context is injected, not a stale original header. |
| Outbox dispatch | If the approved outbox policy persists propagation metadata, verify that the saved carrier survives restart, the relay relationship matches policy, and the outgoing carrier reflects the new publication. If persistence is omitted under a documented `SHOULD` override, verify the recorded replacement causal behavior and absence of an accidental ambient parent. |
| Delayed/replayed job | New linked trace or documented continuation; no accidental ambient worker parent. |
| Nested-span logging | Native log IDs match the active span at direct bridge execution; batching retains those values after scope exit. |
| Log outside a trace | No fabricated trace; native absent/zero correlation remains valid and display omits invalid IDs; ingestion accepts the record. |
| Unsampled or non-recording log context | Valid IDs are included without requiring a retained trace or `is_recording()`. |
| Native log fields and resources | Ingested correlation, full flags, timestamp, severity, body, and service resource match section 15; inspect native records rather than console text. |
| Exception handling | Correct status and exception events; no duplicate event on the same span from manual-plus-automatic recording. |
| Business outcome / recovered retry | Expected result is distinguished from failure; successful logical operation has no stale `error.type`; failed attempts retain evidence. |
| Cancelled handler | Reason/outcome/status follow section 14; cancellation propagates; acknowledgement and subsequent context isolation are correct. |
| Task / thread / process boundaries | Documented propagation works; separately rooted work does not inherit stale context. |
| Baggage / sensitive data | Forbidden fields are absent from real carriers, all middleware baggage stores, and exported telemetry. |
| HTTP egress and redirects | Prohibited fields are absent at actual receivers for direct and redirected requests; instrumentation coverage is verified, while recording/export remains sampler-dependent. |
| Egress with suppressed/excluded tracing | Security filtering still executes; alternate transports/proxies cannot bypass it; the receiver observes the manifest-selected mode (`omit` in the reference policy, or the explicitly approved propagation-only alternative). |
| Noise and instrumentation ownership | Only approved diagnostic routes are excluded; `/orders/metrics` and other non-approved suffix matches remain traced; no duplicate owners. |
| Messaging semantic conventions | SDK-exported messaging spans satisfy the applicable section 7.2 span-name, SpanKind, required/recommended attribute, error, and parent/link assertions for the manifest-recorded mode. |
| Database semantic conventions | SDK-exported database spans satisfy the applicable section 11.1 stable-schema fields for the manifest-recorded mode without enabling prohibited sensitive capture. |
| Messaging cardinality | Many dynamic subjects do not create unbounded SDK-exported span names or SDK metric dimensions before Collector normalization; any Collector normalization is tested separately. |
| Collector outage / recovery | Requests remain functional; telemetry degradation is detectable and queues remain bounded. |
| Graceful shutdown | Measure drain, flush, shutdown, and final process termination against the operational budget; account for incomplete export. |
| Slow exporter / exporter returns failure | Record duration, return value, and observed delivery separately; do not equate `True` with successful export or a hard timeout. |
| SigNoz ingestion | Service identity is correct; trace-to-log and log-to-trace correlation work for retained traces. |

### 20.2 Concrete HTTP assertions

```text
B.SERVER.trace_id       == A.CLIENT.trace_id
B.SERVER.parent.span_id == A.CLIENT.span_id
B.SERVER.span_id        != A.CLIENT.span_id
```

For three services, repeat that assertion for B's client and C's server. Do not compare C's parent to A's server span.

### 20.3 Concrete messaging assertions

For parent-based processing:

```text
consumer.trace_id       == propagated_creation_context.trace_id
consumer.parent.span_id == propagated_creation_context.span_id
consumer.span_id        != propagated_creation_context.span_id
```

For link-based processing:

```text
one of consumer.links matches propagated_creation_context
consumer owns a new span_id
trace equality is required only when the chosen model calls for it
```

If middleware introduces intermediate spans, assert the documented causal path through those spans rather than falsely requiring direct parentage. Include the actual emitted header in test evidence.

For every **new** application publication after consumption, also assert:

```text
(outgoing_creation.trace_id, outgoing_creation.span_id)
    != (incoming_creation.trace_id, incoming_creation.span_id)
outgoing_carrier identifies the fresh creation context selected by its owner
new_creation relates to this execution according to the approved parent/link model
```

For a same-trace new publication, also assert that the new creation span ID differs from the incoming creation span ID. For a deliberately new trace, compare the full `(trace_id, span_id)` pair rather than treating a bare span ID as globally unique. Do not require the outgoing carrier to identify the last span whose name happens to contain `publish`; some integrations separate creation from sending. For unsampled traffic, use propagator extraction and observed active contexts, not an exporter that correctly receives no spans.

### 20.4 Architecture smoke test

Exercise one complete path:

```text
POST /orders
  -> orders.create
  -> PostgreSQL
  -> payment-service over HTTP
  -> publish orders.created
  -> notification-worker processing
  -> correlated application log
```

Run both successful and failed variants. Inspect service names, span kinds, carrier values, parent/link relationships, errors, and logs. The test passes because the causal graph is correct, not merely because SigNoz shows several spans.

### 20.5 Test implementation and evidence requirements

Every matrix row MUST map to one of: (1) a passing test/evidence artifact for the applicable selected policy, (2) a justified `not_applicable` entry for a workload that truly does not use that feature, or (3) an approved `MUST` exception with its replacement assertions and evidence. A feature in use cannot be marked not applicable because testing is inconvenient. A supported policy choice selects which assertions apply; it is not a waiver. A documented `SHOULD` override must identify the affected assertion and replacement evidence. A waived assertion MUST remain visibly `exception`, never silently `passed`.

| Test tier | What it establishes | What it does not establish |
| --- | --- | --- |
| Unit / SDK probe | Parsing, formatter output, filtering logic, context relationships in a controlled process. | Actual broker delivery, deployed middleware ordering, or backend ingestion. |
| Real transport integration | HTTP/NATS carriers, concurrency, retries, redelivery, redirects, and lifecycle behavior. | Correct SigNoz-native fields without an ingestion test. |
| Collector integration | Configuration loads on the locked binary; logs/spans have expected native fields/resources; loss/error paths are visible. | Retention or UI navigation without the backend path. |
| SigNoz acceptance | Actual service identity and navigation between retained traces and logs. | Loss-free telemetry under every load or abrupt failure. |

Keep real HTTP receiver captures, real NATS header captures, exported span relationships, native log records, and shutdown measurements as CI artifacts using synthetic non-sensitive fixtures. Evidence must identify the manifest, config hash, test commit, and run result. Bound polling for eventual ingestion instead of using an arbitrary sleep as the assertion. A screenshot may supplement, not replace, structural assertions.

Useful reference test names include `test_valid_parent_invalid_state`, `test_new_message_context_by_publish_path`, `test_publish_context_under_sampling`, `test_redirect_egress_policy`, `test_bridge_before_batch_queue`, `test_cancellation_ack_policy`, `test_slow_and_failed_exporter`, and `test_business_route_exclusions`. These are required test intents, not a claim that those functions already exist in a repository.

### 20.6 Small executable SDK regression test

This isolated test demonstrates the corrected parent/state rule. It needs `pytest` and `opentelemetry-sdk`; it neither configures the global provider nor proves HTTP middleware behavior. Run its equivalent through the real ingress instrumentor as well.

```python
# tests/test_valid_parent_invalid_state.py
from opentelemetry import trace
from opentelemetry.context import Context
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator


def test_valid_parent_invalid_state() -> None:
    headers = {
        "traceparent": "00-aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa-bbbbbbbbbbbbbbbb-01",
        "tracestate": "invalid-state-without-equals",
    }
    parent = TraceContextTextMapPropagator().extract(headers, context=Context())
    origin = trace.get_current_span(parent).get_span_context()
    assert origin.is_valid and origin.is_remote
    assert origin.trace_id == int("a" * 32, 16)
    assert origin.span_id == int("b" * 16, 16)
    assert not origin.trace_state

    exporter = InMemorySpanExporter()
    provider = TracerProvider(shutdown_on_exit=False)
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    try:
        with provider.get_tracer(__name__).start_as_current_span(
            "receive", context=parent
        ):
            pass
        (received,) = exporter.get_finished_spans()
        context = received.get_span_context()
        assert context is not None and context.is_valid
        assert context.trace_id == origin.trace_id
        assert context.span_id != origin.span_id
        assert received.parent is not None
        assert received.parent.span_id == origin.span_id
    finally:
        provider.shutdown()
```

### 20.7 ContextVars acceptance requirements

These requirements apply to the shared API **and** each service's real boundary adapters. Tests of a helper alone do not certify middleware ordering.

| Scenario | Required assertions |
| --- | --- |
| Read outside an initialized scope | Empty application metadata; strict accessor raises; no fabricated trace/span. |
| Deep service/repository calls | Helpers return the active operation’s values without tracing parameters. |
| Concurrent requests/deliveries | Distinct request/message/tenant metadata; no cross-operation overwrite. |
| Nested binding | Inner values are visible only inside their scope; previous binding restores afterward. |
| Exception and cancellation | Application token is reset; OpenTelemetry owner restores its state; cancellation propagates. |
| Nested spans | `get_trace_context()` follows current span IDs and restores the outer ID; no ingress-time cache. |
| Valid non-recording/unsampled span | Read helpers still return valid IDs and flags. |
| Tasks and TaskGroup | Initial inheritance works; rebinding does not flow back or sideways. |
| Parent exits before copied child | Child retains its snapshot; lifecycle supervision prevents unintended detached work. |
| `to_thread` / custom executor | Read propagation matches policy; worker rebindings do not modify the caller; no thread reuse leak. |
| Empty Python vs OpenTelemetry context | Clean Python task has neither context; clearing only OTel does not silently clear AppContext. |
| Streaming HTTP / framework access logs | Metadata lifetime and middleware ordering match the intended full invocation. |
| FastStream decode/publish/finalization | Required stages run inside the correct application scope; no extra tracing owner. |
| Process boundaries / outbox / replay | Only approved serialized metadata travels; new execution binds fresh metadata. |
| Binding has no side effect | Merely binding `AppContext` emits no telemetry and does not alter headers, baggage, or payloads. |
| Approved log-context mapping | When a log is emitted, the handler-side allowlist adds the approved request/workflow/message attributes; fields without an approved mapping are not exported merely because they exist in `AppContext`. |
| Wire privacy | Local context fields do not cross process/service boundaries unless an explicit approved application metadata or baggage contract maps them. |
| Tenant/authentication | Untrusted fields cannot select authorization scope; required identity fails closed when absent. |

### 20.8 Logging bridge acceptance requirements

Use the real approved bridge package with an in-memory native exporter for local assertions, then repeat through the Collector/SigNoz path. SDK compatibility probes are useful but do not substitute for testing the bridge actually deployed.

| Scenario | Required assertions |
| --- | --- |
| Ordinary `logging.getLogger(__name__).info(...)` | Under a controlled healthy duplicate-routing test, exactly one native log reaches the configured path without per-call trace metadata. This is not a loss-free delivery guarantee under exporter failure or abrupt termination. |
| Handler → service → repository | Same active trace; each log reflects the span actually current at emission. |
| Nested spans and unsampled context | Correct native TraceId/SpanId/flags without `extra` IDs or console-format injection. |
| Business `extra` | Approved business attributes arrive; native trace/resource fields are not replaced. |
| Context enrichment without a span | Allowlisted request/workflow/message data remains available; no fabricated trace. |
| Resource identity | Trace/log resources agree across at least two services; caller metadata cannot impersonate a resource. |
| Export after scope end | Batch queue preserves origin correlation and metadata; listener context is never substituted. |
| Log levels and propagation | Expected records from application/framework loggers reach the bridge; suppression is intentional. |
| Duplicate paths | No manual-plus-auto bridge, ancestor/child duplicate handler, or stdout-plus-OTLP duplicate ingestion. |
| Message and exception privacy | No trace IDs embedded in body; no secrets in body, extra, exception attributes, or unapproved context fields. |
| Shutdown and exporter failure | Provider shutdown is invoked after final logs; flush failure does not skip provider cleanup; delivery is measured separately. |
| Backend ingestion | Native fields and service resources survive; SigNoz can navigate retained trace/log relationships. |

## 21. Repository structure and rollout

**Baseline:** [S1, §§3, 33, 45–49].  
**Microservice extension:** Shared implementation and rollout policy.

```text
shared-observability/             optional, versioned package
  bootstrap.py                   provider and resource conventions
  context.py                     typed ContextVars bindings and live trace readers
  asgi_context.py                pure-ASGI request scope
  message_context.py             per-delivery application scope
  log_context.py                 allowlisted business-metadata enrichment
  logging_bootstrap.py           one stdlib-to-OTel bridge and batch exporter
  log_lifecycle.py               owned log-provider shutdown
  propagation.py                 supported policy extensions / custom boundaries
  testing.py                     reusable behavioral assertions
  compatibility.py               approved integration/version metadata

order-service/
  src/
    domain/                      no tracing plumbing
    application/                 meaningful manual operation spans
    infrastructure/
      telemetry.py               service-specific composition
      db/
      http/
      messaging/
    api/app.py
    main.py                      lifecycle ownership
```

The shared package SHOULD NOT initialize global telemetry merely because a business module imports it. Applications explicitly call bootstrap. Keep service name, version, environment, exporter destinations, and workload policy configurable.

### 21.1 Runnable reference implementation

**Revision 1.1 — rollout prerequisite:** Maintain a versioned reference project that exercises section 20’s smoke-test path and all platform-wide boundary policies. It MUST be executable from a clean checkout with a frozen dependency lock and pinned infrastructure images. The reference project is a required companion artifact; it is not supplied or certified merely by this Markdown standard.

```text
tracing-reference/
  README.md                       exact startup, test, and cleanup commands
  pyproject.toml
  uv.lock                         committed and used without re-resolution
  compose.yaml                    pinned images; real HTTP / PostgreSQL / NATS
  compatibility.yaml              populated approval manifest from section 19
  services/
    order_api/                    FastAPI -> business span -> DB / HTTP / NATS
    payment_api/                  independent receiving process and resource
    notification_worker/          FastStream + real JetStream consumer
  observability/
    bootstrap.py                  one provider per process
    context.py                    typed request/message/job context API
    asgi_context.py               scoped HTTP application metadata
    message_context.py            scoped message metadata
    log_context.py                allowlisted handler-side enrichment
    logging_bootstrap.py          stdlib bridge and batch OTLP log export
    log_lifecycle.py              provider drain/shutdown
    http_policy.py                approved transport composition
    messaging_adapter.py          fresh-publication and baggage policy owner
    otel-collector.yaml           native OTLP traces/logs pipelines
  tests/
    unit/
    integration/
    acceptance/
  evidence/                       generated, non-sensitive run artifacts
```

The project MUST include application lifespan management, bounded reusable clients, logging ownership, persistent JetStream stream/consumer configuration, database fixtures, the selected messaging parent/link model, and explicit failure/cancellation cases. It MUST exercise direct and decorated publishing if both are supported by the service template. A package lock alone is not a compatibility report.

For code represented by a snippet in this document, CI SHOULD execute that snippet’s maintained source or extract/test it to prevent examples from drifting. Validate the Collector configuration with the exact distribution/binary used in the reference, not just a YAML parser.

### 21.2 Rollout gates

Roll out one representative HTTP-to-HTTP-to-NATS path first. Validate with controlled 100%-sampled traffic; then apply the production sampling policy. Expand through service templates and CI checks rather than copying ad-hoc middleware into every repository.

Record supported policy choices separately from deviations. For example, link-based versus single-message parent-based consumer correlation is a supported policy choice when it follows section 8; it is not automatically an exception. Record alternate log export paths or additional database instrumentation as overrides/exceptions only when they actually depart from a `SHOULD` or `MUST`. Do not require identical numbers of spans from different libraries when their documented causal relationships remain correct.

A service is ready when its owner can demonstrate propagation, context isolation, stable resource identity, meaningful errors/cancellation, safe telemetry, and working log correlation through the actual deployment path. Approval requires the populated manifest, reproducible reference test results, service-specific transport/ingestion tests, recorded supported policy choices, `SHOULD` overrides, `MUST` exceptions, and justified not-applicable entries—not a document checkbox alone.

## 22. Compact implementation contract

**Baseline summary plus the explicitly marked extensions above.**

```text
INCOMING HTTP / MESSAGE
  apply ingress trust policy
  filter trace trust / baggage before extraction
  extract W3C context through the boundary owner
  preserve valid traceparent when tracestate is malformed
  create and activate a new local operation span
  use the selected parent/link policy

APPLICATION
  bind fresh immutable AppContext at every request/message/job boundary
  expose get_context() for local metadata; read trace/span from OTel live
  keep context local to the current execution; reset tokens in finally
  add meaningful business spans only
  let instrumented DB / HTTP / messaging calls create their operations
  use standard library logging in handlers/services/repositories/adapters
  use extra only for approved business metadata under an organization-owned namespace; no trace IDs in log text
  let the single startup-installed bridge capture native correlation
  run the bridge before batch queueing; keep identity on provider resources
  classify outcomes and cancellation without changing reliability semantics

OUTGOING HTTP / NEW MESSAGE
  create the outbound operation through its single owner
  inject its current / message-creation context
  preserve approved tracestate and baggage
  never copy stale incoming traceparent blindly
  enforce destination policy after injection and on redirects
  classify new publication vs transparent relay vs batch creation and prove every supported FastStream path with sampled / unsampled inputs

DEFERRED WORK
  persist an approved carrier in infrastructure metadata where needed
  create a new execution span on every attempt
  continue or link according to the documented workflow policy
  keep business identity and idempotency separate from trace identity

SHUTDOWN
  drain work
  end spans
  flush/shut down trace and log providers once per process
  logging.shutdown() is not a substitute for LoggerProvider.shutdown()
  measure exporter / shutdown behavior; do not equate flush True with delivery

APPROVAL
  lock the reference implementation and infrastructure versions
  run transport and native-ingestion acceptance tests
  publish evidence, policy choices, overrides, exceptions, and justified N/A entries before service-template approval
```

Never manually generate tracing IDs, pass them through business signatures, reuse a parent's span ID, create fake IDs for startup logs, embed tracing IDs into domain payloads, or install two owners for one technical boundary.

---

## Appendix A. Explicit reconciliations and additions

| Original statement or example | Treatment in this merged standard |
| --- | --- |
| Generic instructions say to preserve context explicitly across async work. | Retained as an outcome requirement. Ordinary supported Python execution boundaries do not require tracing parameters. Transport and process boundaries require explicit serialization and propagation of approved OpenTelemetry context and application metadata—not manual passing of individual tracing identifiers. |
| General file includes a Go `context.Context` example. | Replaced by the Python active-context model from [S1]; this document targets Python 3.13, not Go. |
| The simple HTTP-to-NATS diagram says all spans should share one trace ID. | Kept as a valid single-message continuation example, not a universal rule for all asynchronous workflows. Links, batches, delayed work, and replay are explicitly distinguished. |
| Diagrams label database spans “DB”. | Preserved as a category but clarified that `DB` is not an SDK span kind. |
| Manual exception example records, sets error, and re-raises inside a default span context manager. | Replaced with separate escaping-exception and handled-exception patterns to avoid duplicate recording on the same span. |
| Setting up log correlation produces JSON fields. | Revision 1.2 uses a stdlib-to-OTel bridge and native fields instead. Optional console/legacy streams remain separate; no duplicate stdout/OTLP ingestion. |
| `LoggingInstrumentor(... inject_trace_context=True ...)` is used. | Optional console enrichment is distinguished from native correlation. The explicit bridge owns native logs; automatic handler installation must not duplicate it. |
| NATS is recommended instead of fire-and-forget asyncio jobs. | Qualified: business durability requires a configured durable workflow, not simply Core NATS publication. |
| Save-to-database followed by publish is shown as business code. | Treated as an observability sketch, not an atomicity guarantee. Outbox guidance is an added optional pattern. |
| Generic OTLP environment variables accompany a gRPC exporter. | Clarified that the explicitly imported exporter class selects the transport. |
| Sampling and semantic-convention settings are examples. | Retained as examples, not unconditional production defaults or proof of support in every instrumentor. |
| No topology, lockfile, or deployed configuration is supplied. | All service names and architecture diagrams remain illustrative; actual runtime compatibility and deployed behavior require the acceptance tests. |
| Gateway policy, retries, fan-out/fan-in, linked jobs, outboxes, redelivery, tail-sampling routing, and rollout. | Explicitly added microservice policies, not claims that these topics were fully covered by the originals. |

## Appendix B. Coverage of the supplied files

| Supplied source sections | Merged sections |
| --- | --- |
| [S1] 1–2: general and Python golden rules | 2–3, 12, 22 |
| [S1] 3–5: bootstrap, export, resources | 1, 4, 18 |
| [S1] 6–9: HTTP ingress, missing context, exclusions, IDs | 2–5 |
| [S1] 10–12: manual spans, names, attributes | 13 |
| [S1] 13–14: HTTPX and manual injection | 6, 12 |
| [S1] 15–17: FastStream, NATS, HTTP-to-NATS | 7–8, 20 |
| [S1] 18: SQLAlchemy | 11 |
| [S1] 19–23: await, tasks, groups, threads, processes | 12 |
| [S1] 24: baggage | 17 |
| [S1] 25–28: logging and context correlation | 15 |
| [S1] 29–30: exceptions and business outcomes | 14 |
| [S1] 31–32: sampling and semantic conventions | 16, 19 |
| [S1] 33–37: ownership, automation, trace shape, naming, sensitive data | 1, 3, 7, 13, 17 |
| [S1] 38: graceful shutdown | 18 |
| [S1] 39–43: integration and correlation tests | 20 |
| [S1] 44–46: dependencies, structure, business code | 13, 19, 21 |
| [S1] 47–49: anti-patterns, summaries, final rule | 1–3, 12–13, 22 |
| [S2] 1–5: propagation, ingress, IDs | 2–5 |
| [S2] 6–8: child spans and outbound context | 3, 6, 12–13 |
| [S2] 9–14: logging and errors | 14–15 |
| [S2] 15–16: async/background and request algorithm | 7–8, 12, 22 |
| [S2] 17–18: required rules and golden rule | 22 |

## Appendix C. External references

The baseline references [W1]–[W21] are retained from the supplied standard. Implementation-sensitive references [W22]–[W34] support the prior review changes. New references [W35]–[W42] and current logging/context documentation were checked on 2026-10-01 for revision 1.2. Tagged source references are deliberately version-specific. `/latest/` and `main` references are moving documents and do not establish the behavior of the service’s locked version. No reference establishes that a particular dependency is installed in your services. Code fragments are not a complete application or a tested deployment lock.

- **[W1]** [W3C Trace Context](https://www.w3.org/TR/trace-context/) — wire identifiers, processing, security considerations.
- **[W2]** [OpenTelemetry Python sampling](https://opentelemetry-python.readthedocs.io/en/latest/sdk/trace.sampling.html) — parent-aware sampling and environment configuration.
- **[W3]** [OpenTelemetry Python trace API](https://opentelemetry-python.readthedocs.io/en/latest/api/trace.html) — spans, links, current context, and exception behavior.
- **[W4]** [OpenTelemetry Python OTLP exporters](https://opentelemetry-python.readthedocs.io/en/latest/exporter/otlp/otlp.html) — distinct gRPC and HTTP exporter implementations.
- **[W5]** [FastAPI instrumentation](https://opentelemetry-python-contrib.readthedocs.io/en/latest/instrumentation/fastapi/fastapi.html) — ingress integration and exclusions.
- **[W6]** [HTTPX instrumentation](https://opentelemetry-python-contrib.readthedocs.io/en/latest/instrumentation/httpx/httpx.html) — outgoing HTTP integration.
- **[W7]** [FastStream OpenTelemetry integration](https://faststream.ag2.ai/latest/getting-started/observability/opentelemetry/) — broker middleware setup.
- **[W8]** [OpenTelemetry messaging spans](https://opentelemetry.io/docs/specs/semconv/messaging/messaging-spans/) — creation context, parent/link models, and messaging operation kinds.
- **[W9]** [NATS JetStream consumer behavior](https://docs.nats.io/learn/jetstream/pull-consumers) — delivery and acknowledgement behavior.
- **[W10]** [NATS publication deduplication](https://nats.io/blog/nats-jetstream-deduplication-for-lfh/) — `Nats-Msg-Id` has a delivery/deduplication role.
- **[W11]** [Core NATS delivery model](https://docs.nats.io/learn/core-nats/) — Core NATS is distinct from persisted JetStream workflows.
- **[W12]** [SQLAlchemy instrumentation](https://opentelemetry-python-contrib.readthedocs.io/en/latest/instrumentation/sqlalchemy/sqlalchemy.html) — async engine integration.
- **[W13]** [Python 3.13 asyncio tasks](https://docs.python.org/3.13/library/asyncio-task.html) — task context and thread propagation.
- **[W14]** [OpenTelemetry HTTP spans](https://opentelemetry.io/docs/specs/semconv/http/http-spans/) — HTTP error semantics.
- **[W15]** [OpenTelemetry Python logging instrumentation](https://opentelemetry-python-contrib.readthedocs.io/en/latest/instrumentation/logging/logging.html) — log-record injection and handler configuration.
- **[W16]** [SigNoz Trace Parser](https://signoz.io/docs/logs-pipelines/guides/trace/) — map parsed log attributes into native correlation fields.
- **[W17]** [SigNoz log/trace correlation](https://signoz.io/docs/traces-management/guides/correlate-traces-and-logs/) — end-to-end correlation validation.
- **[W18]** [OpenTelemetry sampling concepts](https://opentelemetry.io/docs/concepts/sampling/) — head versus tail decisions.
- **[W19]** [Collector tail-sampling processor](https://github.com/open-telemetry/opentelemetry-collector-contrib/blob/main/processor/tailsamplingprocessor/README.md) — per-trace routing and stateful sampling.
- **[W20]** [OpenTelemetry baggage](https://opentelemetry.io/docs/concepts/signals/baggage/) — baggage versus attributes and trust/security limitations.

- **[W21]** [OpenTelemetry Python trace implementation](https://opentelemetry-python.readthedocs.io/en/latest/_modules/opentelemetry/trace.html) — active span attachment and restoration; distinguish parent selection from full-context activation.

- **[W22]** [FastStream 0.7.7 telemetry middleware source](https://raw.githubusercontent.com/ag2ai/faststream/0.7.7/faststream/opentelemetry/middleware.py) — origin-context injection branch, sampled-path distinction, dedicated propagators, and local baggage.
- **[W23]** [HTTPX OpenTelemetry implementation](https://opentelemetry-python-contrib.readthedocs.io/en/latest/_modules/opentelemetry/instrumentation/httpx.html) — request-hook/injection order and explicit transport composition.
- **[W24]** [ASGI OpenTelemetry implementation](https://opentelemetry-python-contrib.readthedocs.io/en/latest/_modules/opentelemetry/instrumentation/asgi.html) — full URL used for exclusions.
- **[W25]** [OpenTelemetry recording errors](https://opentelemetry.io/docs/specs/semconv/general/recording-errors/) — error classification, recovered operations, and development status.
- **[W26]** [Logging instrumentation implementation](https://opentelemetry-python-contrib.readthedocs.io/en/latest/_modules/opentelemetry/instrumentation/logging.html) — record-creation injection and log-hook ordering.
- **[W27]** [OpenTelemetry Logs Data Model](https://opentelemetry.io/docs/specs/otel/logs/data-model/) — native correlation fields, severity/timestamps/body, and resources.
- **[W28]** [Collector trace parser](https://github.com/open-telemetry/opentelemetry-collector-contrib/blob/main/pkg/stanza/docs/operators/trace_parser.md) and [trace parsing types](https://github.com/open-telemetry/opentelemetry-collector-contrib/blob/main/pkg/stanza/docs/types/trace.md) — native trace/span/flags parsing.
- **[W29]** [Collector JSON parser](https://github.com/open-telemetry/opentelemetry-collector-contrib/blob/main/pkg/stanza/docs/operators/json_parser.md) — parsing to attributes and embedded timestamp/severity handling.
- **[W30]** [Collector move operator](https://github.com/open-telemetry/opentelemetry-collector-contrib/blob/main/pkg/stanza/docs/operators/move.md) — promoting fields to resources or the log body.
- **[W31]** [Python 3.13 logging handlers](https://docs.python.org/3.13/library/logging.handlers.html) — queued-record preparation and listener behavior.
- **[W32]** [OpenTelemetry Python SDK 1.42.1 batch processor](https://raw.githubusercontent.com/open-telemetry/opentelemetry-python/v1.42.1/opentelemetry-sdk/src/opentelemetry/sdk/_shared_internal/__init__.py) — flush timeout and exporter-result limitations.

- **[W33]** [OpenTelemetry Python API 1.42.1 trace implementation](https://raw.githubusercontent.com/open-telemetry/opentelemetry-python/v1.42.1/opentelemetry-api/src/opentelemetry/trace/__init__.py) — exception handling in the active-span context path.
- **[W34]** [HTTPX custom transports](https://www.python-httpx.org/advanced/transports/) — wrapping transport behavior, proxy/mount routing, and transport ownership.


- **[W35]** [Python 3.13 contextvars](https://docs.python.org/3.13/library/contextvars.html) — module-scoped variables, get/set/reset, token ownership, Python contexts.
- **[W36]** [OpenTelemetry Python 1.42.1 ContextVars runtime](https://raw.githubusercontent.com/open-telemetry/opentelemetry-python/v1.42.1/opentelemetry-api/src/opentelemetry/context/contextvars_context.py) — OTel state is a separate value in Python context-variable storage.
- **[W37]** [Starlette middleware](https://www.starlette.dev/middleware/) — pure ASGI patterns and BaseHTTPMiddleware context-propagation limitations.
- **[W38]** [AnyIO thread context propagation](https://anyio.readthedocs.io/en/stable/threads.html#context-propagation) — context copies into worker threads without propagating rebindings back.
- **[W39]** [OpenTelemetry Python Logs SDK examples](https://opentelemetry-python.readthedocs.io/en/latest/examples/logs/README.html) — Python Logs API caveats and movement of the logging bridge from SDK to contrib.
- **[W40]** [Contrib logging handler implementation](https://raw.githubusercontent.com/open-telemetry/opentelemetry-python-contrib/main/instrumentation/opentelemetry-instrumentation-logging/src/opentelemetry/instrumentation/logging/handler.py) — native conversion uses active context; business attributes, formatter behavior, and explicit handler API. Moving source, not a production version pin.
- **[W41]** [Python 3.13 logging](https://docs.python.org/3.13/library/logging.html) — module loggers, hierarchy, handler filters, replacement records, and extra fields.
- **[W42]** [OpenTelemetry Python Logs SDK API](https://opentelemetry-python.readthedocs.io/en/latest/sdk/_logs.html) — LoggerProvider, log processors, force flush, and shutdown.
- **[W43]** [OpenTelemetry Semantic Conventions 1.44.0](https://opentelemetry.io/docs/specs/semconv/) and [general naming guidance](https://opentelemetry.io/docs/specs/semconv/general/naming/) — reviewed semantic-convention baseline and custom namespace guidance for revision 1.3.
- **[W44]** [OpenTelemetry `app.*` attribute registry](https://opentelemetry.io/docs/specs/semconv/registry/attributes/app/) — `app.*` is an OpenTelemetry-owned semantic-convention namespace, not a generic custom-application prefix.
- **[W45]** [OpenTelemetry messaging attribute registry](https://opentelemetry.io/docs/specs/semconv/registry/attributes/messaging/) — generic messaging attributes and custom `messaging.system` values.
- **[W46]** [OpenTelemetry database spans](https://opentelemetry.io/docs/specs/semconv/db/database-spans/) and [SQL conventions](https://opentelemetry.io/docs/specs/semconv/db/sql/) — stable database span schema and opt-in query-parameter capture.
- **[W47]** [OpenTelemetry service resource conventions](https://opentelemetry.io/docs/specs/semconv/resource/service/) — `service.instance.id` instance-uniqueness semantics.

## Appendix D. Revision history and verification scope

### D.1 Historical revision 1.1 changes from the supplied standard

These locations describe revision 1.1. Revision 1.2 supersedes its logging examples and extends its context and shutdown sections as recorded in D.3.

| Review finding / enhancement | Revised location |
| --- | --- |
| Fresh-publication policy may conflict with stock FastStream behavior | Sections 1, 7, 9, 10, 20: version-specific gate, every publishing path, sampled/unsampled coverage, and explicit exceptions. |
| Invalid `tracestate` must not invalidate a valid `traceparent` | Sections 2 and 20: corrected processing table and an executable SDK regression test. |
| Flush timeout/boolean is not a delivery guarantee | Section 18: sequential shutdown example, implementation qualification, and failure/elapsed-time evidence. |
| Security policy needs named enforcement | Sections 5, 6, 7, and 17: ingress order, HTTP transport filtering after injection, redirects, and dedicated middleware baggage stores. |
| Logging needs formatter-to-native-field mapping | Section 15: emission-time flags, JSON formatter, native-field/resource table, Collector fragment, and fixture coverage. |
| Business errors and cancellation need explicit defaults | Section 14: outcome table, bounded `error.type`, retry recovery, and cancellation/acknowledgement rules. |
| Diagnostic exclusions are too broad | Sections 5 and 20: anchored top-level paths and positive/negative exclusion tests. |
| Messaging cardinality needs explicit coverage | Section 13.1 and section 20: destination templates and span/metric assertions. |
| A standard needs a reproducible implementation contract | Sections 19–21: populated compatibility manifest, runnable reference-project requirements, and evidence-based rollout gates. |

### D.2 Historical revision 1.1 verification record

This revision does not claim that the platform has a tested dependency lock, an approved FastStream adapter, a running Collector/SigNoz deployment, or a completed companion reference project. Version-specific source inspection is not end-to-end verification. Syntax validation is not runtime or deployment validation.

The following is the verification record inherited from revision 1.1. It was not rerun as that entire original suite for revision 1.2; its JSON-first examples have now been superseded. New revision 1.2 evidence and limitations appear in D.4.

Checks reported while preparing revision 1.1:

| Check | Result and limits |
| --- | --- |
| Python syntax | All **19** Python blocks compiled under Python **3.13.5**. Top-level `await` is allowed for explicitly identified async fragments. Compilation does not establish that all integration imports/configurations run. |
| Structured examples | Both YAML blocks and the JSON example parsed successfully. The Collector fragment was **not** validated by a Collector binary. |
| Document structure | All **22** original numbered section headings retained; **26** internal links resolve; all **34** external-reference labels are defined. |
| Focused local tests | **43 passed** on Python **3.13.5**, OpenTelemetry SDK/API **1.42.1**, and HTTPX **0.28.1**. Coverage included the SDK parent/state regression, unsampled propagation, formatter/flags logic, queue preservation, transport filtering/redirect logic, diagnostic regex, cancellation behavior, flush limitations, and shutdown ordering. |
| Instrumentation integration | Not run as a complete stack. The formatter tests supplied enriched records directly; they did not certify `LoggingInstrumentor` installation. HTTP policy tests used HTTPX `MockTransport`; they did not certify the outer OpenTelemetry transport or a real network/proxy path. |
| Dependency and backend validation | No complete dependency installation/lock or NATS/Collector/SigNoz acceptance run was produced. The package-installation attempt could not reach the package index because DNS resolution failed. |

These focused tests check the revised examples’ isolated behavior. They are not the service-template acceptance suite specified in section 20.

The service owner must still run the real HTTP/NATS/JetStream, Collector-native-field, resource, acknowledgement, shutdown, and SigNoz correlation tests against the approved versions. Requirements for those tests are part of this standard; results not produced here are not implied.

### D.3 Revision 1.2 changes

| Requirement | Revised location |
| --- | --- |
| Get execution metadata anywhere inside the current scope | Section 12: typed immutable AppContext, scoped binder, strict/optional accessors, live OTel readers. |
| Isolated HTTP/message/job lifetimes | Sections 5, 7–8, 10, 12, and 20: ASGI middleware, delivery wrapper, cancellation and concurrency rules. |
| Application code uses normal logging | Section 15.1: stdlib logger API, business extra only, no per-layer tracing parameters or IDs in log text. |
| Startup-only native OTel bridge | Sections 4 and 15: one log provider/bridge/batch exporter, native context correlation, service resource reuse. |
| Context metadata and native tracing remain separate | Sections 12, 15, and 17: allowlisted application fields, live trace source of truth, no automatic wire copying. |
| Queueing does not lose correlation | Section 15.5: native conversion before batching; no unreviewed QueueListener-before-bridge pattern. |
| Provider shutdown and no duplicated delivery | Sections 15 and 18: log-provider lifecycle, trace/log shutdown order, console/OTLP separation. |
| Implementation verification | Sections 19–22: manifest additions, new acceptance requirements, reference-project modules, compact contract. |

### D.4 Revision 1.2 verification

The revision 1.2 checks were run locally on **Python 3.13.5**, with **OpenTelemetry API/SDK 1.42.1**, **FastAPI 0.128.2**, **Starlette 0.50.0**, **HTTPX 0.28.1**, **AnyIO 4.13.0**, and **pytest 9.0.2**. These are test-environment observations, not a recommended production lock.

| Check | Result and limitations |
| --- | --- |
| Final local suite | **51 passed**: 44 runtime/helper checks plus 7 document-contract/structure checks. This is a new focused suite, not the historical revision 1.1 suite. |
| Python examples | All **29** Python blocks compiled under Python 3.13.5; top-level await was permitted for the explicitly illustrative async fragments. Syntax is not import or integration validation. |
| Context behavior | Verified empty/strict reads, immutable metadata, nested restoration, exception/cancellation cleanup, live nested-span readers, non-recording/unsampled contexts, concurrent tasks, copied-thread behavior, clean Python vs OTel contexts, and no implicit metadata injection. |
| HTTP scope | Verified the pure-ASGI adapter with in-process FastAPI/HTTPX ASGITransport, including concurrent requests, request-ID validation, streaming lifetime, failure cleanup, and a sync endpoint. This did not install FastAPIInstrumentor or test a real server/proxy path. |
| Message scope | Verified the independent delivery-scope runner and failure/cancellation restoration. No FastStream middleware hook, decorated publisher, real NATS, acknowledgement, or JetStream workflow was exercised. |
| Native log behavior | Verified native IDs, nested spans, unsampled flags, resource identity, business extras, local metadata, batch preservation after scope exit, and provider shutdown draining. These probes used the installed SDK 1.42.1 **deprecated compatibility LoggingHandler**, not the recommended contrib handler. |
| Queue regression | Confirmed that extra trace strings alone did not populate native IDs when the compatibility bridge ran in an unrelated thread. The required direct-bridge-before-batch design avoids that boundary. |
| Log lifecycle | Verified idempotent owned cleanup and provider shutdown after a simulated flush exception. This does not establish a hard timeout or successful backend ingestion. |
| Document integrity | All **22** numbered sections retained; **26** internal links resolve; all **42** external-reference labels are defined; the remaining YAML manifest parses; embedded module examples match their validation sources. |
| Current contrib bootstrap | Syntax-checked, but **not imported/executed**. Installing the logging/FastAPI contrib packages failed because the environment could not resolve the package-index hostname. No silent substitution was made in the recommended example. |
| Full deployment | No locked full-stack installation, real HTTP/NATS transport acceptance, Collector binary validation, OTLP network delivery, or SigNoz navigation test was completed. The required evidence remains in sections 19–21. |

The recommended production bridge remains the contrib handler in section 15.3. Compatibility-handler probes establish only the tested behaviors of that available SDK implementation; they do not certify another package or version. Keep the real boundary, bridge, native-ingestion, redaction, and shutdown tests as rollout gates. The original revision 1.1 file was left unchanged.



### D.5 Revision 1.3 changes

| Requirement / consistency issue | Revised location |
| --- | --- |
| Organization-owned custom telemetry namespace; no generic custom `app.*` | Sections 13–15, 20, 22; examples and filters use illustrative `com.yourcompany.*` placeholders. |
| Messaging links as the default correlation model, with single-message parentage as a permitted alternative | Sections 7–8 and 20. |
| Explicit messaging semantic-convention schema and per-domain SemConv manifest | Sections 7.2, 19, and 20. |
| HTTP resend attribute and database/resource SemConv tightening | Sections 4, 9, 11, 19, and 20. |
| Transparent relays separated from new publications; batch creation unit defined | Sections 7, 7.1, and 20. |
| Per-message batch processing separated from combined fan-in assertions | Sections 8 and 20. |
| Outbox `SHOULD` persistence made acceptance-conditional | Sections 10 and 20. |
| Canonical application `error.type` mapping made independent of handled/escaping control flow | Section 14. |
| Sampling-compatible third-party client requirement | Sections 6 and 20. |
| Supported policy choices, `SHOULD` overrides, and `MUST` exceptions explicitly distinguished | How-to-read rules, sections 7, 19–21, and 22. |
| Context binding separated from explicit log enrichment in privacy acceptance | Sections 12, 15, and 20.7. |
| Messaging metric cardinality enforced at/before SDK aggregation; Collector normalization is additional | Sections 13.1 and 20. |
| Suppressed/excluded HTTP propagation mode and stale-carrier sanitation defined | Sections 6, 17.3, 19, and 20. |
| Acceptance observation points and N/A/exception evidence states defined | Sections 19–20. |
| Appendix reconciliation no longer says individual tracing identifiers are manually passed across transports | Appendix A. |

### D.6 Revision 1.3 verification scope

Revision 1.3 was checked structurally and at the example level after applying the two review tasks. All **29** embedded Python blocks compile under the syntax checker with top-level `await` permitted for illustrative async fragments; the remaining YAML manifest parses; all **22** numbered sections remain in sequence; all **26** internal document links resolve; and all **47** `[W*]` references used by the document are defined. A stale-wording scan found none of the replaced contradiction phrases or superseded custom telemetry keys from the old generic application namespace.

The semantic-convention corrections were also cross-checked on 2026-10-01 against the current official OpenTelemetry specification pages: the specifications index reports Semantic Conventions **1.44.0**; the naming guidance recommends company reverse-domain prefixes and warns application developers against reusing existing semantic-convention namespaces; `app.*` is an OpenTelemetry-defined namespace; messaging spans use links as the default producer/consumer correlation mechanism and allow message-creation parentage only for single-message processing; `http.request.resend_count` is the standard resend attribute; `database`/`database/dup` and `messaging`/`messaging/dup` are documented stability opt-ins; and `service.instance.id` must be unique for each instance of the same `service.namespace,service.name` pair. [W43, W44, W8, W14, W46, W47]

This remains document/example verification, not a service-template certification. The document is not evidence that the locked FastStream, HTTPX instrumentation, Collector, or SigNoz deployment emits the required schema. Approval still requires the populated manifest and the real integration/acceptance evidence in sections 19–21.
