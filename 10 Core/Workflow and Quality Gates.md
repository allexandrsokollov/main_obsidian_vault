---
type: guideline
status: active
scope: python
source_revision: 885b4e41af02a3c432de5086e74d3bd347cc70ca
tags:
  - python
  - workflow
  - quality-gates
---

# Workflow and Quality Gates

## Non-negotiable workflow

- Codex must never merge pull requests, merge requests, or equivalent
  code-review changes, including through a UI, API, CLI, auto-merge, or merge
  queue. The final merge is human-only.
- Tests are written or updated with every behavior change.
- Behavior fixes use separate RED and GREEN stages. Keep RED test-only: change
  only the focused behavior test, run it, record the expected behavior failure,
  confirm there is no production-code diff, and report that evidence. Start
  production implementation only in the separately authorized GREEN stage.
- Applicable tests, `ruff`, `mypy`, and `basedpyright` must pass before
  completion.
- Do not weaken, disable, or reconfigure quality rules to silence failures.
- Keep any unavoidable suppression local and specific, with a concrete explanation.

## Before starting codebase work

This user-required gate applies to every language, before code exploration,
review, implementation planning, or editing.

- Use the installed `codebase-memory` skill and `codebase-memory-mcp` to create
  or update the code graph for each repository or worktree in the task's scope.
- Check `list_projects` and `index_status`, then run `index_repository` for
  the exact checkout to create a missing graph or refresh an existing graph.
  Wait for indexing to complete and verify its status before starting work.
- Keep indexing limited to the repositories in scope. Recheck and refresh the
  graph when switching checkouts or when source changes make it stale.
- If the tool is unavailable or indexing fails, report the blocker and stop
  before codebase work; do not silently skip this gate or claim the graph is
  current.
- Follow the skill's coverage checks and source-verification requirements
  when using graph results; successful indexing alone does not prove complete
  coverage.

## Before editing

- Restate the intended behavior in verifiable terms.
- Identify the smallest relevant test or reproduction command.
- State assumptions that affect behavior, architecture, tests, or public API.
- Identify applicable context through [[Python Guidelines Context Map]].
- Inspect existing conventions before creating a new pattern.

## During editing

- Change only files and lines required by the request.
- Add or update tests in the same change.
- Assess each new or materially changed test with [[Test Quality Rubric]]. For
  critical or questionable tests, establish sensitivity with a pre-fix
  failure, targeted mutation, or temporary defect when practical.
- Avoid unrelated formatting, renaming, cleanup, and refactoring.
- Keep suppressions exceptional; solve the underlying design issue where practical.

## Verification ladder

Run the narrowest useful checks first:

1. Focused test for changed behavior
2. Test-quality review with [[Test Quality Rubric]]
3. Related test module or package
4. Broader suite when risk or project practice requires it
5. `ruff` on the changed scope
6. `mypy` on the changed scope
7. `basedpyright` on the changed scope

Report the exact command and blocker when a check cannot run. Do not claim completion from inspection alone when executable verification is available.

## Verification provenance

- Run verification from the target repository with its canonical command,
  working directory, locked environment, and resolved dependencies.
- Another repository's virtual environment, a `PYTHONPATH` override, a sibling
  source checkout, or unpublished code carrying an existing released version
  does not verify the target repository.
- For every claimed gate, preserve enough evidence to identify the repository,
  command, checked paths, and dependency source or version. Report deviations
  and resulting risk instead of describing the gate as passed.
- Report unrelated baseline failures without repairing them unless they block
  the requested behavior and the user expands the scope.

## Done criteria

- Requested behavior is implemented.
- Tests cover success and relevant failure paths.
- New or materially changed tests have credible evidence on the rubric's two
  primary criteria; score bands guide improvement rather than act as an
  automatic gate.
- Changed behavior is verified through a real entry point when practical.
- `ruff`, `mypy`, and `basedpyright` pass without weakened configuration.
- Every changed line serves the request.
- No user-owned or unrelated work was reverted.

Related: [[Linting and Type Checking]] · [[Testing Strategy]] ·
[[Implementation Playbook]] · [[Upstream Sources]]
