from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from datetime import date
from pathlib import Path

from vault_core import (
    SearchFilters,
    VaultError,
    VaultIndex,
    audit_vault,
    get_section,
    resolve_note_links,
    route_context,
    search_vault,
)
from vault_router import main


class VaultRouterTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.vault = Path(self.temporary_directory.name)

    def write_note(self, relative_path: str, content: str) -> None:
        path = self.vault / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def build_index(self) -> VaultIndex:
        return VaultIndex.build(self.vault)

    def test_route_uses_map_order_always_load_and_exact_signal(self) -> None:
        self.write_note(
            "00 Maps/Python Guidelines Context Map.md",
            """---
type: map-of-content
status: active
scope: python
---
# Python Guidelines Context Map

## Always load

1. [[Workflow and Quality Gates]]

## Routing table

| Task signal | Load | Key outcome |
|---|---|---|
| Bug fix | [[Testing Strategy]] + [[Implementation Playbook]] | Verified fix |
""",
        )
        self.write_note(
            "10 Core/Workflow and Quality Gates.md", "# Workflow and Quality Gates\n"
        )
        self.write_note("10 Core/Testing Strategy.md", "# Testing Strategy\n")
        self.write_note(
            "30 Playbooks/Implementation Playbook.md", "# Implementation Playbook\n"
        )

        result = route_context(self.build_index(), "python", ("Bug fix",))

        self.assertEqual(
            [source.path for source in result.sources],
            [
                "00 Maps/Python Guidelines Context Map.md",
                "10 Core/Workflow and Quality Gates.md",
                "10 Core/Testing Strategy.md",
                "30 Playbooks/Implementation Playbook.md",
            ],
        )
        self.assertEqual(result.sources[1].reason, "Always load")
        self.assertEqual(result.sources[2].reason, "Bug fix")

    def test_route_rejects_unknown_signal_and_lists_available_values(self) -> None:
        self.write_note(
            "00 Maps/Codex Instruction Map.md",
            """# Codex Instruction Map

## Task routing

| Task signal | Load | Stop when |
|---|---|---|
| Planning | [[Planning Guide]] | Plan settled |
""",
        )
        self.write_note("Planning Guide.md", "# Planning Guide\n")

        with self.assertRaisesRegex(VaultError, "Available signals: Planning"):
            route_context(self.build_index(), "codex", ("Missing",))

    def test_route_resolves_heading_fragments_with_line_ranges(self) -> None:
        self.write_note(
            "00 Maps/Codex Instruction Map.md",
            """# Codex Instruction Map

## Task routing

| Task signal | Load | Stop when |
|---|---|---|
| Planning | [[Strategy#Task and plan]] | Plan settled |
""",
        )
        self.write_note(
            "Strategy.md",
            """# Strategy

## Task and plan

Relevant instructions.

## Other

Not selected.
""",
        )

        result = route_context(self.build_index(), "codex", ("Planning",))

        selected = result.sources[1]
        self.assertEqual(selected.path, "Strategy.md")
        self.assertEqual(selected.heading, "Task and plan")
        self.assertEqual((selected.start_line, selected.end_line), (3, 5))

    def test_search_filters_frontmatter_and_returns_a_bounded_snippet(self) -> None:
        self.write_note(
            "Integration.md",
            """---
type: guideline
status: active
scope: python
tags: [integration, compatibility]
---
# Integration

Preserve transport compatibility at service boundaries.
""",
        )
        self.write_note(
            "Other.md",
            """---
type: guideline
status: draft
scope: codex
tags:
  - integration
---
# Other

Transport compatibility is mentioned here too.
""",
        )

        result = search_vault(
            self.build_index(),
            "transport compatibility",
            SearchFilters(
                scopes=("python",), statuses=("active",), tags=("integration",)
            ),
            max_results=5,
            context_lines=0,
        )

        self.assertEqual(len(result.matches), 1)
        self.assertEqual(result.matches[0].path, "Integration.md")
        self.assertEqual(
            result.matches[0].snippet,
            "Preserve transport compatibility at service boundaries.",
        )

    def test_section_ignores_heading_like_text_inside_code_fences(self) -> None:
        self.write_note(
            "Guide.md",
            """# Guide

## Selected

```markdown
## Not a real heading
```

Selected body.

## Next

Other body.
""",
        )

        result = get_section(self.build_index().find_note("Guide"), "Selected")

        self.assertIn("## Not a real heading", result.content)
        self.assertIn("Selected body.", result.content)
        self.assertNotIn("Other body.", result.content)
        self.assertEqual(result.end_line, 9)

    def test_links_report_resolved_broken_and_missing_heading_separately(self) -> None:
        self.write_note(
            "Source.md",
            """# Source

[[Target#Present|valid]]
[[Target#Missing]]
[[Absent]]
""",
        )
        self.write_note("Target.md", "# Target\n\n## Present\n\nText.\n")

        result = resolve_note_links(self.build_index(), "Source")

        self.assertEqual(
            [resolution.status for resolution in result.links],
            ["resolved", "missing_heading", "broken"],
        )

    def test_links_do_not_silently_choose_duplicate_note_names(self) -> None:
        self.write_note("Source.md", "# Source\n\n[[Duplicate]]\n")
        self.write_note("A/Duplicate.md", "# First\n")
        self.write_note("B/Duplicate.md", "# Second\n")

        result = resolve_note_links(self.build_index(), "Source")

        self.assertEqual(result.links[0].status, "ambiguous")
        self.assertEqual(
            result.links[0].candidates, ("A/Duplicate.md", "B/Duplicate.md")
        )

    def test_audit_separates_stale_invalid_and_unverified_notes(self) -> None:
        self.write_note(
            "Stale.md",
            """---
type: guideline
status: active
verified: 2025-01-01
---
# Stale
""",
        )
        self.write_note(
            "Invalid.md",
            """---
type: guideline
status: active
verified: yesterday
---
# Invalid
""",
        )
        self.write_note(
            "Unverified.md",
            """---
type: guideline
status: active
---
# Unverified
""",
        )
        self.write_note(
            "Pinned.md",
            """---
type: guideline
status: active
source_revision: abc123
---
# Pinned
""",
        )

        result = audit_vault(self.build_index(), date(2026, 1, 1), 180)

        self.assertEqual([item.path for item in result.stale_notes], ["Stale.md"])
        self.assertEqual([item.path for item in result.invalid_dates], ["Invalid.md"])
        self.assertEqual(result.unverified_notes, ("Unverified.md",))

    def test_audit_reports_unknown_frontmatter_and_parse_errors(self) -> None:
        self.write_note(
            "Metadata.md",
            """---
type: guideline
custom: value
  invalid nesting
---
# Metadata
""",
        )

        result = audit_vault(self.build_index(), date(2026, 1, 1), 180)

        self.assertEqual(result.unknown_frontmatter_fields[0].value, "custom")
        self.assertIn("unsupported nested", result.frontmatter_errors[0].message)

    def test_skills_directory_is_excluded_from_vault_index(self) -> None:
        self.write_note("Guide.md", "# Guide\n")
        self.write_note("skills/example/SKILL.md", "# Should not be indexed\n")

        index = self.build_index()

        self.assertEqual([note.relative_path for note in index.notes], ["Guide.md"])

    def test_cli_returns_json_from_public_entry_point(self) -> None:
        self.write_note("Guide.md", "# Guide\n\n## Selected\n\nBody.\n")
        stdout = io.StringIO()
        stderr = io.StringIO()

        with redirect_stdout(stdout), redirect_stderr(stderr):
            exit_code = main(
                (
                    "section",
                    "--vault",
                    str(self.vault),
                    "--note",
                    "Guide",
                    "--heading",
                    "Selected",
                )
            )

        self.assertEqual(exit_code, 0)
        self.assertEqual(stderr.getvalue(), "")
        result = json.loads(stdout.getvalue())
        self.assertEqual(result["path"], "Guide.md")
        self.assertEqual(result["content"], "## Selected\n\nBody.")

    def test_cli_returns_structured_error_for_ambiguous_note(self) -> None:
        self.write_note("A/Duplicate.md", "# First\n")
        self.write_note("B/Duplicate.md", "# Second\n")
        stdout = io.StringIO()
        stderr = io.StringIO()

        with redirect_stdout(stdout), redirect_stderr(stderr):
            exit_code = main(
                (
                    "section",
                    "--vault",
                    str(self.vault),
                    "--note",
                    "Duplicate",
                    "--heading",
                    "First",
                )
            )

        self.assertEqual(exit_code, 2)
        self.assertEqual(stdout.getvalue(), "")
        self.assertIn("Ambiguous note", json.loads(stderr.getvalue())["error"])


if __name__ == "__main__":
    unittest.main()
