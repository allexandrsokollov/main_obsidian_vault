# Local Codex skills

This directory stores source copies of personal Codex skills. Codex does not
discover skills here automatically. Install a skill by copying its complete
directory into your Codex skills directory.

The examples below work from any checkout location and do not assume a
particular username. They use a POSIX-compatible shell; on Windows, use the
equivalent PowerShell commands with the same resolved directories.

## Resolve local directories

Run the following from anywhere inside this vault's Git checkout. Keep the
variables in the same shell session as the later commands:

```bash
VAULT_ROOT="$(git rev-parse --show-toplevel)"
CODEX_DIR="${CODEX_HOME:-$HOME/.codex}"
SKILLS_DIR="$CODEX_DIR/skills"
```

If the vault is not a Git checkout, set `VAULT_ROOT` to its absolute directory
instead. `CODEX_HOME` is optional; when it is unset, the examples use the
standard `.codex` directory in the current user's home directory.

## Install a skill

The installed vault-router layout should be:

```text
<skills-dir>/route-vault-context/
├── SKILL.md
├── agents/
│   └── openai.yaml
└── scripts/
    ├── vault_core.py
    ├── vault_router.py
    └── test_vault_router.py
```

Copy the complete skill directory, including `SKILL.md`, `agents/`, and
`scripts/`. Do not copy the scripts separately; their paths are resolved
relative to the skill directory.

To install it:

```bash
mkdir -p "$SKILLS_DIR"
cp -R "$VAULT_ROOT/skills/route-vault-context" "$SKILLS_DIR/"
```

To update an existing installed copy without deleting unrelated files, use the
same resolved variables:

```bash
mkdir -p "$SKILLS_DIR/route-vault-context"
cp -R "$VAULT_ROOT/skills/route-vault-context/." \
  "$SKILLS_DIR/route-vault-context/"
```

Start a fresh Codex task after installing or updating a skill so Codex can
discover the new metadata. Test explicit invocation with:

```text
Use $route-vault-context for this Python compatibility task. The vault root is
<absolute-path-to-vault>.
```

Replace the placeholder with the real vault directory. A personal instruction
may supply that location for repeated use, but a checked-in reusable skill
should not contain one user's absolute path.

For automatic reuse across tasks, each user may add a machine-local instruction
like this to their personal Codex instructions:

```text
Use the knowledge vault at <absolute-path-to-vault> when relevant. For matching
Python or Codex-guidance tasks, use $route-vault-context and pass that directory
as the vault root. If the vault is unavailable, report that before relying on
memory.
```

The path belongs in personal configuration because checkout locations differ;
keep the placeholder form in files intended to be shared.

## Run the vault router directly

The scripts require Python 3 and use only the standard library. The examples
use `python3`; use the Python 3 launcher appropriate for the local platform if
it has a different name.

```bash
python3 -B "$SKILLS_DIR/route-vault-context/scripts/vault_router.py" \
  signals \
  --vault "$VAULT_ROOT" \
  --map python
```

Available commands are `signals`, `route`, `search`, `section`, `links`, and
`audit`. Run `vault_router.py --help` or a command followed by `--help` for the
complete arguments.

## Verify before copying

Run the bundled test suite from the vault root:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover \
  -s "$VAULT_ROOT/skills/route-vault-context/scripts" \
  -p 'test_*.py'
```

Keep generated files such as `__pycache__/` out of both the source and installed
skill directories.
