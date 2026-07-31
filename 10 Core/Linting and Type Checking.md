---
type: guideline
status: active
scope: python
verified: 2026-07-31
tags:
  - python
  - ruff
  - mypy
  - linting
  - typing
  - quality-gates
---

# Linting and Type Checking

## Required policy

- **Ruff and mypy are required** for production code and tests.
- Use Ruff for both formatting and linting. Do not add Black for formatting.
- The repository's `pyproject.toml` **MUST** contain the baseline below or a
  demonstrably stricter configuration.
- A stricter configuration may select more Ruff rules, ignore fewer rules,
  remove per-file exceptions, or remove mypy relaxations. It must not remove a
  baseline rule, add a broader ignore, disable mypy strict mode, or weaken an
  explicit mypy check.
- Project paths and the Python target **MUST** match the repository. Changing
  only `app`/`src` paths or the declared Python version is an adaptation, not a
  relaxation; all production and test packages must remain in scope.
- Suppressions must be local, narrow, and explained. Do not weaken shared
  configuration to make a failure disappear.

## Commands

Use the repository's actual production and test paths in place of
`${CODE_DIRS}` and `${TEST_DIRS}`.

For local formatting and automatic fixes:

```bash
uv run ruff format ${CODE_DIRS} ${TEST_DIRS}
uv run ruff check ${CODE_DIRS} ${TEST_DIRS} --fix --unsafe-fixes
```

Review every unsafe fix. Verification and CI must use non-mutating commands:

```bash
uv run ruff format --check ${CODE_DIRS} ${TEST_DIRS}
uv run ruff check ${CODE_DIRS} ${TEST_DIRS}
uv run mypy ${CODE_DIRS} ${TEST_DIRS}
```

## Minimum Ruff configuration

```toml
[tool.ruff]
line-length = 100
target-version = "py313"
fix = true

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
skip-magic-trailing-comma = false
line-ending = "auto"
docstring-code-format = true

[tool.ruff.lint]
select = [
    "E",      # pycodestyle errors
    "W",      # pycodestyle warnings
    "F",      # Pyflakes
    "I",      # isort
    "B",      # flake8-bugbear
    "C4",     # flake8-comprehensions
    "UP",     # pyupgrade
    "ARG",    # flake8-unused-arguments
    "SIM",    # flake8-simplify
    "Q",      # flake8-quotes
    "N",      # pep8-naming
    "RUF",    # Ruff-specific rules
    "T20",    # flake8-print
    "RET",    # flake8-return
    "PERF",   # Perflint
    "PIE",    # flake8-pie
    "PT",     # flake8-pytest-style
    "FLY",    # flynt
    "FURB",   # refurb
    "LOG",    # flake8-logging
]
extend-select = ["G004"] # Require lazy %-style logging interpolation.
fixable = ["ALL"]
unfixable = []
ignore = [
    "B008",   # FastAPI dependency injection uses calls in defaults.
    "RUF001", # Allow ambiguous Unicode in strings.
    "RUF002", # Allow ambiguous Unicode in docstrings.
    "RUF003", # Allow ambiguous Unicode in comments.
    "N811",   # Allow constants imported under non-constant names.
    "N814",   # Allow camelCase names imported as constants.
    "SIM117", # Allow separate context managers instead of nested with.
]

[tool.ruff.lint.per-file-ignores]
"app/api/routes/*.py" = ["ARG001"]
"tests/**/*.py" = [
    "ARG001",
    "ARG002",
    "PT004",
]

[tool.ruff.lint.isort]
known-first-party = ["app"]
force-sort-within-sections = true
combine-as-imports = true

[tool.ruff.lint.flake8-quotes]
inline-quotes = "double"
docstring-quotes = "double"
multiline-quotes = "double"

[tool.ruff.lint.flake8-pytest-style]
fixture-parentheses = true
mark-parentheses = true

[tool.ruff.lint.flake8-bugbear]
extend-immutable-calls = [
    "fastapi.Depends",
    "fastapi.Query",
    "fastapi.Path",
    "fastapi.Body",
]

[tool.ruff.lint.pycodestyle]
max-line-length = 100
```

The listed ignores are ceilings, not defaults to copy without thought. Remove
framework-specific ignores and exceptions when a repository does not need
them. Update `known-first-party` and per-file paths to the actual package
layout without reducing checked scope.

## Minimum mypy configuration

```toml
[tool.mypy]
python_version = "3.13"
files = ["src", "tests"]
exclude = [
    "^build/",
    "^dist/",
    "^\\.venv/",
]

strict = true
disallow_any_generics = true
disallow_subclassing_any = true
disallow_untyped_calls = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_untyped_decorators = true
no_implicit_optional = true
strict_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_return_any = true
warn_unreachable = true
no_implicit_reexport = true
strict_equality = true
strict_equality_for_none = true
extra_checks = true
local_partial_types = true

pretty = true
show_error_codes = true
show_error_code_links = true
show_column_numbers = true
ignore_missing_imports = false
namespace_packages = true
incremental = true
cache_dir = ".mypy_cache"

# Enable only the plugins used by the repository, at the top level so they
# apply to production code as well as tests.
plugins = [
    "sqlalchemy.ext.mypy.plugin",
    "pydantic.mypy",
]

[[tool.mypy.overrides]]
module = ["tests.*"]
disallow_untyped_defs = false
disallow_incomplete_defs = false
disallow_untyped_decorators = false
```

The test override is the maximum permitted relaxation. Omitting any or all of
its three exceptions is stricter. Never add `ignore_missing_imports = true` or
an `ignore_errors = true` override. Keep relevant framework plugins enabled;
remove a plugin only when its framework is not a project dependency.

## Review checklist

- [ ] Ruff formats and checks every production and test package.
- [ ] The complete Ruff rule baseline remains enabled.
- [ ] Every ignore is no broader than the baseline and is actually required.
- [ ] mypy checks every production and test package with `strict = true`.
- [ ] Explicit mypy strictness flags are not disabled by an override.
- [ ] Missing third-party typing is handled rather than globally ignored.
- [ ] Ruff and mypy pass using non-mutating verification commands.

Related: [[Workflow and Quality Gates]] · [[Typing and DTO Contracts]] ·
[[Interpretation Notes]] · [[Upstream Sources]]
