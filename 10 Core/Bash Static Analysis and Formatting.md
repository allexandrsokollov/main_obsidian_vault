---
type: guideline
status: active
scope: bash
verified: 2026-07-31
tags:
  - bash
  - shellcheck
  - shfmt
  - linting
  - formatting
  - quality-gates
---

# Bash Static Analysis and Formatting

## Required policy

- **Bash syntax checking, ShellCheck, and `shfmt` are required** for production
  Bash code and Bash-based tests they support.
- Check files against the interpreter they declare. A Bash file is checked as
  Bash; a POSIX `sh` file is checked separately as `sh`.
- Use a repository-pinned tool version in CI. Local versions may be newer, but
  CI must be reproducible.
- Do not weaken or globally exclude diagnostics to make a failure disappear.
  Fix the issue or use the narrowest justified suppression.
- Formatting may follow an established repository configuration. New
  repositories use the baseline below unless the team documents another
  consistent style.

## Verification commands

Replace the example paths with all production scripts, sourced libraries, and
supported Bash test helpers in the repository.

```bash
bash -n scripts/deploy.sh lib/common.bash
shellcheck -x -s bash scripts/deploy.sh lib/common.bash
shfmt -d -ln bash -i 2 -ci -bn scripts/deploy.sh lib/common.bash
bats test
shfmt -d -ln bats -i 2 -ci -bn test/*.bats
```

Use `bash -n` because it verifies the real target parser. Keep `shfmt` parsing
as an additional check; it can find static syntax problems that `bash -n` does
not reject.

For local formatting:

```bash
shfmt -w -ln bash -i 2 -ci -bn scripts/deploy.sh lib/common.bash
shfmt -w -ln bats -i 2 -ci -bn test/*.bats
```

Review formatted output and any automated simplification. Verification and CI
must use non-mutating commands.

## Minimum formatting profile

The default new-repository style is the `shfmt` profile that closely resembles
the Google shell style guide:

```text
-ln bash -i 2 -ci -bn
```

It means Bash syntax, two-space indentation, indented `case` bodies, and binary
operators permitted at the start of continuation lines. A repository may put
equivalent settings in `.editorconfig`:

```ini
[*.sh]
shell_variant = bash
indent_style = space
indent_size = 2
switch_case_indent = true
binary_next_line = true
```

If command-line parser or printer flags are supplied, `shfmt` does not apply
EditorConfig formatting options. Choose one canonical invocation and use it in
editors, local checks, and CI. Extensionless executables and `.bats` files must
also be included deliberately.

## ShellCheck policy

- Run ShellCheck over executable scripts and sourced libraries. Use `-x` when
  source paths can be resolved.
- Correct source relationships with a narrow `# shellcheck source=...`
  directive when a runtime-computed source path prevents analysis.
- Put a rule suppression immediately before the smallest affected command or
  function and explain why the flagged behavior is intentional and safe.
- Do not add global excludes or blanket file disables unless generated or
  vendored code is outside the maintained source boundary.
- Treat quoting, array, redirection, masked-status, portability, and destructive
  command findings as correctness or safety issues, not cosmetic style.

Example of making a dynamic source path analyzable without disabling a rule:

```bash
# shellcheck source=lib/common.bash
source "$script_dir/lib/common.bash"
```

Prefer restructuring code so that no suppression is necessary.

## Dialect and version checks

- The shebang, ShellCheck dialect, `shfmt` dialect, and test interpreter must
  agree.
- When POSIX compatibility is required, use `sh -n`, `shellcheck -s sh`,
  `shfmt -ln posix`, and tests under every supported `sh` implementation. Do
  not merely run Bash in POSIX mode and assume equivalence.
- Static tools do not prove compatibility with an older Bash version. Exercise
  the suite using the minimum supported version.
- `bash -n` parses but does not execute the script; it does not prove commands
  exist, arguments are safe, or runtime branches work.

## Review checklist

- [ ] Every maintained Bash file is included, including extensionless scripts
      and sourced libraries.
- [ ] The declared interpreter and configured dialect match.
- [ ] `bash -n` passes using the minimum supported Bash version.
- [ ] ShellCheck passes without unexplained or broad exclusions.
- [ ] `shfmt` passes using one repository-wide configuration.
- [ ] Bats or other shell test syntax is checked with its supported dialect.
- [ ] CI pins tool versions and uses non-mutating verification commands.
- [ ] Runtime and platform behavior is tested separately from static analysis.

Related: [[Bash Design and Safety]] · [[Bash Workflow and Quality Gates]] ·
[[Bash Sources]]
