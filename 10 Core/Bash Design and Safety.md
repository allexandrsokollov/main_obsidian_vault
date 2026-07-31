---
type: guideline
status: active
scope: bash
verified: 2026-07-31
tags:
  - bash
  - shell
  - design
  - security
  - portability
---

# Bash Design and Safety

## Design target

Use Bash for small programs that primarily compose commands. A production
script should make its interpreter, inputs, side effects, failure behavior, and
output contract obvious. Move substantial data modeling, concurrency, parsing,
or complex business rules to a more structured language before the script
becomes difficult to test and reason about.

## Interpreter contract

- Declare Bash in the shebang and declare the minimum supported Bash version in
  repository documentation or a startup check when version-specific features
  matter.
- Use `#!/usr/bin/env bash` when the selected environment or toolchain controls
  `PATH`; use an absolute interpreter path when the deployment contract fixes
  that path. Do not assume one choice is portable to every environment.
- Put shell options in the script, not in shebang arguments, so behavior is the
  same when the script is invoked as `bash script`.
- Do not label a script `#!/bin/sh` if it uses Bash arrays, `[[ ... ]]`,
  `mapfile`, process substitution, `source`, or other Bash-only syntax.
- Test on every Bash version and operating system the script claims to support.
  Do not infer portability from one successful local run.

## Program structure

- Keep top-level execution small: constants, function definitions, then
  `main "$@"`.
- Give each function one job and use `local` for function variables. Declare a
  local separately from command substitution so the declaration cannot mask the
  command's exit status.
- Pass values through arguments and stdout rather than hidden globals. Reserve
  uppercase names for exported environment variables and true constants.
- Use `readonly` for invariants after initialization.
- Parse options with `getopts` or a tested parser. Validate argument count,
  allowed values, and mutually exclusive modes before side effects.
- Resolve resources relative to the script only when that is the documented
  contract. Otherwise accept explicit paths and do not assume the caller's
  working directory.
- Sourced libraries must define functions and constants without executing the
  program, changing the caller's shell options, installing global traps, or
  calling `exit`. Return failures to the caller.

Use a direct-execution guard for a file that is both executable and sourceable:

```bash
if [[ ${BASH_SOURCE[0]} == "$0" ]]; then
  main "$@"
fi
```

## Words, arguments, and data

- Quote parameter expansion, command substitution, and array expansion unless
  word splitting or glob expansion is explicitly required and documented.
- Preserve caller arguments with `"$@"`; do not use unquoted `$@` or `$*`.
- Store command arguments in arrays, not strings. Invoke them with
  `"${command_args[@]}"`.
- Use `--` before operands for commands that support it, especially when a path
  or user-provided value may begin with `-`. When a command lacks `--`, use a
  safe operand form such as `./name` or validate against its option grammar.
- Use `IFS= read -r` for line input. Use NUL-delimited producers and consumers
  when filenames may contain newlines, for example `find ... -print0` with
  `read -r -d ''` or `mapfile -d ''`.
- Do not parse `ls` output. Iterate globs or consume a command's structured,
  delimiter-safe output.
- Prefer `printf` over `echo` for data and diagnostics. Keep the format string
  constant: `printf '%s\n' "$value"`.
- Use `[[ ... ]]` for Bash string/file conditions and `(( ... ))` for
  arithmetic. Use a command directly as a condition instead of checking `$?`
  later.

## Exit status and error handling

- Treat zero as success and non-zero as a meaningful part of each command's
  contract. Distinguish expected negative results from operational failures.
- Check every failure that affects correctness, cleanup, or safety at the point
  where it occurs: use `if command; then`, `if ! command; then`, `command ||
  die`, or capture and handle the status immediately.
- Do not rely on `set -e` to identify every important failure. Bash exempts
  several conditional and pipeline contexts, and command substitutions and
  subshells add further edge cases.
- If the repository uses `errexit`, keep explicit handling at expected-failure
  sites and test functions, pipelines, substitutions, arithmetic, and cleanup
  paths affected by it.
- Enable `set -o pipefail` when a failed non-final pipeline stage must fail the
  pipeline. Handle pipelines where an early consumer exit and `SIGPIPE` are
  expected rather than assuming every non-zero stage is a defect.
- Enable `set -u` when unset variables should be fatal, then use intentional
  defaults or requirements such as `${value:-default}` and `${value:?message}`.
  Test empty arrays, optional environment variables, and optional arguments on
  the minimum supported Bash version.
- Capture status before another command overwrites it. Keep diagnostics on
  stderr, preserve the most useful failure status, and avoid generic success
  after partial work.
