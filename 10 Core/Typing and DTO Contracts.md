---
type: guideline
status: active
scope: python
source_revision: 885b4e41af02a3c432de5086e74d3bd347cc70ca
tags:
  - python
  - typing
  - dto
---

# Typing and DTO Contracts

## Contract rule

Every meaningful data shape must be explicit: typed signatures, typed DTOs, typed filters, typed returns, and predictable flow between layers.

## Function signatures

- Type every argument and return value.
- Prefer precise containers such as `list[str]`, `dict[int, UserDto]`, `set[EntityId]`, and `tuple[str, int]`.
- Model optionality explicitly with `T | None` only when absence is valid.
- Keep primitives for narrow, simple helpers.
- For a business operation with five or more parameters, group its related arguments into an intent-named DTO. See the upstream threshold clarification in [[Interpretation Notes]].

## DTOs

- Use DTOs for requests, create/update data, service payloads, commands, queries, filters, and meaningful return objects.
- Declare DTOs with `@dataclass(slots=True)` by default.
- Name by role and intent: `CreateUserDto`, `UpdateOrderDto`, `UserResponseDto`, `SyncVaultGroupCommand`.
- Separate DTOs when input and output meanings differ.
- Return a DTO rather than an anonymous dictionary when the result represents a business entity or contract.

Avoid generic names such as `Data`, `Payload`, `Info`, `Params`, and `RequestObject`.

## `Any` boundary

Treat `Any` as a local escape hatch for framework internals, untyped libraries, raw ORM filter dictionaries, or short compatibility layers. Do not let it spread into core business code.

## ORM query filters

- Represent query criteria with dedicated, typed filter DTOs.
- Centralize conversion from the DTO to raw ORM filter syntax inside the DTO or repository boundary.
- Keep string-based query construction out of higher-level services.
- Make supported filters discoverable from the filter class.

## Review checklist

- [ ] Every changed function has complete parameter and return annotations.
- [ ] Containers and optionals describe the actual shape.
- [ ] Structured business data uses an intent-named DTO.
- [ ] DTOs use `@dataclass(slots=True)` unless a documented boundary requires another model.
- [ ] Meaningful results are not anonymous dictionaries.
- [ ] `Any` is confined to a technical boundary.
- [ ] ORM filter construction is centralized and typed.

Related: [[Clean Code and Architecture]] · [[Interpretation Notes]] · [[Upstream Sources]]
