# Engineering Guidelines Context

This repository is a task-oriented knowledge vault for Python, Bash, and Codex
work. It contains guidance, quality gates, review and implementation playbooks,
framework notes, and pinned source references. It is context for engineering
work, not an application or shared library.

The vault is designed to be cloned or copied to any location. Shared files do
not depend on a particular username, home directory, or checkout path.

## How the vault is organized

| Location | Purpose |
|---|---|
| [`00 Maps/`](<00 Maps/>) | Routes a task to the smallest relevant set of notes |
| [`10 Core/`](<10 Core/>) | Language rules, testing guidance, and quality gates |
| [`20 Frameworks/`](<20 Frameworks/>) | Framework-specific guidance |
| [`30 Playbooks/`](<30 Playbooks/>) | Implementation, review, planning, and handoff workflows |
| [`90 Sources/`](<90 Sources/>) | Provenance, pinned upstream material, and interpretations |
| [`skills/`](skills/) | Optional Codex skill and deterministic routing tools |
| [`AGENTS.md`](AGENTS.md) | Authoritative instructions for Codex inside this vault |

[`Welcome.md`](Welcome.md) is the vault home page for tools that support
Obsidian-style wiki-links.

## Use the context manually

1. Read [`AGENTS.md`](AGENTS.md) for the authoritative routing and vault
   contract.
2. Open the context map selected by those instructions.
3. Match the current task to a task signal in the map.
4. Read only the files or sections returned by that route, in order. Do not
   traverse `Related` links unless the selected route requires it.
5. Apply the guidance alongside the target repository's closest instructions
   and established conventions.
6. Run the required checks and report checks that could not be run, along with
   the remaining risk.

The main maps are:

- [Python Guidelines Context Map](<00 Maps/Python Guidelines Context Map.md>)
- [Bash Guidelines Context Map](<00 Maps/Bash Guidelines Context Map.md>)
- [Codex Instruction Map](<00 Maps/Codex Instruction Map.md>)

Rules marked **Required** or **Forbidden** are strict unless the user approves
a documented exception. Other guidance should be reconciled with the target
repository's conventions.

## Use the context with Codex

When a Codex task runs inside this vault, Codex discovers the root
[`AGENTS.md`](AGENTS.md) automatically. Start a fresh task after changing
instruction files so the updated instructions are loaded.

For tasks in another repository, give Codex the local vault location without
checking that machine-specific path into shared files. A task prompt can say:

```text
Use the engineering guidelines vault at <absolute-path-to-vault>. Follow its
context map for this task and load only the routed guidance. The target
repository's closest instructions take precedence where they conflict.
```

Replace the placeholder in personal configuration or the task prompt. Each
user's absolute path is intentionally local to their machine.

For repeated use, install the optional `route-vault-context` skill. See the
[skill installation and usage guide](skills/README.md). The skill can list
valid task signals, retrieve routed sections, search bounded context, resolve
wiki-links, and audit the vault without loading every note.

Example explicit invocation:

```text
Use $route-vault-context for this Python integration task. The vault root is
<absolute-path-to-vault>.
```

## Precedence and scope

- Explicit user requirements take precedence over vault guidance.
- The target repository's nearest applicable instructions govern that
  repository.
- This vault's `AGENTS.md` governs maintenance of the vault itself. When the
  vault is consulted from another repository, treat its notes as guidance, not
  as repository-local instructions for the target.
- If the vault or a routed source is unavailable, report that before relying on
  memory.

## Verify the router

The router uses Python 3 and only the standard library. From the vault root,
run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover \
  -s skills/route-vault-context/scripts \
  -p 'test_*.py'
```

Use the Python 3 launcher appropriate for the local platform if it is not named
`python3`. More installation, direct-command, and portability details are in
[`skills/README.md`](skills/README.md).

## Contributing

- Put guidance at its narrowest durable scope.
- Update the appropriate context map when adding a routable note.
- Preserve pinned source provenance and verification metadata.
- Keep machine-specific paths, credentials, generated files, and personal
  configuration out of shared files.
- Preserve unrelated notes and run the narrowest relevant checks before
  handing off changes.
