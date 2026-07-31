# Local Codex skills

This directory stores source copies of personal Codex skills. Codex does not
discover skills here automatically. Install a skill by copying its complete
directory into your Codex skills directory.

## Install a skill

For the current user, Codex skills belong under:

```text
/Users/allxndrskllv/.codex/skills
```

Copy the complete skill directory, including `SKILL.md`, `agents/`, and
`scripts/`. Do not copy the scripts separately; their paths are resolved
relative to the skill directory.

For the vault router, the installed layout should be:

```text
/Users/allxndrskllv/.codex/skills/route-vault-context/
├── SKILL.md
├── agents/
│   └── openai.yaml
└── scripts/
    ├── vault_core.py
    ├── vault_router.py
    └── test_vault_router.py
```

To install it from the terminal:

```bash
mkdir -p /Users/allxndrskllv/.codex/skills
cp -R \
  /Users/allxndrskllv/Documents/mian/skills/route-vault-context \
  /Users/allxndrskllv/.codex/skills/
```

To update an existing installed copy without deleting unrelated files:

```bash
rsync -a --exclude '__pycache__' \
  /Users/allxndrskllv/Documents/mian/skills/route-vault-context/ \
  /Users/allxndrskllv/.codex/skills/route-vault-context/
```

Start a fresh Codex task after installing or updating a skill so Codex can
discover the new metadata. Test explicit invocation with:

```text
Use $route-vault-context for this Python compatibility task.
```

## Run the vault router directly

The scripts require Python 3 and use only the standard library. For example:

```bash
python3 \
  /Users/allxndrskllv/.codex/skills/route-vault-context/scripts/vault_router.py \
  signals \
  --vault /Users/allxndrskllv/Documents/mian \
  --map python
```

Available commands are `signals`, `route`, `search`, `section`, `links`, and
`audit`. Run `vault_router.py --help` or a command followed by `--help` for the
complete arguments.

## Verify before copying

Run the bundled test suite from the vault root:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover \
  -s skills/route-vault-context/scripts \
  -p 'test_*.py'
```

Keep generated files such as `__pycache__/` out of both the source and installed
skill directories.
