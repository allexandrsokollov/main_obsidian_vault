---
type: interpretation-register
status: active
source_revision: 885b4e41af02a3c432de5086e74d3bd347cc70ca
tags:
  - python
  - ambiguity
  - provenance
---

# Interpretation Notes

This register makes source ambiguity explicit instead of silently inventing policy.

## Local retrospective extensions

[[Integration Boundaries]] records local collaboration preferences extracted
from a 2026-07-31 retrospective about shared-library, NATS, correlation, and
telemetry work. It extends the pinned upstream Python guidance; it does not
claim upstream provenance or change the upstream source wording. Explicit user
requirements and closer repository instructions retain precedence.

## Linting and type-checking configuration

Keep the mypy `plugins` key in `[tool.mypy]` so relevant plugins apply to
production and test code rather than only a test override. Package paths,
first-party module names, applicable framework plugins, and the declared
Python version must match the repository without reducing the production or
test scope.

BasedPyright supplements rather than replaces mypy. Its minimum profile uses
basic mode and keeps `reportInvalidCast = "error"` active. Only
`reportArgumentType`, `reportCallIssue`, and `reportIndexIssue` may be disabled
because strict mypy owns those overlapping checks and they can produce false
positives for Pydantic runtime defaults. Enabling those diagnostics or a
broader checking mode is stricter; disabling another basic-mode diagnostic or
lowering the invalid-cast diagnostic is not.

## Function argument threshold

The upstream typing guide contains conflicting phrasings:

- its core principles and section title say to use a DTO when a function has more than five arguments;
- the section body says more than four arguments;
- its bad example has five arguments and is replaced by a DTO.

Vault interpretation: for a business operation with **five or more parameters**, group related data into a DTO. This follows the stricter body text and example. For a narrow helper, apply judgment from [[Clean Code and Architecture]] and surface any public-API impact.

## Framework precedence

- FastAPI configuration uses `pydantic-settings`; Django configuration uses Django's settings module and explicit environment conversion.
- FastAPI domain code must not raise `HTTPException`; Django/DRF domain code must not raise `APIException` or `ValidationError`.
- Django guidance explicitly prefers reusable exception categories with specific error codes. FastAPI examples sometimes show entity-specific subclasses. Follow the applicable framework note and preserve stable error codes.

## Summary boundary

The vault compresses rules for retrieval and does not reproduce every upstream example. When exact syntax or wording matters, open the pinned file in [[Upstream Sources]].

## Read-only Git inspection

The pinned upstream workflow forbids an AI agent from running any Git command. This vault intentionally applies a repository-local exception: agents may run Git commands that only inspect state or history. Any invocation that modifies the working tree, index, refs, configuration, remotes, stash, history, or other local or remote state remains human-only. See [[Workflow and Quality Gates]] for the operational boundary.
