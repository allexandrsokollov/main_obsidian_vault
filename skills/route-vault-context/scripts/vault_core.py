from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path, PurePosixPath

MAP_FILES = {
    "codex": "00 Maps/Codex Instruction Map.md",
    "python": "00 Maps/Python Guidelines Context Map.md",
}
DEFAULT_EXCLUDED_DIRECTORIES = frozenset({".codex", ".git", ".obsidian", "skills"})
KNOWN_FRONTMATTER_FIELDS = frozenset(
    {
        "framework",
        "retrieved",
        "scope",
        "source_repository",
        "source_revision",
        "status",
        "tags",
        "type",
        "verified",
    }
)
HEADING_RE = re.compile(r"^(#{1,6})[ \t]+(.+?)[ \t]*#*[ \t]*$")
FENCE_RE = re.compile(r"^[ \t]*(`{3,}|~{3,})")
WIKILINK_RE = re.compile(r"!?\[\[([^\[\]]+)\]\]")
WORD_RE = re.compile(r"\w+", re.UNICODE)


class VaultError(Exception):
    """Raised when a deterministic vault operation cannot be completed."""


@dataclass(frozen=True, slots=True)
class NoteMetadata:
    fields: tuple[tuple[str, tuple[str, ...]], ...]

    def get(self, field: str) -> tuple[str, ...]:
        normalized_field = field.casefold()
        for name, values in self.fields:
            if name == normalized_field:
                return values
        return ()

    @property
    def names(self) -> tuple[str, ...]:
        return tuple(name for name, _ in self.fields)


@dataclass(frozen=True, slots=True)
class Heading:
    title: str
    level: int
    line: int


@dataclass(frozen=True, slots=True)
class WikiLink:
    raw: str
    target: str
    heading: str | None
    alias: str | None
    line: int


@dataclass(frozen=True, slots=True)
class Note:
    relative_path: str
    text: str
    lines: tuple[str, ...]
    title: str
    metadata: NoteMetadata
    frontmatter_end_line: int
    frontmatter_errors: tuple[str, ...]
    headings: tuple[Heading, ...]
    links: tuple[WikiLink, ...]


@dataclass(frozen=True, slots=True)
class SectionResult:
    path: str
    heading: str
    start_line: int
    end_line: int
    content: str


@dataclass(frozen=True, slots=True)
class LinkResolution:
    raw: str
    line: int
    status: str
    path: str | None
    heading: str | None
    candidates: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class LinksResult:
    path: str
    links: tuple[LinkResolution, ...]


@dataclass(frozen=True, slots=True)
class RouteSource:
    path: str
    heading: str | None
    start_line: int
    end_line: int
    reason: str


@dataclass(frozen=True, slots=True)
class RouteResult:
    map: str
    signals: tuple[str, ...]
    sources: tuple[RouteSource, ...]
    warnings: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class SignalDescription:
    signal: str
    load: str
    outcome: str


@dataclass(frozen=True, slots=True)
class SignalsResult:
    map: str
    signals: tuple[SignalDescription, ...]


@dataclass(frozen=True, slots=True)
class SearchFilters:
    note_types: tuple[str, ...] = ()
    scopes: tuple[str, ...] = ()
    statuses: tuple[str, ...] = ()
    tags: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class SearchMatch:
    path: str
    title: str
    score: int
    start_line: int
    end_line: int
    snippet: str
    matched_metadata: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class SearchResult:
    query: str
    filters: SearchFilters
    matches: tuple[SearchMatch, ...]


@dataclass(frozen=True, slots=True)
class AuditIssue:
    path: str
    line: int | None
    value: str
    message: str
    candidates: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class StaleNote:
    path: str
    field: str
    value: str
    age_days: int


@dataclass(frozen=True, slots=True)
class AuditResult:
    broken_links: tuple[AuditIssue, ...]
    ambiguous_links: tuple[AuditIssue, ...]
    missing_headings: tuple[AuditIssue, ...]
    invalid_dates: tuple[AuditIssue, ...]
    stale_notes: tuple[StaleNote, ...]
    unverified_notes: tuple[str, ...]
    unknown_frontmatter_fields: tuple[AuditIssue, ...]
    frontmatter_errors: tuple[AuditIssue, ...]


