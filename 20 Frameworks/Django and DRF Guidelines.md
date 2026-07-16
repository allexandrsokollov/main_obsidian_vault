---
type: framework-guideline
status: active
scope: python
framework:
  - django
  - drf
source_revision: 885b4e41af02a3c432de5086e74d3bd347cc70ca
tags:
  - python
  - django
  - drf
  - settings
  - error-handling
---

# Django and DRF Guidelines

Load this note with the core context bundle in [[Python Guidelines Context Map]].

## Settings

- Use the Django settings module as the single configuration entry point.
- Read secrets and environment-specific values from environment variables only.
- Do not give critical secrets or production credentials defaults; fail fast when absent.
- Use safe defaults only when they are genuinely safe, such as `DEBUG=False`.
- Convert environment strings to booleans, integers, and lists inside the settings module.
- Group settings into titled domain sections; a settings package split by environment is allowed as the project grows.
- Give each domain a consistent environment-variable prefix such as `DATABASE_`.
- Enable HTTPS, HSTS, and secure-cookie production controls conditionally so local development remains usable.
- Maintain a committed `.env.example` with names but no secrets, and exclude the real `.env`.
- Never place business logic in settings.

## DRF error handling

Classify every failure as expected domain/business or unexpected system/bug.

Required architecture:

- Services and domain code raise plain domain exceptions, never DRF `APIException` subclasses.
- Use one shared exception hierarchy with stable machine-readable codes.
- Prefer reusable category exceptions such as `NotFoundError`; carry entity detail in codes such as `user_not_found`.
- Translate ORM and infrastructure errors at repository/service boundaries and preserve the cause.
- Configure one custom DRF `EXCEPTION_HANDLER` for domain-to-HTTP mapping.
- Return one schema: `{"error": {"code": "...", "message": "..."}}`; do not mix it with default `{"detail": ...}` responses.
- Keep views and serializers thin. Cross-entity business rules belong in services, not serializer `validate_*` methods.
- Log unexpected errors with traceback and request context; expected domain errors should be warning/info or unlogged.
- Never expose SQL errors, tracebacks, raw provider errors, or stack details to clients.

## DRF test gate

Use `APITestCase` through real API entry points. For each endpoint or use case, cover:

- Success with the complete response payload
- Representative domain 4xx errors
- One unexpected 500 path
- The consistent error shape and machine-readable code

Related: [[Clean Code and Architecture]] · [[Testing Strategy]] · [[Upstream Sources]]
