---
type: framework-guideline
status: active
scope: python
framework: fastapi
source_revision: 885b4e41af02a3c432de5086e74d3bd347cc70ca
tags:
  - python
  - fastapi
  - settings
  - error-handling
---

# FastAPI Guidelines

Load this note with the core context bundle in [[Python Guidelines Context Map]].

## Settings

- Use `pydantic-settings`; every settings class inherits `BaseSettings`.
- Every class declares its own `SettingsConfigDict` with `.env`, UTF-8 encoding, `extra="ignore"`, and a unique `env_prefix`.
- Split configuration by domain: general app, database, Kafka, and other distinct responsibilities.
- Let `env_prefix` provide domain scoping; do not repeat prefixes in field names or aliases.
- Use precise field types, safe defaults only where genuinely safe, and required fields for required configuration.
- Instantiate settings once at startup, dependency wiring, or the composition root.
- Do not read environment variables or create settings objects inside services, repositories, or endpoints.

### Settings gate

- [ ] Every settings class owns a unique `model_config` and `env_prefix`.
- [ ] Unrelated configuration is split into separate classes.
- [ ] Required values remain required; fields do not use `Any`.
- [ ] Configuration is loaded once at the application edge.

## Error handling

Classify every failure as:

1. Expected domain/business error → mapped 4xx
2. Unexpected system error or bug → logged with traceback and mapped 500

Required architecture:

- Domain and service layers raise plain domain exceptions, never `HTTPException`.
- Use one application exception hierarchy with stable machine-readable codes.
- Validate important invariants with clearly named guards.
- Translate infrastructure exceptions at repository/service boundaries and preserve cause with `raise ... from exc`.
- Map exceptions to HTTP once, through global handlers or middleware.
- Return one error schema: `{"error": {"code": "...", "message": "..."}}`.
- Keep endpoints limited to validation, service invocation, and response mapping.
- Log unexpected errors with traceback and request context; keep expected rejection logging low-noise.
- Never expose SQL errors, tracebacks, raw provider errors, or stack details to clients.

### Error test gate

For each endpoint or use case, cover representative 4xx errors, an unexpected 500 path, and the complete error contract including `error.code`.

Related: [[Clean Code and Architecture]] · [[Testing Strategy]] · [[Upstream Sources]]
