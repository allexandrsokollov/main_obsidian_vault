---
name: route-vault-context
description: Route Python implementation, review, integration, and compatibility tasks, plus Codex configuration, instruction-design, planning, retrospective, and handoff tasks, into the relevant notes in the local Markdown knowledge vault. Use when Codex needs guidance from /Users/allxndrskllv/Documents/mian without loading the entire vault, or when auditing that vault's links and verification metadata.
---

# Route Vault Context

Use `/Users/allxndrskllv/Documents/mian` as the vault root. Resolve `<skill-dir>`
to the directory containing this `SKILL.md` before running a bundled script.

## Route a task

1. Classify the task as `python` or `codex`.
2. Select every applicable task signal from the corresponding context map. For
   shared-library, cross-service, compatibility, transport, or observability
   work, include the applicable Python integration signal.
3. Run:

   ```bash
   python3 <skill-dir>/scripts/vault_router.py route \
     --vault /Users/allxndrskllv/Documents/mian \
     --map <python-or-codex> \
     --signal "<exact task signal>"
   ```

4. Read only the returned files or sections, in returned order.
5. Do not follow `Related` links unless a selected map row explicitly routes to
   them.
6. Report the paths, headings, line ranges, and routing reasons used.

If the applicable signal is uncertain, inspect the deterministic choices first:

```bash
python3 <skill-dir>/scripts/vault_router.py signals \
  --vault /Users/allxndrskllv/Documents/mian \
  --map <python-or-codex>
```

Do not silently choose between ambiguous signals or note names. Explicit user
requirements and repository-local instructions take precedence over vault
guidance.

## Search or retrieve

Use `search` for bounded lexical retrieval with frontmatter filters:

```bash
python3 <skill-dir>/scripts/vault_router.py search \
  --vault /Users/allxndrskllv/Documents/mian \
  --query "transport compatibility" \
  --scope python --status active --tag integration
```

Use `section` for one exact heading and `links` to inspect a note's resolved
wiki-links. Prefer these bounded operations over reading unrelated whole notes.

## Audit the vault

For vault maintenance or a loading audit, run:

```bash
python3 <skill-dir>/scripts/vault_router.py audit \
  --vault /Users/allxndrskllv/Documents/mian \
  --stale-after-days 180
```

The script is read-only. Treat broken links, ambiguous links, missing headings,
invalid dates, stale dates, and unverified active notes as separate findings.
