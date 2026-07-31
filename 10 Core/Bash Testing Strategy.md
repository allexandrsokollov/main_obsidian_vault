---
type: guideline
status: active
scope: bash
verified: 2026-07-31
tags:
  - bash
  - shell
  - testing
  - bats
---

# Bash Testing Strategy

## Testing target

Tests should prove the script's public contract: exit status, stdout, stderr,
filesystem and process effects, and behavior under the supported interpreter and
environment. Use the repository's established framework; default to Bats for a
new Bash test suite.

Judge each new, materially changed, or specifically reviewed test with
[[Test Quality Rubric]]. Protect meaningful behavior and prove that the test
responds to the relevant defect before relying on its aggregate score.

## Preferred entry points

- Executable CLI invoked as a real subprocess
- Public function in a sourceable library
- Installed wrapper or packaging entry point
- Scheduled, container, or CI entry point when its environment is part of the
  behavior

Exercise the path real callers use. Unit-test a function only when the file has
a deliberate sourceable-library contract and the integration path is covered
elsewhere.

## Required assertions

- Assert the exact exit status when callers rely on it.
- Assert stdout and stderr separately. Do not let diagnostic output pollute a
  machine-readable stdout contract.
- Assert created, modified, and removed files; permissions; content; and atomic
  replacement when relevant.
- Assert that forbidden side effects did not happen on validation or dependency
  failure.
- Assert arguments passed to external boundaries when quoting, option
  termination, or injection resistance is relevant.
- For a multi-step mutation, assert the state after failure at each material
  boundary, including cleanup and rollback behavior.

## Scenario requirements

- Keep tests deterministic, isolated, and independent of execution order.
- Give each test its own temporary directory. Do not depend on a developer's
  home directory, current shell configuration, network, locale, or installed
  aliases.
- Control `PATH`, locale, time zone, time, randomness, user identity, and
  environment variables when they affect behavior.
- Include representative adversarial values: spaces, tabs, glob characters,
  leading dashes, empty strings, Unicode, embedded newlines where supported,
  missing files, symlinks, and permission failures.
- Cover zero matches, one match, and multiple matches for glob or discovery
  behavior.
- Cover every documented option, invalid option, missing option argument,
  positional-argument count, and `--` boundary.
- Cover external-command success, expected negative status, command-not-found,
  and operational failure where each leads to different behavior.
- Test pipeline failure at each stage when `pipefail` or `PIPESTATUS` affects
  correctness.
- Test normal exit and relevant `INT`/`TERM` cleanup for scripts that own
  temporary or partial state.
- Run compatibility-sensitive suites on the minimum and current supported Bash
  versions and required operating systems.

## External commands and fakes

- Use real standard utilities when their platform behavior is part of the
  contract and the test environment pins that platform.
- Replace network services, privileged commands, destructive tools, and other
  uncontrolled boundaries with small executable fakes placed first in a
  test-only `PATH`.
- A fake must record its argv without re-splitting it, emit configured stdout
  and stderr, and return the configured status. It must not silently accept
  arguments the real command would reject when that grammar matters.
- Do not mock Bash builtins or reproduce shell expansion in a fake. Let the
  target Bash perform quoting, expansion, redirection, and status propagation.
- Never let a test fake shadow a real command outside the test process or
  temporary environment.

## Bats guidance

- Use `run` when the test needs to inspect a command's status and captured
  output. Remember that `run` itself succeeds so assertions can continue.
- Keep setup explicit and use Bats temporary directories for isolated state.
- Use exact filenames with `load`; do not depend on deprecated implicit suffix
  lookup.
- Never commit a focused-only test configuration. A focused Bats run is not a
  complete suite.
- Keep test helpers valid and statically analyzable Bash where practical, and
  format `.bats` files with the Bats dialect.

## Sensitivity evidence

For a bug fix, capture the pre-fix failure. For new or refactored behavior,
temporarily introduce the smallest relevant defect or use a targeted mutation
when practical—for example remove `--`, unquote an expansion, change a handled
status, or skip cleanup—and confirm that the test fails for the intended
reason. Restore the production logic before completion.

## Anti-patterns

- Asserting only that the script ran without crashing.
- Combining stdout and stderr when the interface distinguishes them.
- Testing only simple filenames and successful commands.
- Sourcing an executable that performs top-level side effects.
- Stubbing every external utility so thoroughly that no real entry path remains.
- Depending on the developer machine's `PATH`, locale, credentials, or home
  directory.
- Sleeping to coordinate processes when a deterministic readiness or wait
  mechanism exists.
- Running destructive commands against real user or shared paths in tests.

Related: [[Test Quality Rubric]] · [[Bash Design and Safety]] ·
[[Bash Workflow and Quality Gates]] · [[Bash Sources]]
