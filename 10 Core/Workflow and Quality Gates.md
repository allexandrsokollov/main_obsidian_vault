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

- Read-only Git inspection is allowed. Codex may use commands such as `git status`, `git diff`, `git log`, `git show`, and `git blame` when they do not change repository state.
- Git mutations are human-only. Codex must not modify the working tree, index, refs, configuration, remotes, stash, history, or other local or remote state through Git.
- Tests are written or updated with every behavior change.
- Applicable tests, `ruff`, `mypy`, and `basedpyright` must pass before
  completion.
- Do not weaken, disable, or reconfigure quality rules to silence failures.
- Keep any unavoidable suppression local and specific, with a concrete explanation.

## Git boundary

- Use read-only Git commands when they provide useful evidence about user-owned changes, history, or the final diff.
- Do not use mutating options with an otherwise read-only command.
- Mutating invocations include staging or restoring files; creating, deleting, or switching branches or tags; changing configuration or remotes; stashing; fetching; pulling; committing; merging; rebasing; cherry-picking; reverting; resetting; cleaning; and pushing.
- If it is unclear whether a Git invocation can change local or remote state, do not run it; use a non-Git inspection method or ask the user.

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
