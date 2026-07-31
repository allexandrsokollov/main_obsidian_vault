---
type: guideline
status: active
scope: python
verified: 2026-07-31
tags:
  - python
  - modules
  - organization
  - imports
  - public-api
---

# Python Module Organization

## Design target

A module should tell one coherent story: readers can find its public entry
points quickly, understand its dependencies, and import it without triggering
surprising work.

## Default order

Use only the sections the module needs:

1. Module docstring
2. `from __future__` imports
3. Module dunder metadata such as `__all__`
4. Imports, separated into standard-library, third-party, and local groups
5. An `if TYPE_CHECKING:` block when exceptional typing-only imports are needed
6. Logger, constants, and narrow module configuration
7. Foundational types, protocols, DTOs, and domain exceptions
8. Cohesive implementation sections, grouped by feature or reader flow
9. `main()` and the `if __name__ == "__main__":` guard for an executable module

Ruff should own mechanical formatting and import sorting. Do not add empty
sections or headings merely to reproduce this list.

## Required

- Give the module one clear responsibility and keep related public and internal
  definitions together. Do not mechanically group every class separately from
  every function.
- Make the public API easy to find. Use `__all__` when the module needs an
  explicit export contract, and prefix internal names with one underscore.
- Keep imports at module level and avoid wildcard imports. Use a local import
  only for a documented optional dependency or a measured startup concern, not
  to conceal a circular dependency.
- Keep import-time behavior minimal. Defining immutable constants and a logger
  is normal; network calls, database access, file mutation, application startup,
  and other runtime side effects belong behind an explicit function.
- Prefer reader flow over a rigid declaration taxonomy. Put an entry point
  before its private helpers when Python's evaluation rules allow it; otherwise
  define required base classes, decorators, defaults, or class-body inputs
  before their consumers.
- Apply the typed-contract and function-design rules from
  [[Typing and DTO Contracts]] and [[Clean Code and Architecture]].
- Put executable behavior in `main()` and protect it with the `__name__` guard
  so importing, documentation, and tests do not run the program.

## When to split the module

Do not use a fixed line-count threshold. Split when the file has more than one
reason to change, exposes unrelated APIs, mixes policy with substantial
infrastructure work, or forces readers to jump repeatedly between distant
sections. Split by cohesive feature or responsibility, not simply into
`classes.py`, `functions.py`, and `helpers.py` buckets.

## Review checklist

- [ ] The module has one explainable responsibility.
- [ ] Its imports, public API, and executable entry point follow a predictable
  order.
- [ ] Importing it performs no surprising runtime work.
- [ ] Related definitions are close together and internal names are identifiable.
- [ ] Any proposed split creates cohesive modules rather than arbitrary
  file-size relief.

Related: [[Clean Code and Architecture]] · [[Typing and DTO Contracts]] ·
[[Linting and Type Checking]] · [[Interpretation Notes]] · [[Upstream Sources]]