@dataclass(slots=True)
class VaultIndex:
    root: Path
    notes: tuple[Note, ...]
    by_path: dict[str, tuple[Note, ...]]
    by_stem: dict[str, tuple[Note, ...]]
    by_title: dict[str, tuple[Note, ...]]

    @classmethod
    def build(
        cls,
        root: Path,
        excluded_directories: frozenset[str] = DEFAULT_EXCLUDED_DIRECTORIES,
    ) -> VaultIndex:
        resolved_root = root.expanduser().resolve()
        if not resolved_root.is_dir():
            raise VaultError(f"Vault root is not a directory: {resolved_root}")

        notes: list[Note] = []
        for markdown_path in sorted(resolved_root.rglob("*.md")):
            relative_path = markdown_path.relative_to(resolved_root)
            if any(part in excluded_directories for part in relative_path.parts[:-1]):
                continue
            resolved_path = markdown_path.resolve()
            if not resolved_path.is_relative_to(resolved_root):
                continue
            try:
                text = resolved_path.read_text(encoding="utf-8")
            except UnicodeError as error:
                raise VaultError(f"Cannot decode {relative_path} as UTF-8") from error
            notes.append(parse_note(relative_path.as_posix(), text))

        by_path: dict[str, list[Note]] = {}
        by_stem: dict[str, list[Note]] = {}
        by_title: dict[str, list[Note]] = {}
        for note in notes:
            path_without_suffix = str(PurePosixPath(note.relative_path).with_suffix(""))
            for key in {note.relative_path.casefold(), path_without_suffix.casefold()}:
                by_path.setdefault(key, []).append(note)
            by_stem.setdefault(Path(note.relative_path).stem.casefold(), []).append(
                note
            )
            by_title.setdefault(note.title.casefold(), []).append(note)

        return cls(
            root=resolved_root,
            notes=tuple(notes),
            by_path={key: tuple(value) for key, value in by_path.items()},
            by_stem={key: tuple(value) for key, value in by_stem.items()},
            by_title={key: tuple(value) for key, value in by_title.items()},
        )

    def find_note(self, identifier: str, current_note: Note | None = None) -> Note:
        candidates = self.note_candidates(identifier, current_note)
        if not candidates:
            raise VaultError(f"Note not found: {identifier}")
        if len(candidates) > 1:
            paths = ", ".join(note.relative_path for note in candidates)
            raise VaultError(f"Ambiguous note {identifier!r}: {paths}")
        return candidates[0]

    def note_candidates(
        self,
        identifier: str,
        current_note: Note | None = None,
    ) -> tuple[Note, ...]:
        normalized_identifier = _normalize_note_identifier(identifier)
        if not normalized_identifier and current_note is not None:
            return (current_note,)
        if not normalized_identifier:
            return ()

        direct_keys: list[str] = []
        if current_note is not None:
            current_directory = PurePosixPath(current_note.relative_path).parent
            local_path = (current_directory / normalized_identifier).as_posix()
            direct_keys.extend([local_path.casefold(), f"{local_path}.md".casefold()])
        direct_keys.extend(
            [normalized_identifier.casefold(), f"{normalized_identifier}.md".casefold()]
        )
        for key in direct_keys:
            direct = self.by_path.get(key, ())
            if direct:
                return direct

        if "/" not in normalized_identifier:
            stem_matches = self.by_stem.get(normalized_identifier.casefold(), ())
            if stem_matches:
                return stem_matches
            title_matches = self.by_title.get(normalized_identifier.casefold(), ())
            if title_matches:
                return title_matches
        return ()


def parse_note(relative_path: str, text: str) -> Note:
    lines = tuple(text.splitlines())
    metadata, frontmatter_end_line, frontmatter_errors = _parse_frontmatter(lines)
    headings = _parse_headings(lines, frontmatter_end_line)
    links = _parse_wikilinks(lines, frontmatter_end_line)
    title = next(
        (heading.title for heading in headings if heading.level == 1),
        Path(relative_path).stem,
    )
    return Note(
        relative_path=relative_path,
        text=text,
        lines=lines,
        title=title,
        metadata=metadata,
        frontmatter_end_line=frontmatter_end_line,
        frontmatter_errors=frontmatter_errors,
        headings=headings,
        links=links,
    )


