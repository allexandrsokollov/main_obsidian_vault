---
type: framework-guideline
status: active
scope: python
framework: opentelemetry
source_revision: tracing-standard-1.3
verified: 2026-10-01
tags:
  - python
  - tracing
  - opentelemetry
  - logging
  - fastapi
  - faststream
---

# Python OpenTelemetry Integration

Use only the sections selected by [[Python Guidelines Context Map]] for the
actual stack. Apply [[Distributed Tracing]] and [[Integration Boundaries]].
This summarizes the supplied proposed standard; its examples, tagged-source
observations, and reported checks are not an approved dependency lock or a
certification of a service. See [[Tracing Sources]].

## Bootstrap and resources

Required:

- Initialize telemetry once in each worker process after worker creation and
  before serving or consuming. Use one provider/configuration owner, not
  per-request providers or a prefork master's inherited provider.
- Set stable service.name; replicas of one logical service use the same name.
  Prefer service.namespace, service.version, and deployment.environment.name.
  When service.instance.id is used, it must be unique among concurrently
  running instances of the same namespace/name pair. Pod identity is separate.
- Record a consistent naming choice for independently deployed HTTP/worker
  components; do not vary names by tenant, request, or replica.
- Reuse process resource identity for trace and log providers. Service identity,
  exporter destinations, runtime dependencies, and workload policy are configured
  at the service composition root, not supplied by application log extra.
- Select explicit bootstrap or managed auto-configuration, not both. Explicit
  exporter imports select the protocol; changing an environment variable does
  not convert a constructed gRPC exporter into an HTTP exporter.
- Tests exercise the production construction path.

Shared helpers SHOULD remain import-safe and avoid initializing global telemetry
when a business module imports them; applications call bootstrap explicitly.
Tests needing different provider configurations SHOULD use isolated processes
or explicit test providers. These recommendations require SHOULD-override
records when departed from, not mandatory-rule exceptions.

Inspect the canonical framework/shared-library API before adding adapters.
Illustrative package/module names in the source do not authorize creating a
new shared library or replacing an existing owner.

## FastAPI ingress and application scope

Required:

- FastAPIInstrumentor owns HTTP extraction and the SERVER span. Register it
  before requests are served; do not parse traceparent or add a second server
  span in application middleware.
- Enforce ingress trace trust and baggage filtering before extraction. Prove
  actual nesting: ingress filtering → application scope → OTel HTTP boundary
  → authentication/validated enrichment → application code. File order or a
  post-creation request hook is not proof of server parentage.
- Bind fresh application metadata with a pure ASGI boundary, not
  BaseHTTPMiddleware or a synchronous dependency that sets a token in another
  thread. Scope the full awaited invocation, including streaming work; restore
  on failure and cancellation. WebSockets need an explicit scope policy.
- Validate support IDs under an explicit ingress contract. They are correlation
  labels, not trusted identity. Bind identity enrichment in the async boundary
  enclosing its consumers; do not move reset tokens between contexts.
- Test task-creating middleware, sync endpoints, mounted prefixes, and access
  logs outside request scope. Optional receive/send-span exclusions do not
  mean excluding the HTTP server operation.
- Exclude only explicitly approved diagnostic routes using precise anchored
  matching against the locked implementation's URL representation. Business
  routes such as /orders/metrics must remain traced unless deliberately excluded.
- Transparent uninstrumented gateways should preserve approved carriers.
  Instrumented gateways inject their outbound context. Public resets require
  an explicit policy; neither proxy headers nor health prove continuity.

## HTTPX egress and redirects

Required:

- Use HTTPXClientInstrumentor or an explicit OTel transport as the one tracing
  owner; do not layer both integrations on one path.
- Ordinary trusted calls propagate the active client context, including valid
  unsampled context. Third-party/unapproved destinations remain instrumented
  but omit W3C propagation by default; recording stays sampler-dependent.
- At the actual send path, remove stale/caller-supplied W3C fields before
  injection, then enforce destination/vendor/baggage policy after injection
  and before network I/O. A request hook running before injection is insufficient.
- Match approved origins by normalized scheme, host, and effective port, not
  hostname suffixes. Approve traceparent, tracestate, and baggage independently.
- Re-evaluate every redirect destination and review all mounts/proxies/alternate
  transports. follow_redirects=False alone does not control manually followed
  redirects or bypass paths.
- Suppressed/excluded tracing uses the recorded omit mode by default. A reviewed
  propagation-only alternative for trusted destinations is permitted with its
  own adapter, manifest choice, and tests. Unsampled is not suppressed.
