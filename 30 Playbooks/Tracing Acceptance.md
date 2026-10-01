---
type: playbook
status: active
scope: python
source_revision: tracing-standard-1.3
verified: 2026-10-01
tags:
  - python
  - tracing
  - acceptance
  - observability
---

# Tracing Acceptance

## Scope

Use for tracing implementation verification, dependency compatibility,
service-template approval, and live telemetry acceptance. Apply
[[Distributed Tracing]], the selected sections of
[[Python OpenTelemetry Integration]], and the existing
[[Workflow and Quality Gates]] and [[Test Quality Rubric]]. This playbook is
guidance, not a recorded deployment result. See [[Tracing Sources]] for the
pinned proposed standard and its reported verification limits.

Documentation changes are checked through coverage, metadata, links, and
routing. Production behavior changes retain RED-first evidence, focused and
related tests, targeted mutation checks, Ruff, mypy, and BasedPyright. A
documentation check or an SDK probe does not establish real transport or
backend conformance.

## Conformance and evidence states

Before testing, record applicable features, owners, the selected supported
policy alternatives, and each assertion's observation point.

| Mechanism | Required record |
|---|---|
| Supported policy choice | Selected permitted alternative and its applicable tests; it is not an exception |
| SHOULD override | Reason, owner, scope, affected assertions, and replacement evidence |
| MUST exception | Named rule/text, affected paths/versions, approving authority, owner, validity/review date, replacement assertions, and approval impact |

| Evidence state | Meaning |
|---|---|
| PASS | Applicable assertion passed at its required observation point with an identified artifact |
| FAIL | Observed behavior contradicts the applicable assertion |
| NOT RUN | Evidence was not produced; give the exact blocker and remaining risk |
| N/A | The workload truly does not use the feature; give usage justification and evidence owner |
| EXCEPTION | A named mandatory assertion has an approved bounded waiver; preserve its replacement test result separately |

A used feature cannot be N/A because testing is inconvenient. A selected
supported alternative is not a waiver. Never report a waived assertion as
passed or claim complete approval with unresolved FAIL/NOT RUN/applicable
unpopulated fields. Exceptions and their approval impact remain visible.

## Compatibility manifest