- Treat `ERR` traps as diagnostics, not as the primary error-control mechanism.
  Their inheritance and execution follow the same context-sensitive rules as
  `errexit`.

## Filesystem, cleanup, and destructive operations

- Create temporary files or directories with `mktemp`; never predict names with
  `$$`, timestamps, or a fixed `/tmp` path. Install cleanup only after creation
  succeeds and quote the path in the trap action.
- Use restrictive permissions such as `umask 077` when temporary or output data
  may contain secrets.
- Make cleanup idempotent and preserve the original status. Test normal exit,
  handled failure, and relevant signals.
- Use atomic replacement—write a sibling temporary file, validate it, then
  rename it—when readers must not observe partial output.
- Before deletion, overwrite, privilege escalation, or remote mutation, validate
  that every target is non-empty, resolved as expected, within the allowed
  boundary, and not a broad root. Quote it and pass it after `--` where
  supported.
- Prefer an explicit dry-run or confirmation boundary for high-impact manual
  operations. Non-interactive automation must fail closed rather than silently
  choosing a dangerous default.
- Use a locking or idempotency strategy when concurrent invocations can corrupt
  state. Document whether the chosen mechanism is platform-specific.

## Security and environment

- Never construct code from untrusted data. Avoid `eval`, `bash -c` with
  interpolated values, generated shell fragments, and variables containing
  commands.
- Keep executable names and fixed options in code. Put each validated dynamic
  value in its own quoted argument and use `--` where supported.
- Validate untrusted inputs with an allowlist appropriate to the command's
  operand grammar. Quoting prevents shell splitting; it does not prevent a value
  from being interpreted as a dangerous option or valid destructive operand.
- Run with the least privilege required. Isolate privileged actions in small,
  reviewable functions and never accept privilege-changing flags from untrusted
  input.
- Treat environment variables as untrusted input unless the execution boundary
  guarantees them. Validate `PATH`, locale, configuration paths, and tool-specific
  variables when they affect security or determinism.
- Check required commands with `command -v` before side effects. Pin or record
  external-tool versions when their behavior is part of the contract.
- Do not enable `set -x` around secrets. If tracing is needed, make it opt-in,
  send it to a controlled destination, and redact sensitive values.

## Output contract

- Reserve stdout for the command's documented result. Send diagnostics,
  progress, and logs to stderr.
- Provide a concise usage message and use stable, documented exit statuses when
  callers distinguish usage, expected absence, and operational failure.
- Do not log secrets, tokens, full credential-bearing URLs, or uncontrolled
  environment dumps.
- Make non-interactive behavior deterministic. Do not emit color or prompts
  unless explicitly requested or attached to an appropriate terminal.

## Forbidden

- Unquoted expansions that accidentally split or glob.
- Command construction in strings or `eval` for ordinary argument passing.
- Parsing filenames through whitespace-delimited command substitution.
- Predictable temporary paths.
- `cd` without checking success when later operations depend on the directory.
- A library that mutates caller options, traps, positional parameters, or
  working directory as an undocumented import side effect.
- Destructive commands whose target can be empty, `.`/`..`, a filesystem root,
  or outside the declared boundary.
- Broad ShellCheck exclusions used to hide findings.
- Clever one-liners that obscure status propagation, quoting, or side effects.

## Minimal executable shape

This is a shape, not a universal template. Select options according to the
script's tested error policy.

```bash
#!/usr/bin/env bash

set -u
set -o pipefail

readonly PROGRAM_NAME=${0##*/}

die() {
  printf '%s: %s\n' "$PROGRAM_NAME" "$*" >&2
  exit 1
}

require_command() {
  local command_name=$1
  command -v "$command_name" >/dev/null 2>&1 ||
    die "required command not found: $command_name"
}

main() {
  (($# == 1)) || die "usage: $PROGRAM_NAME INPUT"

  local input=$1
  local result
  if ! result=$(some_command -- "$input"); then
    die "some_command failed for the requested input"
  fi

  printf '%s\n' "$result"
}

main "$@"
```

## Design review prompts

- Is Bash still the simplest safe language for this job?
- Is the interpreter and minimum version explicit?
- Can every input survive spaces, tabs, glob characters, leading dashes, and
  relevant newlines?
- Does each important command failure have an intentional outcome?
- Can partial execution leave corrupt, overbroad, or privileged state?
- Are stdout, stderr, exit status, and filesystem effects stable contracts?
- Can the file be sourced without executing or mutating the caller?

Related: [[Bash Static Analysis and Formatting]] · [[Bash Testing Strategy]] ·
[[Bash Workflow and Quality Gates]] · [[Bash Sources]]