def get_section(note: Note, heading_name: str) -> SectionResult:
    normalized_heading = _normalize_heading(heading_name)
    matches = [
        heading
        for heading in note.headings
        if _normalize_heading(heading.title) == normalized_heading
    ]
    if not matches:
        available = ", ".join(heading.title for heading in note.headings)
        raise VaultError(
            f"Heading {heading_name!r} not found in {note.relative_path}. "
            f"Available headings: {available or '(none)'}"
        )
    if len(matches) > 1:
        lines = ", ".join(str(heading.line) for heading in matches)
        raise VaultError(
            f"Ambiguous heading {heading_name!r} in {note.relative_path}; lines: {lines}"
        )

    selected = matches[0]
    end_line = len(note.lines)
    for candidate in note.headings:
        if candidate.line > selected.line and candidate.level <= selected.level:
            end_line = candidate.line - 1
            break
    while end_line > selected.line and not note.lines[end_line - 1].strip():
        end_line -= 1
    content = "\n".join(note.lines[selected.line - 1 : end_line])
    return SectionResult(
        path=note.relative_path,
        heading=selected.title,
        start_line=selected.line,
        end_line=end_line,
        content=content,
    )


def resolve_link(
    index: VaultIndex, source_note: Note, link: WikiLink
) -> LinkResolution:
    candidates = index.note_candidates(link.target, source_note)
    if not candidates:
        return LinkResolution(
            raw=link.raw,
            line=link.line,
            status="broken",
            path=None,
            heading=link.heading,
            candidates=(),
        )
    if len(candidates) > 1:
        return LinkResolution(
            raw=link.raw,
            line=link.line,
            status="ambiguous",
            path=None,
            heading=link.heading,
            candidates=tuple(note.relative_path for note in candidates),
        )

    target_note = candidates[0]
    if link.heading is not None:
        heading_matches = [
            heading
            for heading in target_note.headings
            if _normalize_heading(heading.title) == _normalize_heading(link.heading)
        ]
        if len(heading_matches) != 1:
            return LinkResolution(
                raw=link.raw,
                line=link.line,
                status="missing_heading"
                if not heading_matches
                else "ambiguous_heading",
                path=target_note.relative_path,
                heading=link.heading,
                candidates=tuple(str(heading.line) for heading in heading_matches),
            )

    return LinkResolution(
        raw=link.raw,
        line=link.line,
        status="resolved",
        path=target_note.relative_path,
        heading=link.heading,
        candidates=(),
    )


def resolve_note_links(index: VaultIndex, note_identifier: str) -> LinksResult:
    note = index.find_note(note_identifier)
    return LinksResult(
        path=note.relative_path,
        links=tuple(resolve_link(index, note, link) for link in note.links),
    )


def list_signals(index: VaultIndex, map_name: str) -> SignalsResult:
    map_note = _get_map_note(index, map_name)
    rows = _routing_rows(map_note)
    descriptions = tuple(
        SignalDescription(
            signal=row["task signal"],
            load=row.get("load", ""),
            outcome=row.get("key outcome", row.get("stop when", "")),
        )
        for row in rows
    )
    return SignalsResult(map=map_note.relative_path, signals=descriptions)