Keep the populated manifest beside the target/reference project's evidence,
not as machine-specific configuration in this vault. The following is a schema
example, not an approval record. It corrects the source's stale 1.2 value to
1.3 as recorded in [[Interpretation Notes#Tracing standard integration]].

```yaml
standard_revision: "1.3"
validation_status: "not_run"
python_version: null
reference_commit: null
lockfile_sha256: null
resolved_packages: {}
container_images: {}
semantic_conventions:
  version: "1.44.0"           # source review target, not evidence of emitted support
  http: null                 # stable | legacy | duplicate | not_applicable
  database: null             # stable | legacy | duplicate | not_applicable
  messaging: null            # actual emitted mode | not_applicable
  stability_opt_in: null     # migration mechanism, not the SemConv version
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

Replace every applicable null/unpopulated field with actual artifacts. Record
the exact Python patch, API/SDK/exporter/contrib/FastStream versions, approved
adapter/bridge API, reference commit and lock hash, Collector distribution and
version/image digest, NATS/JetStream and SigNoz versions, and configuration
hashes. not_applicable is allowed only with corresponding feature usage,
justification, and evidence owner. Use dedicated choice/override/exception
fields rather than hiding these distinctions in free-form deviations.

Record actual per-domain SemConv output and opt-in support. A resolved lockfile,
an environment variable, a source example version, or a successful constructor
is not a compatibility report. Upgrades rerun affected acceptance.

## Observation points and test tiers

| Assertion or tier | Required observation | Limit |
|---|---|---|
| Parsing/filtering/helper probe | Active API context or controlled SDK/native exporter | Does not certify real middleware/transport |
| Carrier propagation | Actual HTTP receiver or NATS broker-delivered headers | Producer mock arguments alone are insufficient |
| Span schema/graph | SDK-exported spans before Collector transformation | Backend rewrites cannot satisfy an SDK requirement |
| Metric cardinality | SDK metric stream before Collector transformation | Collector normalization is additional evidence |
| Native logging | Approved real bridge plus native exporter, then named Collector/backend path | Console strings or trace IDs in extra are not native fields |
| Collector integration | Exact locked distribution/binary and inspected output | YAML parsing alone is insufficient |
| SigNoz acceptance | Actual identity, native fields, and retained trace/log navigation | Does not prove loss-free delivery under every failure/load |

Test ID relationships rather than randomly generated literal IDs. Fixed
incoming IDs may be fixtures; generated child IDs must be new and compared to
their actual producer/client context. Unsampled propagation uses carrier/API
evidence without requiring spans that the sampler correctly does not export.

## Transport and boundary matrix

Each applicable row needs a test/evidence artifact and the selected policy.

| Scenario | Required assertions |
|---|---|
| Missing/invalid HTTP context | Valid new root without ambient worker parent; business request succeeds; invalid parent also discards its vendor state |
| Valid parent with malformed tracestate/baggage | Preserve accepted trace ID/remote parent; new local span ID; filter invalid state/baggage independently |
| Trusted A → B → C HTTP | Each server's parent is its corresponding outbound client, not an earlier server; continued trace ID is preserved |
| Gateway/public ingress | Actual receiver observes the declared preserve/reset trust policy and real middleware order |
| Sampled/unsampled paths | Valid context propagates in both; recording must not select a different identity policy accidentally |
| HTTP egress/redirects | Destination allowlist applies after injection at each actual target; stale/manual forbidden carriers absent; all mounts/proxies covered |
| Suppressed/excluded HTTP | Filtering still runs; receiver sees omit or the explicitly selected propagation-only mode; do not equate this with unsampled |
| Diagnostics and ownership | Only approved exact routes excluded; business suffix matches stay traced; no duplicate technical owners |
| Manual business operation/database | Database/outbound spans follow the span active at execution; applicable SDK database schema is correct without unsafe capture |
| Single-message NATS | Broker-delivered carrier survives; selected parent/link relationship is correct; tracing IDs absent from business payload |
| Each used FastStream publishing API | Classify direct HTTP/scheduler, consume-to-publish, decorated return, retry/dead-letter, relay, and batch paths; prove fresh creation context for every new publication |
| Sampled/unsampled consume-to-publish | Publication policy holds in both; inspect carrier/API rather than requiring unsampled exports |
| Fan-out | Distinct processing operations correlated to origin; subscribers are not chained |
| Per-message batch | One processing operation/application scope per message under its selected single-message policy |
| Combined batch/fan-in | Contributing contexts linked; no unrelated first-input parent; bounded/truncated links follow policy |
| HTTP retries | Attempt visibility matches the owner; distinct attempt IDs; applicable resend_count; no cached header reuse |
| JetStream redelivery | Stable business message identity, fresh processing span/scope each time, correct acknowledgement/retry behavior |
| New retry/dead-letter publication | Fresh creation context distinct from consumed input; causation/idempotency remain separate |
| Outbox/restart | If carrier persisted, origin survives restart and dispatch injects new publication context; SHOULD override instead proves replacement causality and no ambient parent |
| Delayed/replayed/scheduled work | Selected linked-root/continuation behavior; fresh application state, no accidental previous worker context |
| Messaging SemConv | Applicable create/send/receive/process/settle schema, names, kinds, fields, errors, and parent/links match the recorded emitted mode |
| Messaging cardinality | Many dynamic subjects keep SDK span names and metric dimensions bounded before Collector normalization |
| Baggage/privacy | Forbidden data absent from real carriers, extracted context, middleware-local baggage, spans, metrics, logs, and exception diagnostics |
| Business outcomes/recovery | Expected rejection differs from technical failure; equivalent handled/escaping failures have canonical error.type; successful retry parent has no stale error |
| Cancellation | Classified outcome/status, cancellation re-raised, no false successful acknowledgement, cleanup and later isolation |

For new publication, extract the actual outgoing carrier and compare its
creation context to the consumed input. In a continued trace the new span ID
differs; for new traces compare the full trace-ID/span-ID pair. Do not require
the carrier to identify the last span whose name contains publish; verify the
owner's documented creation/send graph, including intermediate spans.

## Context isolation matrix

| Scenario | Required assertions |
|---|---|
| Outside scope/deep calls | Empty optional metadata; strict accessor raises; deep calls see current scope without tracing parameters; no fabricated trace |
| Concurrent requests/messages | Distinct metadata and OTel context; no cross-operation overwrite or tenant/request leak |
| Nested binding/spans | Application outer binding restores; live trace reader follows nested span and returns to outer span |
| Failure/cancellation | App token resets and OTel owner restores; cancellation propagates |
| Unsampled/non-recording context | Live readers return valid IDs/flags without requiring recording |
| Tasks and TaskGroup | Initial inheritance; no backward/sideways rebinding; supervised child lifetime and snapshot after parent exit |
| to_thread/custom executor | Intended one-way propagation; no rebindings back to caller or thread-reuse leak |
| Empty Python versus OTel context | Clean Python execution has neither binding; clearing only OTel leaves separate application state explicit |
| HTTP streaming/sync/access logs | Real middleware lifetime/order covers intended stages and documents outside-scope logs |
| Message decode/publish/finalization | Each required framework stage runs in its intended fresh scope without another tracing owner |
| Process/outbox/replay | Only approved serialized metadata crosses; receiving execution binds fresh state |
| Binding and enrichment privacy | Binding alone changes no carrier/baggage/payload and emits no telemetry; log mapping exports only allowlisted fields at emission |
| Required identity | Caller metadata/baggage cannot authorize tenant access; missing required identity fails closed |

## Native logging matrix

Use the actual approved bridge with an in-memory native exporter locally,
then repeat applicable assertions through Collector/SigNoz. Compatibility-handler
probes do not certify the recommended or deployed bridge.

| Scenario | Required assertions |
|---|---|
| Ordinary module log through handler/service/repository | Correct active context, no per-call IDs, exactly one native record under controlled healthy duplicate-routing test |
| Nested/unsampled/no-span log | Native IDs/flags follow active span; valid unsampled correlation preserved; absent/zero no-span fields allowed; no fabricated IDs |
| Business extra/context mapping | Approved business attributes and centrally owned context fields; no trace/resource replacement, tenant/user/baggage copying, or context-key override |
| Trace/log resources | Identity agrees across at least two services and cannot be impersonated by caller extra |
| Batch export after scope exit | Emission-time native correlation/metadata retained; listener thread's context never substituted |
| Levels/propagation/configuration | Expected app/framework records reach bridge; suppression deliberate; later server configuration preserves routing |
| Duplicate delivery | No manual/automatic, child/ancestor-handler, or stdout/OTLP duplicate backend path |
| Native fields/privacy | Correct timestamp, severity, body, full flags, resource and attributes; no decorated native body or secrets in message/extra/exception fields |
| Shutdown/failure | Final logs emitted before provider closes; flush failure does not skip cleanup; export duration/result/delivery measured separately |
| Backend | Native fields survive ingestion; both trace-to-log and log-to-retained-trace navigation work |

## Failure, shutdown, and reference rollout

Required:

- Run a representative real HTTP → HTTP → database/NATS → worker path with
  logs at semantic steps. Cover successful, failed, cancelled, retried, and
  sampled/unsampled variants. Verify causal graph and business results, not
  merely that several spans appear in SigNoz.
- Use a versioned runnable reference project, frozen dependency lock, and
  pinned infrastructure images from a clean checkout. Include lifespan,
  bounded reusable clients, shared production construction, log ownership,
  database fixtures, durable JetStream stream/consumer settings when used,
  selected messaging relationships, and direct/decorated publication when used.
  The Markdown standard does not supply or certify this companion project.
- Validate Collector configuration with the exact locked binary. Prefer CI
  execution of maintained snippet sources or extracted examples to prevent drift.
- Test slow exporters, exporter-returned failure, Collector outage/recovery,
  queue bounds/drop signals, and process termination with in-flight work.
  Business traffic remains functional during telemetry degradation.
- Measure drain, flush, shutdown, final termination, and observed export/drop
  behavior separately. A successful flush boolean is not ingestion or a hard
  timeout. Include final logs and single lifecycle ownership.
- Validate controlled representative traffic with 100% sampling, then the
  production policy. Expand via service templates and CI rather than copied
  per-service tracing middleware.
- For Hyperdrive, also use [[Hyperdrive Delivery and Acceptance]]: exact target,
  deployed revision/digest, rollout counts, and business API evidence remain
  separate from tracing, native-ingestion, and backend-navigation evidence.

## Evidence handoff

Preserve synthetic non-sensitive receiver/header captures, SDK span graphs,
SDK metric streams, native records, and shutdown measurements as artifacts.
Record repository/test commit, exact command/environment, manifest/lock/config
hashes, infrastructure versions, observation point, result, owner, and remaining
gap for each scenario. Use bounded polling for eventual ingestion, not an
arbitrary sleep as the assertion. Screenshots supplement structural evidence.

Readiness requires a populated manifest, reproducible reference results,
service-specific transport/ingestion tests, selected choices, documented SHOULD
overrides, approved MUST exceptions with replacement evidence, and justified
N/A entries. Report code/tests/CI, deployed revision/rollout, live business
behavior, and telemetry conformance separately.

Related: [[Distributed Tracing]] · [[Python OpenTelemetry Integration]] ·
[[Tracing Sources]] · [[Test Quality Rubric]]
