---
type: guideline
status: active
scope: python
source_revision: 885b4e41af02a3c432de5086e74d3bd347cc70ca
tags:
  - python
  - clean-code
  - architecture
---

# Clean Code and Architecture

## Design target

Production code should be easy to read, easy to change, and hard to misuse.

## Required

- Prefer explicit, straightforward control flow and intent-revealing domain names.
- Give each function one responsibility and one abstraction level.
- Prefer guard clauses over deep nesting.
- Use explicit domain models and DTOs for structured data.
- Separate transport schemas, domain entities, and ORM models.
- Keep business logic independent of HTTP, framework, request, and ORM primitives.
- Isolate side effects such as databases, networks, files, and queues from complex policy decisions.
- Raise meaningful domain exceptions and preserve causes when translating errors.
- Remove duplicated business knowledge, while allowing small local syntax duplication when abstraction would reduce clarity.
- Organize by business feature and keep classes cohesive.
- Keep imports at module level except for a justified optional or measured heavy dependency.
- Keep naming, typing, DTO, error, logging, and return conventions consistent within a repository.

## Forbidden

- Clever compression that obscures intent.
- Vague names such as `data`, `obj`, `tmp`, or `stuff` where domain meaning is available.
- Boolean flags that make a function switch responsibilities.
- Large business-operation argument lists.
- Raw `dict` or `tuple` payloads crossing application boundaries.
- Deep conditional trees for normal control flow or silent fallback for unknown domain states.
- Swallowed exceptions or generic exceptions for known business failures.
- Framework and persistence details embedded in core domain functions.
- Speculative abstractions without repeated need.
- Broad `noqa`, `type: ignore`, or coverage suppressions.
- Double casts through `object` that erase the source type to force an otherwise
  invalid cast past the type checker.
- Local imports used to conceal circular dependencies.

Never use an intermediate `cast(object, ...)` to manufacture compatibility:

```python
client_factory = cast(
    Callable[[UUID, str], VaultWrapperProtocol],
    cast(object, create_rpc_client(VaultWrapperProtocol, get_broker())),
)
```

`cast()` performs no runtime conversion. The inner cast discards the type
evidence that the outer cast should validate, defeating the purpose of invalid-
cast checking. Correct the factory or boundary type instead.

## Design review prompts

- Can a new team member infer intent from names and signatures?
- Does each function stay at one abstraction level?
- Are domain policy and infrastructure concerns separated?
- Are structured inputs and outputs explicit contracts?
- Is every error either handled, translated with cause, or allowed to surface intentionally?
- Is an abstraction removing repeated knowledge, or merely hiding a single use?

Related: [[Python Module Organization]] · [[Typing and DTO Contracts]] ·
[[Testing Strategy]] · [[FastAPI Guidelines]] · [[Django and DRF Guidelines]]
