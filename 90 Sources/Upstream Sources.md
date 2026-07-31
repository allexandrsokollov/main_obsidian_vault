---
type: source-index
status: active
source_repository: https://github.com/allexandrsokollov/guidelines-python
source_revision: 885b4e41af02a3c432de5086e74d3bd347cc70ca
retrieved: 2026-07-16
verified: 2026-07-31
tags:
  - python
  - sources
  - provenance
---

# Upstream Sources

Vault summaries are pinned to revision `885b4e41af02a3c432de5086e74d3bd347cc70ca` of [allexandrsokollov/guidelines-python](https://github.com/allexandrsokollov/guidelines-python).

## Common

- [Clean code rules](https://github.com/allexandrsokollov/guidelines-python/blob/885b4e41af02a3c432de5086e74d3bd347cc70ca/common/clean_code.md) → [[Clean Code and Architecture]]
- [Typing guide](https://github.com/allexandrsokollov/guidelines-python/blob/885b4e41af02a3c432de5086e74d3bd347cc70ca/common/typing.md) → [[Typing and DTO Contracts]]
- [Testing rules](https://github.com/allexandrsokollov/guidelines-python/blob/885b4e41af02a3c432de5086e74d3bd347cc70ca/common/testing.md) → [[Testing Strategy]]
- [Development workflow](https://github.com/allexandrsokollov/guidelines-python/blob/885b4e41af02a3c432de5086e74d3bd347cc70ca/common/workflow.md) → [[Workflow and Quality Gates]]

## FastAPI

- [Settings rules](https://github.com/allexandrsokollov/guidelines-python/blob/885b4e41af02a3c432de5086e74d3bd347cc70ca/fastapi/settings.md) → [[FastAPI Guidelines]]
- [Error handling rules](https://github.com/allexandrsokollov/guidelines-python/blob/885b4e41af02a3c432de5086e74d3bd347cc70ca/fastapi/error_handling.md) → [[FastAPI Guidelines]]

## Django and DRF

- [Settings rules](https://github.com/allexandrsokollov/guidelines-python/blob/885b4e41af02a3c432de5086e74d3bd347cc70ca/django/settings.md) → [[Django and DRF Guidelines]]
- [Error handling rules](https://github.com/allexandrsokollov/guidelines-python/blob/885b4e41af02a3c432de5086e74d3bd347cc70ca/django/error_handling.md) → [[Django and DRF Guidelines]]

## Supplemental official Python style sources

These sources support local guidance that is not attributed to the pinned
upstream repository:

- [PEP 8](https://peps.python.org/pep-0008/) → import grouping, module
  dunder placement, naming, and public/internal interfaces in
  [[Python Module Organization]]
- [Python tutorial: Modules](https://docs.python.org/3/tutorial/modules.html) →
  module execution and import behavior in [[Python Module Organization]]
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
  → related-definition grouping, import-time safety, and executable-module
  structure in [[Python Module Organization]]

## Maintenance

When updating the vault:

1. Compare the pinned revision with upstream using read-only inspection; do not fetch or otherwise modify local or remote Git state.
2. Update only notes affected by source changes.
3. Record new ambiguities in [[Interpretation Notes]].
4. Update every `source_revision` field and this index together.
5. Re-run the internal-link and metadata checks.
