---
type: playbook
status: active
scope: bash
verified: 2026-07-31
tags:
  - bash
  - shell
  - codex
  - review
---

# Bash Review Checklist

Review for data loss, injection, unintended execution, failure propagation, and
observable contract errors before style. Load the applicable notes from
[[Bash Guidelines Context Map]].

## Interpreter and interface

- [ ] The shebang, syntax, minimum Bash version, and supported platforms agree.
- [ ] Option parsing validates missing, invalid, and conflicting arguments.
- [ ] `--` and leading-dash operands are handled where applicable.
- [ ] Exit statuses, stdout, stderr, usage text, and side effects are intentional.
- [ ] A sourceable file has no undocumented top-level execution or caller-state
      mutation.

## Words and commands

- [ ] Expansions and array elements preserve their intended word boundaries.
- [ ] `"$@"` preserves caller arguments.
- [ ] Commands are arrays/direct invocations, not strings evaluated as code.
- [ ] Line and filename processing handles spaces, glob characters, and relevant
      delimiters without parsing `ls`.
- [ ] `printf` uses a constant format string.
- [ ] Dynamic operands cannot be reinterpreted as options.

## Failures and side effects

- [ ] Important command failures are handled explicitly, including inside
      functions, pipelines, and substitutions.
- [ ] Shell options are deliberate and their exceptional contexts are tested.
- [ ] Temporary paths are created securely and cleaned up idempotently.
- [ ] Partial output cannot replace valid state without validation.
- [ ] Destructive targets are validated as non-empty, narrow, and within the
      allowed boundary.
- [ ] Concurrent or repeated invocation cannot corrupt state.

## Security and environment

- [ ] Untrusted data is validated and never evaluated as shell code.
- [ ] Executables and fixed options are controlled; dynamic values are separate
      quoted arguments.
- [ ] The script uses the least necessary privilege.
- [ ] Environment variables and `PATH` are validated when they affect security
      or determinism.
- [ ] Logs and traces cannot disclose secrets.

## Tests

- [ ] Tests are assessed with [[Test Quality Rubric]], starting with meaningful
      behavior and defect sensitivity.
- [ ] Tests invoke a real public entry point where practical.
- [ ] Status, stdout, stderr, and side effects are asserted separately.
- [ ] Spaces, globs, leading dashes, empty values, and relevant newlines are
      covered.
- [ ] External-command and pipeline failures are exercised at material stages.
- [ ] Tests use isolated paths and cannot affect real user or system state.
- [ ] Compatibility claims are exercised on the supported matrix.

## Quality gates

- [ ] Relevant tests pass.
- [ ] `bash -n` passes on the declared minimum version.
- [ ] ShellCheck passes without broad exclusions.
- [ ] `shfmt` passes using the repository profile.
- [ ] Skipped checks and remaining platform/tool assumptions are reported.

Report actionable findings with file and line, expected impact, and the
smallest credible correction. If there are no findings, state that explicitly
and mention any verification gap.
