---
type: source-index
status: active
scope: python
source_revision: tracing-standard-1.3
retrieved: 2026-10-01
verified: 2026-10-01
tags:
  - python
  - tracing
  - sources
  - provenance
---

# Tracing Sources

## Pinned supplied standard

- Source: [Distributed Tracing Standard for Python Microservices, revision 1.3](References/microservices_tracing_standard_v1_3.md).
- Original supplied filename: microservices_tracing_standard_v1_3.md.
- Document date/revision: 2026-10-01 / 1.3.
- Source status: **Proposed platform standard**; preserved unchanged.
- Snapshot SHA-256: `8423366207d5644e2cb8fe6a62cdec0fafe1861c7e0804850663d72f68526754`.
- Stack: Python 3.13, FastAPI, FastStream, NATS/JetStream, HTTPX, SQLAlchemy,
  OpenTelemetry, OTLP, and SigNoz.
- Integration: user-approved adoption as scoped vault guidance on 2026-10-01.
  Active derived notes are not approval/certification of a service deployment.
- Provenance: the supplied document attributes inherited material to
  python_tracing_rules(1).md and signoz_tracing_integration_rules(1).md. Those
  earlier files were not supplied or independently re-audited in this integration.

This is a supplemental source, not part of the pinned guidelines-python
revision in [[Upstream Sources]]. The snapshot is reference material, not a
task instruction or an executable service template. Do not load it wholesale
for ordinary tasks; select derived notes through [[Python Guidelines Context Map]].

## Section coverage

Every original numbered section is retained in the snapshot. The following
maps its rules to their canonical summaries and applicable acceptance. Options
and recommendations retain MAY/SHOULD strength; mandatory adaptations are
recorded in [[Interpretation Notes#Tracing standard integration]].

| Source section | Canonical destination | Applicability or adaptation |
|---|---|---|
| 1 Architecture and ownership | [[Distributed Tracing#Ownership and propagation]]; [[Python OpenTelemetry Integration#Bootstrap and resources]] | One boundary/process owner; shared helpers are not shared runtime state |
| 2 Propagation contract | [[Distributed Tracing#Ownership and propagation]] | W3C carriers, trust, invalid state, and unsampled continuation; preserve business compatibility |
| 3 IDs and HTTP relationships | [[Distributed Tracing#Ownership and propagation]]; [[Tracing Acceptance#Observation points and test tiers]] | SDK-generated IDs and relational assertions; links do not merge traces |
| 4 Identity and initialization | [[Python OpenTelemetry Integration#Bootstrap and resources]] | Per-process startup, resources, exporter protocol; example rates/versions remain illustrative |
| 5 FastAPI and gateways | [[Python OpenTelemetry Integration#FastAPI ingress and application scope]] | Only matching HTTP stack; actual trust/extraction/scope order and precise exclusions |
| 6 HTTPX | [[Python OpenTelemetry Integration#HTTPX egress and redirects]] | Only used HTTPX paths, including proxy/mount/redirect and suppressed modes |
| 7 FastStream/NATS | [[Python OpenTelemetry Integration#FastStream and NATS boundaries]] | Actual locked owner, each used publish API, baggage stores, and emitted SemConv gate |
| 8 Async/fan-out/batches | [[Distributed Tracing#Asynchronous causality and reliability]] | Selected link/parent and per-message/combined batch policies; no second consumer owner |
| 9 Retries/redelivery/replay | [[Distributed Tracing#Asynchronous causality and reliability]]; [[Python OpenTelemetry Integration#HTTPX egress and redirects]] | New publication differs from same-message redelivery; actual retry visibility |
| 10 Outboxes/durable jobs | [[Distributed Tracing#Asynchronous causality and reliability]] | Conditional on usage; carrier persistence remains SHOULD with replacement evidence for override |
| 11 SQLAlchemy/databases | [[Python OpenTelemetry Integration#SQLAlchemy and database spans]] | Conditional database path, one owner, applicable schema, parameter privacy |
| 12 Execution context | [[Distributed Tracing#Application execution context]]; [[Distributed Tracing#Concurrency and lifetime]] | Canonical immutable ContextVars API, live OTel reads, separate stores, boundary adapters |
| 13 Business spans/attributes | [[Distributed Tracing#Attributes, sampling, and trust]] | Owned custom namespace; no generic app.*; SDK-side messaging cardinality |
| 14 Errors/cancellation | [[Distributed Tracing#Outcomes and cancellation]] | Application-span policy only; adapt sole broad-handler example to existing vault rule |
| 15 Logging | [[Python OpenTelemetry Integration#Native logging and context enrichment]] | Actual bridge API, native fields, emission-before-batch, allowlists, no duplicate routes |
| 16 Sampling | [[Distributed Tracing#Attributes, sampling, and trust]] | Parent-aware continuation, linked-root decisions, tail-sampling path/capacity limits |
| 17 Baggage/trust | [[Distributed Tracing#Attributes, sampling, and trust]]; [[Python OpenTelemetry Integration#HTTPX egress and redirects]] | Deny-default, approved keys/origins, pre-extraction/post-injection enforcement |
| 18 Delivery/shutdown | [[Python OpenTelemetry Integration#Collector delivery and shutdown]] | Actual pipelines, outage isolation, measured shutdown; flush is not ingestion |
| 19 Dependencies/SemConv | [[Python OpenTelemetry Integration#Dependencies and semantic conventions]]; [[Tracing Acceptance#Compatibility manifest]] | Actual locks/output; derived manifest revision corrected to 1.3 |
| 20 Tests/acceptance | [[Tracing Acceptance]] | All applicable transport, context, native-log, failure and ingestion rows; required observation points |
| 21 Structure/rollout | [[Tracing Acceptance#Failure, shutdown, and reference rollout]]; [[Python OpenTelemetry Integration#Bootstrap and resources]] | Canonical shared APIs, runnable companion, reference then service-specific rollout |
| 22 Compact contract | [[Distributed Tracing]]; [[Python OpenTelemetry Integration]]; [[Tracing Acceptance]] | Retrieval summary; no new independent requirements |

Appendices A–D remain in the snapshot: reconciliations, inherited source
coverage, external references, and historical verification. Their provenance
and review observations are retained, not promoted into target-project evidence.

## Verification boundary

The source reports focused example/structural checks for revisions 1.1–1.3.
It explicitly does not certify a locked full stack, approved FastStream adapter,
recommended contrib logging bridge, runnable companion, real HTTP/NATS path,
Collector binary/configuration, OTLP delivery, or SigNoz acceptance. Its revision
1.2 native-log probes used a deprecated compatibility handler; they do not
certify the recommended bridge. No such runtime verification was performed by
this documentation integration.

The imported technical observations and Appendix C's external references were
not independently refreshed here. The verified date records source identity,
summary/coverage review, and documentation routing checks only. Before acting
on version-sensitive behavior, inspect the target lock and canonical APIs,
verify applicable official/tagged sources, and run [[Tracing Acceptance]].

## Maintenance

1. Keep this revision's snapshot immutable and compare its checksum on update.
2. Import a later revision as a separate snapshot; record its date/hash and
   changed requirements rather than silently replacing the original.
3. Update only affected summaries, coverage, interpretations, and routes.
4. Preserve explicit scope, strength, supported choices, overrides, exceptions,
   verification limits, and compatibility boundaries.
5. Re-run source identity, coverage, route, metadata/link audit, and router tests.
   Runtime conformance must be rerun separately for affected implementations.

Related: [[Upstream Sources]] · [[Interpretation Notes]] · [[Distributed Tracing]]
