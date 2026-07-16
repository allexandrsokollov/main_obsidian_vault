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
