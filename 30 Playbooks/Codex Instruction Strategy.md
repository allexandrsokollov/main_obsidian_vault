---
type: playbook
status: active
scope: codex
verified: 2026-07-16
tags:
  - codex
  - personalization
  - agents
  - prompting
---

# Codex Instruction Strategy

## Recommendation

Shorten Personalization to universal behavior. Move language rules, commands, and detailed checklists into repository `AGENTS.md` files or reusable skills. Use [[Codex Instruction Map]] to choose the scope.

## Problems in the current Personalization text

1. It mixes global working style, language-specific policy, implementation workflow, and completion checks in one layer.
2. Bare GitHub URLs do not guarantee that the relevant files are loaded, pinned, or reachable in every task.
3. Several rules repeat the same idea, increasing context without adding a decision.
4. “Ask when unclear” can create unnecessary pauses. Codex should ask only when a reasonable assumption would materially change behavior, public API, tests, architecture, safety, or external state.
5. “Bias toward caution over speed” is too broad for trivial work. Verification effort should be proportional to risk.
6. The Go line contains the typo `coe`; use `code`.

## Replacement Personalization text

Copy this concise block into **Settings → Personalization**:

```text
Work as a cautious, pragmatic coding collaborator.

- State assumptions only when they materially affect behavior, public API, tests, architecture, safety, or external state.
- When ambiguity is low-risk and reversible, make the smallest reasonable assumption and state it. Ask only when the choice is material.
- Do only the minimum work needed to complete the task, including code changes and non-code actions. Keep edits surgical, follow existing local patterns, and do not refactor, reformat, rename, or remove unrelated code.
- Avoid speculative features, configuration, abstractions, and defensive handling without a demonstrated need.
- For bugs and behavior changes, define an observable check, implement the smallest fix, and verify it in proportion to risk.
- Preserve user-owned work. Before finishing, confirm every changed line is in scope and report checks run, checks not run, and remaining risk.
- Follow the closest applicable AGENTS.md and project instructions.
```

This block describes how to collaborate everywhere. It intentionally omits Python and Go details.

## Repository `AGENTS.md` template

Put language routing and executable commands in each repository:

```md
# Repository instructions

## Scope

- Follow existing local conventions unless they conflict with an explicit rule below.
- Keep changes minimal and preserve unrelated work.

## Language guidance

- Python: read the repository's pinned Python context map before Python code or test work.
- Go: read the repository's pinned Go context map before Go code or test work.
- If a referenced map is unavailable, report that before relying on memory or a mutable external URL.

## Verification

- Behavior change: add or update a behavior-focused test.
- Run the narrowest relevant tests first, then the repository lint and type/static-analysis commands.
- Do not weaken quality configuration to make checks pass.

## Commands

- Tests: `<project command>`
- Lint: `<project command>`
- Types/static analysis: `<project command>`
- Build: `<project command>`

## Done

- Requested behavior is verified.
- Every changed line serves the request.
- Unrelated changes remain untouched.
- Missing verification and remaining risk are reported.
```

Replace placeholders with real repository commands. A repository instruction that says only “follow this URL” is weaker than a pinned local map plus concrete commands.

## How to use the language repositories

### Python

This vault already provides a pinned, task-oriented mirror. Point a Python repository's `AGENTS.md` to [[Python Guidelines Context Map]] when the vault is accessible. For portability, copy or package the map and its linked notes inside the repository or a Codex skill.

### Go

The [Go guidelines repository](https://github.com/allexandrsokollov/guidelines-golang) currently exposes guidance for project structure, testing, and API error handling. Build a pinned Go context map before replacing the URL with a local reference.

## Personalization versus personal `AGENTS.md`

Codex documentation connects Settings custom instructions with personal `AGENTS.md` guidance. Treat them as one global layer: choose one main editing surface and avoid maintaining duplicate copies that can drift.

Use the global layer for stable preferences only. Use repository and nested files for concrete rules because Codex loads more specific guidance later in the instruction chain.

## Prompt template

For non-trivial tasks, use:

```text
Goal: <observable outcome>
Context: <relevant files, errors, examples, or decisions>
Constraints: <important boundaries only>
Done when: <tests, checks, or behavior that prove completion>
```

Do not repeat the entire guardrail document in every prompt. Add only task-specific information.

## Planning rules

Every non-trivial implementation plan must:

- State the minimum information required to implement the task, including the relevant files, current behavior, desired behavior, constraints, and completion evidence. Inspect available context first; ask the user only for missing information that would materially change the implementation.
- Propose the smallest code change that fully implements the requested behavior. Exclude speculative abstractions, unrelated refactors, cleanup, and optional features.
- Include at least one control point with the narrowest relevant tests. Name the behavior being tested and the expected passing result before proceeding.
- End with verification of the completed work against the requested behavior and completion criteria.
- If a test or verification step fails, diagnose the cause, revise the implementation, and repeat the failed checks. Do not declare completion until the checks pass or an external blocker is reported with the remaining risk.

## Rollout checklist

- [ ] Replace the long Personalization block with the concise version.
- [ ] Avoid duplicating it in personal `AGENTS.md`.
- [ ] Add a concrete `AGENTS.md` to each active repository.
- [ ] Pin or locally package Python and Go guidance rather than relying only on moving URLs.
- [ ] Add nested instructions only where a subtree genuinely differs.
- [ ] Start a new task/session so Codex rebuilds its instruction chain.
- [ ] Ask Codex to list active instruction sources and conflicts.
- [ ] For substantial work, settle material choices with a decision checkpoint.
- [ ] Start implementation from a compact accepted-decision handoff.
- [ ] After a repeated failure, update the narrowest responsible instruction layer.

Related: [[Codex Instruction Map]] · [[Codex Context Continuity]] · [[Python Guidelines Context Map]] · [[Codex Product Sources]]