def route_context(
    index: VaultIndex, map_name: str, signals: tuple[str, ...]
) -> RouteResult:
    if not signals:
        raise VaultError("At least one --signal is required")
    map_note = _get_map_note(index, map_name)
    rows = _routing_rows(map_note)
    rows_by_signal: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        rows_by_signal.setdefault(row["task signal"].casefold(), []).append(row)

    selected_rows: list[tuple[str, dict[str, str]]] = []
    for signal in signals:
        matches = rows_by_signal.get(signal.casefold(), [])
        if not matches:
            available = ", ".join(row["task signal"] for row in rows)
            raise VaultError(
                f"Unknown signal {signal!r}. Available signals: {available}"
            )
        if len(matches) > 1:
            raise VaultError(
                f"Signal is duplicated in {map_note.relative_path}: {signal}"
            )
        selected_rows.append((matches[0]["task signal"], matches[0]))

    sources: list[RouteSource] = [
        RouteSource(
            path=map_note.relative_path,
            heading=None,
            start_line=1,
            end_line=len(map_note.lines),
            reason="Context map",
        )
    ]
    warnings: list[str] = []

    always_heading = _find_heading(map_note, "Always load")
    if always_heading is not None:
        always_section = get_section(map_note, always_heading.title)
        for link in _parse_wikilinks(tuple(always_section.content.splitlines()), 0):
            _append_route_source(
                sources,
                warnings,
                index,
                map_note,
                link,
                reason="Always load",
            )

    for signal, row in selected_rows:
        load_value = row.get("load", "")
        links = _parse_inline_wikilinks(load_value)
        if not links:
            warnings.append(f"Signal {signal!r} has no wiki-link in its Load cell")
        for link in links:
            _append_route_source(
                sources,
                warnings,
                index,
                map_note,
                link,
                reason=signal,
            )

    return RouteResult(
        map=map_note.relative_path,
        signals=tuple(signal for signal, _ in selected_rows),
        sources=tuple(_deduplicate_sources(sources)),
        warnings=tuple(warnings),
    )


def search_vault(
    index: VaultIndex,
    query: str,
    filters: SearchFilters,
    max_results: int,
    context_lines: int,
) -> SearchResult:
    normalized_query = query.strip().casefold()
    if not normalized_query:
        raise VaultError("Search query must not be empty")
    if max_results < 1:
        raise VaultError("--max-results must be at least 1")
    if context_lines < 0:
        raise VaultError("--context-lines must not be negative")

    query_terms = tuple(dict.fromkeys(WORD_RE.findall(normalized_query)))
    matches: list[SearchMatch] = []
    for note in index.notes:
        if not _matches_filters(note, filters):
            continue
        score, matched_metadata = _score_note(note, normalized_query, query_terms)
        if score <= 0:
            continue
        start_line, end_line, snippet = _search_snippet(
            note,
            normalized_query,
            query_terms,
            context_lines,
        )
        matches.append(
            SearchMatch(
                path=note.relative_path,
                title=note.title,
                score=score,
                start_line=start_line,
                end_line=end_line,
                snippet=snippet,
                matched_metadata=matched_metadata,
            )
        )

    matches.sort(key=lambda match: (-match.score, match.path.casefold()))
    return SearchResult(
        query=query, filters=filters, matches=tuple(matches[:max_results])
    )


def audit_vault(index: VaultIndex, as_of: date, stale_after_days: int) -> AuditResult:
    if stale_after_days < 0:
        raise VaultError("--stale-after-days must not be negative")

    broken_links: list[AuditIssue] = []
    ambiguous_links: list[AuditIssue] = []
    missing_headings: list[AuditIssue] = []
    invalid_dates: list[AuditIssue] = []
    stale_notes: list[StaleNote] = []
    unverified_notes: list[str] = []
    unknown_fields: list[AuditIssue] = []
    frontmatter_errors: list[AuditIssue] = []

    for note in index.notes:
        for error in note.frontmatter_errors:
            frontmatter_errors.append(
                AuditIssue(note.relative_path, None, "frontmatter", error)
            )
        for field_name in note.metadata.names:
            if field_name not in KNOWN_FRONTMATTER_FIELDS:
                unknown_fields.append(
                    AuditIssue(
                        note.relative_path,
                        None,
                        field_name,
                        "Unknown frontmatter field",
                    )
                )

        for link in note.links:
            resolution = resolve_link(index, note, link)
            issue = AuditIssue(
                path=note.relative_path,
                line=link.line,
                value=link.raw,
                message=resolution.status.replace("_", " "),
                candidates=resolution.candidates,
            )
            if resolution.status == "broken":
                broken_links.append(issue)
            elif resolution.status in {"ambiguous", "ambiguous_heading"}:
                ambiguous_links.append(issue)
            elif resolution.status == "missing_heading":
                missing_headings.append(issue)

        verification_fields = (
            ("verified", note.metadata.get("verified")),
            ("retrieved", note.metadata.get("retrieved")),
        )
        has_verification_date = False
        for field_name, values in verification_fields:
            for value in values:
                has_verification_date = True
                try:
                    parsed_date = date.fromisoformat(value)
                except ValueError:
                    invalid_dates.append(
                        AuditIssue(
                            note.relative_path,
                            None,
                            value,
                            f"Invalid {field_name} date; expected YYYY-MM-DD",
                        )
                    )
                    continue
                age_days = (as_of - parsed_date).days
                if age_days > stale_after_days:
                    stale_notes.append(
                        StaleNote(note.relative_path, field_name, value, age_days)
                    )

        is_active = "active" in {
            value.casefold() for value in note.metadata.get("status")
        }
        has_revision = bool(note.metadata.get("source_revision"))
        if is_active and not has_verification_date and not has_revision:
            unverified_notes.append(note.relative_path)

    return AuditResult(
        broken_links=tuple(sorted(broken_links, key=_issue_sort_key)),
        ambiguous_links=tuple(sorted(ambiguous_links, key=_issue_sort_key)),
        missing_headings=tuple(sorted(missing_headings, key=_issue_sort_key)),
        invalid_dates=tuple(sorted(invalid_dates, key=_issue_sort_key)),
        stale_notes=tuple(
            sorted(stale_notes, key=lambda item: (item.path.casefold(), item.field))
        ),
        unverified_notes=tuple(sorted(unverified_notes, key=str.casefold)),
        unknown_frontmatter_fields=tuple(sorted(unknown_fields, key=_issue_sort_key)),
        frontmatter_errors=tuple(sorted(frontmatter_errors, key=_issue_sort_key)),
    )