- Preserve the same policy if baggage or proxy routing is enabled. The source's
  default deny-baggage transport is not changed by an environment variable alone.
- Test real receiver headers for concurrent callers, redirects, stale fields,
  sampled/unsampled traffic, and suppressed/excluded paths. Transport mocks
  establish filtering logic, not full instrumentor/proxy conformance.

The application lifecycle SHOULD own a reusable AsyncClient with explicit
timeouts and connection limits. Do not keep request-specific trace headers in
shared client defaults. The lifecycle owns closing its clients.

A logical operation MAY own an INTERNAL span covering its retry budget; omitting
that optional span is neither an override nor an exception. Each actual network
attempt SHOULD have a separate client span visible to the selected integration.
Do not claim visibility
of transport-internal retries without evidence. Use http.request.resend_count
where applicable; application-level retry attributes use the owned namespace.
Never reuse a cached carrier; preserve business idempotency separately.

## FastStream and NATS boundaries

Required:

- NatsTelemetryMiddleware is the default tracing owner only after its actual
  locked version passes the compatibility gate. An approved upgrade or reviewed
  extension/replacement can own the boundary; business code must not mutate
  middleware-private state or add another producer/consumer instrumentor.
- When FastAPI/FastStream share a process, share the process provider and one
  lifecycle owner. Durable JetStream stream/consumer, acknowledgement, retry,
  and dead-letter behavior remain explicit application reliability contracts.
- Bind fresh validated application metadata for each delivery through the
  canonical dispatch scope. Cover decoding/enrichment, handler work, decorated
  publication, final reporting, and acknowledgement logs where they need it.
  A handler-only wrapper may end too early; test the real hook and ordering.
