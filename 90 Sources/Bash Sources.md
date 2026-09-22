---
type: source-index
status: active
scope: bash
verified: 2026-07-31
tags:
  - bash
  - shell
  - sources
  - provenance
---

# Bash Sources

The Bash notes synthesize the sources below. Unlike the Python notes, they are
not a summary of one pinned upstream repository. Exact language behavior comes
from the interpreter or portability specification; tooling behavior comes from
the tool's own documentation. Style recommendations are adapted to the vault's
workflow and safety contract.

## Language semantics

- [GNU Bash Reference Manual, edition 5.3](https://www.gnu.org/software/bash/manual/bash.html)
  → interpreter invocation, quoting, expansions, arrays, conditionals,
  functions, builtins, traps, options, pipelines, status, and portability
- [Bash pipelines](https://www.gnu.org/software/bash/manual/html_node/Pipelines)
  → subshell execution, `pipefail`, and pipeline status
- [Bash exit status](https://www.gnu.org/software/bash/manual/html_node/Exit-Status.html)
  → success/failure conventions and reserved statuses
- [Bourne shell builtins](https://www.gnu.org/software/bash/manual/html_node/Bourne-Shell-Builtins.html)
  → `getopts`, `read`, `trap`, `return`, `source`, and related behavior
- [POSIX.1-2024 Shell Command Language](https://pubs.opengroup.org/onlinepubs/9799919799/utilities/V3_chap02.html)
  → exact requirements only when a script declares POSIX `sh` portability

## Static analysis and formatting

- [ShellCheck](https://github.com/koalaman/shellcheck) and its [diagnostic
  reference](https://www.shellcheck.net/wiki/) → common quoting, status,
  portability, command, and destructive-operation defects
- [`shfmt` documentation](https://github.com/mvdan/sh/blob/master/cmd/shfmt/shfmt.1.scd)
  → dialect parsing, CI diff checks, formatting flags, and EditorConfig behavior
- [Google Shell Style Guide](https://google.github.io/styleguide/shellguide.html)
  → maintainability, naming, structure, and the default two-space formatting
  profile; treated as a style input rather than a language specification

## Testing and security

- [Bats-core documentation](https://bats-core.readthedocs.io/en/stable/)
  and [writing tests](https://bats-core.readthedocs.io/en/stable/writing-tests.html)
  → Bash test execution, `run`, loading helpers, focus behavior, and test
  temporary directories
- [GNU Coreutils `mktemp`](https://www.gnu.org/software/coreutils/manual/html_node/mktemp-invocation.html)
  → unpredictable, securely created temporary files and directories
- [OWASP OS Command Injection Defense](https://cheatsheetseries.owasp.org/cheatsheets/OS_Command_Injection_Defense_Cheat_Sheet.html)
  → avoiding command construction, separating commands from arguments,
  allowlist validation, `--`, and least privilege

## Local interpretations

### RED-before-GREEN checkpoints

The separate, test-only RED checkpoint in [[Bash Workflow and Quality Gates]]
is a local collaboration preference rather than wording from the Bash, Bats,
or style-guide sources. Record the expected behavior failure and confirm there
is no production-code diff before a separately authorized GREEN stage.

### Bash versus POSIX `sh`

The guide chooses an explicit dialect instead of a lowest-common-denominator
hybrid. Bash scripts may use Bash features and must declare/test their minimum
Bash version. POSIX scripts use a separate `sh` tool and runtime matrix.

### Shell suitability

The Google guide recommends shell for small utilities and wrappers and suggests
moving beyond it as size or control flow grows. This vault treats complexity,
testability, parsing, concurrency, and data modeling—not a fixed line count—as
the decision boundary.

### Error options are not error handling

The Bash manual documents that `errexit` is ignored in several conditional and
pipeline contexts, that pipeline elements normally run in subshells, and that
pipeline status changes under `pipefail`. Therefore [[Bash Design and Safety]]
requires explicit checks for failures that matter. `set -e`, `set -u`, and
`pipefail` are deliberate, tested policy choices rather than a universal line
copied into every script.

### Formatting baseline

The new-repository `shfmt` profile `-ln bash -i 2 -ci -bn` is the tool's
documented approximation of the Google style. Existing consistent repository
formatting takes precedence; static-analysis and safety rules do not become
optional when style differs.

### Quoting and `--`

Quoting preserves one shell argument but cannot stop a syntactically valid
value from becoming an option or destructive operand. The guide therefore pairs
quoted arguments with command-specific validation and `--` where supported.

## Maintenance

When updating the Bash guidance:

1. Recheck the Bash manual edition and supported interpreter versions.
2. Review official ShellCheck, `shfmt`, Bats, POSIX, GNU Coreutils, and OWASP
   documentation affected by the change.
3. Update only notes whose behavior or policy changed.
4. Record local judgment under **Local interpretations** instead of presenting
   it as specification wording.
5. Re-run internal-link, metadata, and Markdown checks.
