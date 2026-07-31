---
type: playbook
status: active
scope: bash
verified: 2026-07-31
tags:
  - bash
  - shell
  - codex
  - implementation
---

# Bash Implementation Playbook

## 1. Frame the change

- Express success as exit status, stdout, stderr, and side effects.
- State the Bash version, platforms, privilege level, and external utilities.
- Identify whether the file is executable, sourceable, or both.
- Select context through [[Bash Guidelines Context Map]].
- Identify the smallest safe test, command, or inspection that proves each step.

## 2. Inspect locally

- Find the real entry point, callers, tests, shebang, shell options, traps,
  sourced files, CI commands, and formatting configuration.
- Trace data from arguments and environment through expansions into external
  commands and filesystem paths.
- Trace exit statuses through functions, conditionals, pipelines, command
  substitutions, and cleanup.
- Prefer an existing local pattern only when it satisfies the strict safety
  guidance.
- Note unrelated defects but do not fix them without scope.

## 3. Establish evidence

- Bug fix: reproduce the bug with a focused failing test or safe command.
- New behavior: write a focused scenario that states status, output, and effects.
- Refactor: capture the public behavior before changing structure.
- Destructive or privileged behavior: create a disposable test boundary and
  prove invalid or broad targets are rejected before testing the allowed path.

## 4. Implement minimally

- Keep the script as orchestration; move complex data or policy elsewhere.
- Parse and validate all inputs before side effects.
- Pass dynamic values as quoted array elements, never constructed command text.
- Check important failures explicitly; do not rely on `errexit` alone.
- Create temporary state securely and install idempotent cleanup after creation.
- Keep stdout, stderr, and exit statuses stable and intentional.
- Avoid a new helper or sourced library until it removes repeated knowledge or
  isolates a meaningful boundary.

## 5. Verify progressively

1. Run the focused behavior test.
2. Demonstrate test sensitivity when practical, then restore the intended code.
3. Run the related Bats file or package.
4. Run `bash -n`, ShellCheck, and `shfmt` on the changed scope.
5. Run broader and compatibility suites when risk warrants it.
6. Exercise the real entry point in a disposable environment.
7. Inspect the final diff with read-only Git commands and confirm every changed
   line is in scope.

## 6. Hand off

Report:

- Observable outcome and preserved CLI contracts
- Files changed
- Bash versions and platforms verified
- Tests and quality checks run
- Checks not run and exact reason
- Remaining risk, external-tool assumption, or source ambiguity

Git mutations and history remain human-owned under
[[Bash Workflow and Quality Gates]].
