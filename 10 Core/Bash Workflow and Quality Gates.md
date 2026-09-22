---
type: guideline
status: active
scope: bash
verified: 2026-07-31
tags:
  - bash
  - shell
  - workflow
  - quality-gates
---

# Bash Workflow and Quality Gates

## Non-negotiable workflow

- Read-only Git inspection is allowed under the repository `AGENTS.md`; Git
  mutations remain human-only.
- Tests are written or updated with every behavior change.
- Behavior fixes use separate RED and GREEN stages. Keep RED test-only: change
  only the focused behavior test, run it, record the expected behavior failure,
  confirm there is no production-code diff, and report that evidence. Start
  production implementation only in the separately authorized GREEN stage.
- Applicable tests, `bash -n`, ShellCheck, and `shfmt` must pass before
  completion.
- Portability claims require execution on every supported interpreter/platform,
  not static analysis alone.
- Destructive or privileged behavior requires a safe test boundary and explicit
  verification of refusal paths before any live-path verification.
- Do not weaken, disable, or reconfigure quality rules to silence failures.
- Keep unavoidable suppressions local and specific, with a concrete safety
  explanation.

## Before editing

- Restate success as observable exit status, stdout, stderr, and side effects.
- Identify the interpreter, minimum version, platforms, and external utilities
  in scope.
- Identify the smallest relevant test or reproduction command.
- State assumptions that affect public CLI behavior, portability, destructive
  scope, privilege, or environment.
- Select context through [[Bash Guidelines Context Map]].
- Inspect existing shebang, options, style, tests, and CI commands before
  creating a new pattern.

## During editing

- Change only files and lines required by the request.
- Add or update tests in the same change.
- Assess each new or materially changed test with [[Test Quality Rubric]]. For
  critical or questionable tests, establish sensitivity with a pre-fix failure
  or targeted temporary defect when practical.
- Preserve the script's public status and output contracts unless the change is
  explicit.
- Keep expansions, arrays, filenames, and external-command arguments intact.
- Avoid unrelated formatting, renaming, cleanup, and refactoring.
- Do not test destructive behavior against real user, repository, system, or
  shared paths.

## Verification ladder

Run the narrowest useful checks first:

1. Focused behavior test or safe reproduction
2. Test-quality review with [[Test Quality Rubric]]
3. Related Bats file or test package
4. Syntax check with the minimum supported Bash: `bash -n`
5. ShellCheck on the changed and sourced scope
6. `shfmt` diff check on the changed and test scope
7. Broader test suite
8. Supported Bash-version and operating-system matrix when portability or
   platform tools are affected
9. Safe end-to-end entry point in a disposable environment when practical

Report the exact command and blocker when a check cannot run. Do not claim
runtime correctness from syntax or static inspection alone.

## Done criteria

- Requested behavior is implemented through the real entry point.
- Tests cover success, relevant failure paths, adversarial inputs, and side
  effects.
- New or materially changed tests have credible evidence on the rubric's two
  primary criteria.
- `bash -n`, ShellCheck, and `shfmt` pass without weakened configuration.
- Compatibility-sensitive behavior passes on the declared support matrix.
- Destructive and privileged paths fail closed and were verified only in an
  isolated, authorized boundary.
- Every changed line serves the request.
- No user-owned or unrelated work was reverted.

Related: [[Bash Static Analysis and Formatting]] · [[Bash Testing Strategy]] ·
[[Bash Implementation Playbook]] · [[Bash Sources]]