- Preserve carriers through serialization, forwarding adapters, and broker
  delivery. Classify new publication, byte-for-byte relay, and batch creation;
  verify the selected fresh-context and parent/link rules from
  [[Distributed Tracing#Asynchronous causality and reliability]].
- Inspect actual direct HTTP/scheduler publication, consume-to-publish,
  decorated/handler-return publication, retry/dead-letter publication, relay,
  and batch APIs used by the service. Run each with sampled and unsampled
  inputs; use carrier/API assertions for non-recording contexts.
- Enforce policy against transport headers, extracted OTel context, and
  middleware-local baggage. Global OTEL_PROPAGATORS is not proof that dedicated
  propagators obey the same policy. Filtering only one store is insufficient.
- Test SDK span names, kinds, applicable required/recommended messaging fields,
  errors, and relationships against the manifest's actual emitted SemConv mode.
  Do not demand invented identical span sequences across libraries.
- Bound dynamic subject names and metric dimensions before SDK aggregation;
  inspect many distinct subjects. A manual span or downstream Collector rewrite
  cannot fix the middleware's SDK metric cardinality.

The source's FastStream 0.7.7 origin-context branch is a tagged observation,
not a diagnosis of the target release. If the stock owner fails a mandatory
policy, use a tested owner upgrade/adaptation or a bounded approved MUST
exception with replacement assertions. Constructor success is not acceptance.

## SQLAlchemy and database spans

- Required: instrument the highest useful database abstraction once. An async
  SQLAlchemy engine uses its synchronous engine interface for the instrumentor.
  Prefer one SQLAlchemy owner; extra driver instrumentation needs an intentional,
  tested additional purpose rather than duplicate query spans.
- Prefer queries under the operation active during execution, not flattened
  under an earlier server span. Database calls commonly use CLIENT; there is
  no DB span kind to invent.
- Required: inspect applicable SDK-exported fields for the recorded SemConv
  mode, including database/system/operation/query summary, server address,
  response status, and error classification. Do not fabricate unavailable or
  inapplicable attributes to satisfy a checklist.
- Query parameters remain opt-in. Keep sensitive literal query text, comments,
  connection strings, parameters, and exception text out by default. Parameterized
  SQL alone is not a telemetry privacy guarantee.

## Native logging and context enrichment

Required:

- Handlers, services, repositories, and adapters use stdlib module loggers.
  Business code does not create exporters, call low-level Logs APIs, pass tracing
  parameters, or put trace/span IDs in message text or extra.
- Configure one stdlib-to-OTel bridge, log provider, and batch processor at worker
  startup. Explicit manual wiring is the reference mode; managed wiring may
  replace it if it proves the same contract. Never install both bridges.
- Capture native trace/span/flags from active OTel context when the bridge runs.
  Keep the native body as the event message. Formatting and LoggingInstrumentor
  record-factory enrichment are separate from native correlation; no span/zero
  correlation is valid, and logging must not manufacture a trace.
- Pin and test the actual bridge API. The source prefers the contrib handler
  over the deprecated SDK compatibility handler; it does not certify a current
  package or permit a silent fallback. See the source's reported limits.
- Put an allowlisted application-context mapper on the handler, not only the
  root logger. Centrally owned request/workflow/message fields cannot be
  overridden by business extra. Do not automatically map tenant/user identity,
  baggage, or arbitrary ContextVars; validation and redaction remain separate.
- Use extra only for approved business attributes with an organization-owned
  namespace, bounded values, and no reserved LogRecord field collisions.
- Run native conversion on the emitting task/thread before batch queueing.
  QueueHandler/QueueListener before the bridge requires a reviewed origin-context
  adapter; preserving trace-ID strings alone does not populate native fields.
- Capture application metadata before any off-thread enrichment. Optional
  console formatting uses a record copy/emission-time snapshot and must not
  leak formatting fields into native attributes.
- Audit logger levels, disabled/propagate settings, child/root handlers,
  launchers, and later logging reconfiguration. One backend application stream
  must not be collected through both stdout/files and native OTLP. Other runtime
  streams may keep distinct collection paths; test duplicate counts under
  controlled healthy delivery.
- Preserve trace/log resource identity and native timestamps, severity, body,
  flags, and attributes through ingestion. A JSON parser is not required to
  manufacture native correlation for the native OTLP stream.

## Collector delivery and shutdown

Required:

- Configure actual OTLP trace and log pipelines, approved authentication/TLS,
  processing, resources, and destination. A traces-only pipeline is not log
  ingestion; a second Collector tier is not inherently required.
- Use bounded asynchronous batch processing, exporter queues/timeouts/retries,
  and degradation signals. Export is not a synchronous requirement of each
  business operation. Collector failure degrades observability without
  deliberately failing otherwise valid business requests or breaking propagation.
- One lifecycle owner drains requests/messages/supervised work, ends spans,
  emits final application logs, and then flushes/shuts down providers once.
  Keep logging available for trace-shutdown diagnostics before log-provider
  shutdown. logging.shutdown does not replace LoggerProvider.shutdown.
- Serialize combined shutdown, including work moved to a thread. Cancelling an
  await does not forcibly terminate synchronous exporter work; do not launch
  a second concurrent shutdown. Keep non-recursive local failure diagnostics.
- Measure drain, flush, provider shutdown, and process termination. A flush
  boolean is not exporter success, backend ingestion, or a hard wall-clock bound.
  Test slow/failing exporters, Collector outage, and in-flight termination.
- Flush at shutdown, not every request. Abrupt termination can lose buffered
  telemetry; size the supervisor/Kubernetes grace period from measured budgets
  and maintain time synchronization.
- Validate native fields and resource identity through the real Collector/SigNoz
  path, including navigation for retained traces, unsampled/no-span logs, and
  exporter failure. Do not invent IDs to repair absent sampled/retained traces.

The platform SHOULD monitor export failures, dropped telemetry, queue pressure,
and missing resource identity. Standard OTel APIs suffice; business code SHOULD
avoid SigNoz-specific SDK dependencies.

## Dependencies and semantic conventions

Required:

- Use the target lockfile and record Python patch version, resolved packages,
  adapter/bridge APIs, lock hash, reference commit, infrastructure versions and
  image digests, configuration hashes, and acceptance report.
- Record the SemConv review version separately from actual HTTP/database/messaging
  modes and stability opt-ins. This source's review target is 1.44.0; source
  observations such as SDK 1.42.1 and FastStream 0.7.7 are not production pins.
- Verify emitted attributes and supported migration tokens per locked component;
  environment variables and successful dependency resolution are not conformance.
  Do not force equal numeric versions across packages with different schemes.
- Treat duplicate SemConv modes as a deliberate migration choice and align
  dashboards/queries/alerts with actual output. Do not silently rename fields.
- Rerun applicable tests when libraries, middleware, Collector, or SemConv change.
  Python 3.13 includes contextvars; no backport package is needed.

Use [[Tracing Acceptance#Compatibility manifest]] before claiming readiness.

Related: [[Distributed Tracing]] · [[Tracing Acceptance]] · [[Tracing Sources]]
