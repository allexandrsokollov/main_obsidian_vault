from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from dataclasses import asdict
from datetime import date, datetime, timezone
from pathlib import Path

from vault_core import (
    AuditResult,
    LinksResult,
    RouteResult,
    SearchFilters,
    SearchResult,
    SectionResult,
    SignalsResult,
    VaultError,
    VaultIndex,
    audit_vault,
    get_section,
    list_signals,
    resolve_note_links,
    route_context,
    search_vault,
)

CommandResult = (
    AuditResult
    | LinksResult
    | RouteResult
    | SearchResult
    | SectionResult
    | SignalsResult
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Deterministically route and retrieve Markdown vault context."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    signals_parser = subparsers.add_parser(
        "signals", help="List exact routing signals from a context map."
    )
    _add_vault_argument(signals_parser)
    signals_parser.add_argument("--map", required=True, choices=("python", "codex"))

    route_parser = subparsers.add_parser(
        "route", help="Resolve exact task signals into ordered vault sources."
    )
    _add_vault_argument(route_parser)
    route_parser.add_argument("--map", required=True, choices=("python", "codex"))
    route_parser.add_argument(
        "--signal",
        action="append",
        required=True,
        help="Exact Task signal cell from the selected context map; repeat as needed.",
    )

    search_parser = subparsers.add_parser(
        "search", help="Search notes lexically with optional frontmatter filters."
    )
    _add_vault_argument(search_parser)
    search_parser.add_argument("--query", required=True)
    search_parser.add_argument("--type", dest="note_types", action="append", default=[])
    search_parser.add_argument("--scope", dest="scopes", action="append", default=[])
    search_parser.add_argument("--status", dest="statuses", action="append", default=[])
    search_parser.add_argument("--tag", dest="tags", action="append", default=[])
    search_parser.add_argument("--max-results", type=int, default=5)
    search_parser.add_argument("--context-lines", type=int, default=2)

    section_parser = subparsers.add_parser(
        "section", help="Retrieve one exact Markdown section with line numbers."
    )
    _add_vault_argument(section_parser)
    section_parser.add_argument("--note", required=True)
    section_parser.add_argument("--heading", required=True)

    links_parser = subparsers.add_parser(
        "links", help="Resolve every wiki-link in one note without following it."
    )
    _add_vault_argument(links_parser)
    links_parser.add_argument("--note", required=True)

    audit_parser = subparsers.add_parser(
        "audit", help="Report broken links and verification metadata problems."
    )
    _add_vault_argument(audit_parser)
    audit_parser.add_argument("--stale-after-days", type=int, default=180)
    audit_parser.add_argument(
        "--as-of",
        type=_iso_date,
        default=datetime.now(tz=timezone.utc).astimezone().date(),
        help="Audit date in YYYY-MM-DD format; defaults to today.",
    )

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    arguments = parser.parse_args(argv)
    try:
        index = VaultIndex.build(Path(arguments.vault))
        result = _execute(arguments, index)
    except VaultError as error:
        print(json.dumps({"error": str(error)}, ensure_ascii=False), file=sys.stderr)
        return 2
    print(json.dumps(asdict(result), ensure_ascii=False, indent=2))
    return 0


def _execute(arguments: argparse.Namespace, index: VaultIndex) -> CommandResult:
    if arguments.command == "signals":
        return list_signals(index, arguments.map)
    if arguments.command == "route":
        return route_context(index, arguments.map, tuple(arguments.signal))
    if arguments.command == "search":
        filters = SearchFilters(
            note_types=tuple(arguments.note_types),
            scopes=tuple(arguments.scopes),
            statuses=tuple(arguments.statuses),
            tags=tuple(arguments.tags),
        )
        return search_vault(
            index,
            arguments.query,
            filters,
            arguments.max_results,
            arguments.context_lines,
        )
    if arguments.command == "section":
        note = index.find_note(arguments.note)
        return get_section(note, arguments.heading)
    if arguments.command == "links":
        return resolve_note_links(index, arguments.note)
    if arguments.command == "audit":
        return audit_vault(index, arguments.as_of, arguments.stale_after_days)
    raise VaultError(f"Unsupported command: {arguments.command}")


def _add_vault_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--vault", required=True, help="Path to the Markdown vault root."
    )


def _iso_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("expected YYYY-MM-DD") from error


if __name__ == "__main__":
    raise SystemExit(main())