def _parse_frontmatter(
    lines: tuple[str, ...],
) -> tuple[NoteMetadata, int, tuple[str, ...]]:
    if not lines or lines[0].strip() != "---":
        return NoteMetadata(fields=()), 0, ()

    closing_index = next(
        (
            index
            for index, line in enumerate(lines[1:], start=1)
            if line.strip() == "---"
        ),
        None,
    )
    if closing_index is None:
        return NoteMetadata(fields=()), 0, ("Unclosed YAML frontmatter",)

    values: dict[str, list[str]] = {}
    errors: list[str] = []
    current_key: str | None = None
    for line_number, line in enumerate(lines[1:closing_index], start=2):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if line[:1].isspace() and stripped.startswith("-"):
            if current_key is None:
                errors.append(f"Line {line_number}: list item has no field")
                continue
            item = _clean_scalar(stripped[1:].strip())
            if item:
                values[current_key].append(item)
            continue
        if line[:1].isspace():
            errors.append(f"Line {line_number}: unsupported nested frontmatter")
            continue
        if ":" not in line:
            errors.append(f"Line {line_number}: expected 'field: value'")
            current_key = None
            continue
        raw_key, raw_value = line.split(":", 1)
        current_key = raw_key.strip().casefold()
        if not current_key:
            errors.append(f"Line {line_number}: empty frontmatter field")
            current_key = None
            continue
        if current_key in values:
            errors.append(f"Line {line_number}: duplicate field {current_key!r}")
        values.setdefault(current_key, [])
        value = raw_value.strip()
        if value.startswith("[") and value.endswith("]"):
            inline_items = value[1:-1].split(",")
            values[current_key].extend(
                cleaned
                for item in inline_items
                if (cleaned := _clean_scalar(item.strip()))
            )
        elif value:
            values[current_key].append(_clean_scalar(value))

    metadata = NoteMetadata(
        fields=tuple(
            (name, tuple(field_values)) for name, field_values in values.items()
        )
    )
    return metadata, closing_index + 1, tuple(errors)


def _clean_scalar(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    return value


def _visible_lines(
    lines: tuple[str, ...],
    frontmatter_end_line: int,
) -> tuple[tuple[int, str], ...]:
    visible: list[tuple[int, str]] = []
    fence_character: str | None = None
    fence_length = 0
    for line_number, line in enumerate(lines, start=1):
        if line_number <= frontmatter_end_line:
            continue
        fence_match = FENCE_RE.match(line)
        if fence_match:
            marker = fence_match.group(1)
            if fence_character is None:
                fence_character = marker[0]
                fence_length = len(marker)
            elif marker[0] == fence_character and len(marker) >= fence_length:
                fence_character = None
                fence_length = 0
            continue
        if fence_character is None:
            visible.append((line_number, line))
    return tuple(visible)


def _parse_headings(
    lines: tuple[str, ...], frontmatter_end_line: int
) -> tuple[Heading, ...]:
    headings: list[Heading] = []
    for line_number, line in _visible_lines(lines, frontmatter_end_line):
        match = HEADING_RE.match(line)
        if match:
            headings.append(
                Heading(
                    title=match.group(2).strip(),
                    level=len(match.group(1)),
                    line=line_number,
                )
            )
    return tuple(headings)


def _parse_wikilinks(
    lines: tuple[str, ...],
    frontmatter_end_line: int,
) -> tuple[WikiLink, ...]:
    links: list[WikiLink] = []
    for line_number, line in _visible_lines(lines, frontmatter_end_line):
        for match in WIKILINK_RE.finditer(line):
            links.append(_wikilink_from_raw(match.group(1), line_number))
    return tuple(links)


def _parse_inline_wikilinks(value: str) -> tuple[WikiLink, ...]:
    return tuple(
        _wikilink_from_raw(match.group(1), 0) for match in WIKILINK_RE.finditer(value)
    )


def _wikilink_from_raw(raw: str, line: int) -> WikiLink:
    target_part, separator, alias_part = raw.partition("|")
    target, heading_separator, heading = target_part.partition("#")
    return WikiLink(
        raw=raw,
        target=target.strip(),
        heading=heading.strip() if heading_separator and heading.strip() else None,
        alias=alias_part.strip() if separator and alias_part.strip() else None,
        line=line,
    )


def _normalize_note_identifier(identifier: str) -> str:
    normalized = identifier.strip().replace("\\", "/")
    if normalized.casefold().endswith(".md"):
        normalized = normalized[:-3]
    while normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized.strip("/")


def _normalize_heading(heading: str) -> str:
    return " ".join(heading.strip().casefold().split())


def _find_heading(note: Note, heading_name: str) -> Heading | None:
    normalized = _normalize_heading(heading_name)
    matches = [
        heading
        for heading in note.headings
        if _normalize_heading(heading.title) == normalized
    ]
    if len(matches) > 1:
        raise VaultError(
            f"Heading {heading_name!r} is duplicated in {note.relative_path}"
        )
    return matches[0] if matches else None


def _get_map_note(index: VaultIndex, map_name: str) -> Note:
    map_path = MAP_FILES.get(map_name.casefold())
    if map_path is None:
        available = ", ".join(sorted(MAP_FILES))
        raise VaultError(f"Unknown map {map_name!r}. Available maps: {available}")
    return index.find_note(map_path)


def _routing_rows(map_note: Note) -> tuple[dict[str, str], ...]:
    visible_lines = _visible_lines(map_note.lines, map_note.frontmatter_end_line)
    visible_by_number = {line_number: line for line_number, line in visible_lines}
    line_numbers = sorted(visible_by_number)
    for position, line_number in enumerate(line_numbers[:-1]):
        header_line = visible_by_number[line_number].strip()
        if not header_line.startswith("|"):
            continue
        next_number = line_numbers[position + 1]
        if next_number != line_number + 1:
            continue
        separator_line = visible_by_number[next_number].strip()
        headers = _table_cells(header_line)
        if "task signal" not in {header.casefold() for header in headers}:
            continue
        if not _is_table_separator(separator_line):
            continue

        normalized_headers = tuple(header.casefold() for header in headers)
        rows: list[dict[str, str]] = []
        for row_number in line_numbers[position + 2 :]:
            if row_number != next_number + 1 + len(rows):
                break
            row_line = visible_by_number[row_number].strip()
            if not row_line.startswith("|"):
                break
            cells = _table_cells(row_line)
            if len(cells) != len(normalized_headers):
                raise VaultError(
                    f"Malformed routing row at {map_note.relative_path}:{row_number}"
                )
            rows.append(dict(zip(normalized_headers, cells, strict=True)))
        if rows:
            return tuple(rows)
    raise VaultError(f"No routing table found in {map_note.relative_path}")


def _table_cells(line: str) -> tuple[str, ...]:
    return tuple(cell.strip() for cell in line.strip().strip("|").split("|"))


def _is_table_separator(line: str) -> bool:
    cells = _table_cells(line)
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells)


def _append_route_source(
    sources: list[RouteSource],
    warnings: list[str],
    index: VaultIndex,
    map_note: Note,
    link: WikiLink,
    reason: str,
) -> None:
    resolution = resolve_link(index, map_note, link)
    if resolution.status != "resolved" or resolution.path is None:
        details = ", ".join(resolution.candidates)
        raise VaultError(
            f"Cannot route {link.raw!r} from {map_note.relative_path}: "
            f"{resolution.status}{f' ({details})' if details else ''}"
        )
    target_note = index.find_note(resolution.path)
    if resolution.heading is None:
        sources.append(
            RouteSource(
                path=target_note.relative_path,
                heading=None,
                start_line=1,
                end_line=len(target_note.lines),
                reason=reason,
            )
        )
        return
    section = get_section(target_note, resolution.heading)
    sources.append(
        RouteSource(
            path=section.path,
            heading=section.heading,
            start_line=section.start_line,
            end_line=section.end_line,
            reason=reason,
        )
    )
    if section.start_line == section.end_line:
        warnings.append(f"Selected section is empty: {section.path}#{section.heading}")


def _deduplicate_sources(sources: list[RouteSource]) -> list[RouteSource]:
    deduplicated: list[RouteSource] = []
    seen: set[tuple[str, str | None]] = set()
    for source in sources:
        key = (
            source.path.casefold(),
            source.heading.casefold() if source.heading else None,
        )
        if key not in seen:
            seen.add(key)
            deduplicated.append(source)
    return deduplicated


def _matches_filters(note: Note, filters: SearchFilters) -> bool:
    return (
        _contains_all(note.metadata.get("type"), filters.note_types)
        and _contains_all(note.metadata.get("scope"), filters.scopes)
        and _contains_all(note.metadata.get("status"), filters.statuses)
        and _contains_all(note.metadata.get("tags"), filters.tags)
    )


def _contains_all(actual: tuple[str, ...], required: tuple[str, ...]) -> bool:
    normalized_actual = {value.casefold() for value in actual}
    return all(value.casefold() in normalized_actual for value in required)


def _score_note(
    note: Note,
    normalized_query: str,
    query_terms: tuple[str, ...],
) -> tuple[int, tuple[str, ...]]:
    title = note.title.casefold()
    headings = tuple(heading.title.casefold() for heading in note.headings)
    body = "\n".join(note.lines[note.frontmatter_end_line :]).casefold()
    metadata_values = {
        f"{field}:{value}".casefold()
        for field, values in note.metadata.fields
        for value in values
    }
    plain_metadata_values = {
        value.casefold() for _, values in note.metadata.fields for value in values
    }

    score = 0
    if normalized_query == title:
        score += 1000
    if normalized_query in headings:
        score += 700
    if normalized_query in plain_metadata_values or normalized_query in metadata_values:
        score += 500
    if normalized_query in body:
        score += 200

    matched_metadata: set[str] = set()
    for term in query_terms:
        if term in title:
            score += 80
        score += 30 * sum(term in heading for heading in headings)
        if any(term in value for value in plain_metadata_values):
            score += 50
            matched_metadata.add(term)
        score += min(body.count(term), 10)
    return score, tuple(sorted(matched_metadata))


def _search_snippet(
    note: Note,
    normalized_query: str,
    query_terms: tuple[str, ...],
    context_lines: int,
) -> tuple[int, int, str]:
    content_start_line = max(1, note.frontmatter_end_line + 1)
    match_line = next(
        (
            line_number
            for line_number, line in enumerate(note.lines, start=1)
            if line_number >= content_start_line and normalized_query in line.casefold()
        ),
        None,
    )
    if match_line is None:
        match_line = next(
            (
                line_number
                for line_number, line in enumerate(note.lines, start=1)
                if line_number >= content_start_line
                and any(term in line.casefold() for term in query_terms)
            ),
            note.headings[0].line if note.headings else 1,
        )
    start_line = max(content_start_line, match_line - context_lines)
    end_line = min(len(note.lines), match_line + context_lines)
    snippet = "\n".join(note.lines[start_line - 1 : end_line])
    return start_line, end_line, snippet


def _issue_sort_key(issue: AuditIssue) -> tuple[str, int, str]:
    return (issue.path.casefold(), issue.line or 0, issue.value.casefold())
