# AGENT_CONTEXT: Read .agent/README.md for rules
#!/usr/bin/env python3
"""
---
id: SCRIPT-0036
type: script
owner: platform-team
status: active
maturity: 1
dry_run:
  supported: true
  command_hint: --dry-run
test:
  runner: pytest
  command: pytest -q tests/scripts/test_script_0036.py
  evidence: declared
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
---
"""
from __future__ import annotations

"""
Session Summary Archive Script.

Archives session summary entries older than retention period to monthly files.
Only runs when the main file exceeds the line threshold.

Usage:
  python3 scripts/archive_sessions.py                    # Auto-archive if needed
  python3 scripts/archive_sessions.py --dry-run          # Preview changes
  python3 scripts/archive_sessions.py --force            # Archive regardless of size
  python3 scripts/archive_sessions.py --retention-days 14  # Custom retention
"""

import argparse
import os
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Tuple, Optional


# Configuration
DEFAULT_SUMMARY_FILE = "session_summary/agent_session_summary.md"
DEFAULT_ARCHIVE_DIR = "session_summary/archive"
DEFAULT_LINE_THRESHOLD = 1000
DEFAULT_RETENTION_DAYS = 30


def count_lines(file_path: Path) -> int:
    """Count lines in a file."""
    if not file_path.exists():
        return 0
    with open(file_path, "r", encoding="utf-8") as f:
        return sum(1 for _ in f)


def parse_session_entries(content: str) -> List[Tuple[str, datetime, str]]:
    """
    Parse session entries from the summary file.

    Returns list of (entry_id, date, content) tuples.
    Entry pattern: ## YYYY-MM-DDTHH:MMZ or ## Session: YYYY-MM-DD
    """
    entries = []

    # Split by session headers (## followed by date pattern)
    # Matches: ## 2026-01-20T13:34Z or ## Session: 2026-01-20
    pattern = r'^(## (?:\d{4}-\d{2}-\d{2}T\d{2}:\d{2}Z|Session: \d{4}-\d{2}-\d{2}).*?)(?=^## |\Z)'

    matches = re.findall(pattern, content, re.MULTILINE | re.DOTALL)

    for match in matches:
        # Extract date from the header
        date_match = re.search(r'(\d{4}-\d{2}-\d{2})', match)
        if date_match:
            date_str = date_match.group(1)
            try:
                entry_date = datetime.strptime(date_str, "%Y-%m-%d")
                entry_id = f"{date_str}-{hash(match) % 10000:04d}"
                entries.append((entry_id, entry_date, match))
            except ValueError:
                continue

    return entries


def split_frontmatter_and_content(content: str) -> Tuple[str, str]:
    """
    Split file into frontmatter (including instructions) and session entries.

    Frontmatter ends at the first session header (## YYYY-MM-DD or ## Session:).
    """
    # Find the first session entry header
    pattern = r'^## (?:\d{4}-\d{2}-\d{2}T\d{2}:\d{2}Z|Session: \d{4}-\d{2}-\d{2})'
    match = re.search(pattern, content, re.MULTILINE)

    if match:
        frontmatter = content[:match.start()].rstrip() + "\n\n"
        entries_content = content[match.start():]
        return frontmatter, entries_content

    return content, ""


def group_entries_by_month(entries: List[Tuple[str, datetime, str]]) -> dict:
    """Group entries by year-month."""
    grouped = {}
    for entry_id, entry_date, content in entries:
        key = entry_date.strftime("%Y-%m")
        if key not in grouped:
            grouped[key] = []
        grouped[key].append((entry_id, entry_date, content))
    return grouped


def archive_old_entries(
    summary_file: Path,
    archive_dir: Path,
    retention_days: int,
    dry_run: bool = False,
) -> Tuple[int, List[str]]:
    """
    Archive entries older than retention_days to monthly files.

    Returns (archived_count, archive_files_written).
    """
    cutoff_date = datetime.now() - timedelta(days=retention_days)

    # Read current content
    with open(summary_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Split into frontmatter and entries
    frontmatter, entries_content = split_frontmatter_and_content(content)

    # Parse all entries
    entries = parse_session_entries(entries_content)

    if not entries:
        print("No session entries found to archive.")
        return 0, []

    # Separate old and recent entries
    old_entries = [(eid, date, cont) for eid, date, cont in entries if date < cutoff_date]
    recent_entries = [(eid, date, cont) for eid, date, cont in entries if date >= cutoff_date]

    if not old_entries:
        print(f"No entries older than {retention_days} days to archive.")
        return 0, []

    # Group old entries by month
    grouped = group_entries_by_month(old_entries)

    archive_files = []

    if dry_run:
        print(f"[DRY RUN] Would archive {len(old_entries)} entries to {len(grouped)} monthly files:")
        for month, month_entries in sorted(grouped.items()):
            archive_path = archive_dir / f"{month}.md"
            print(f"  - {archive_path}: {len(month_entries)} entries")
        print(f"[DRY RUN] Would keep {len(recent_entries)} recent entries in main file.")
        return len(old_entries), list(grouped.keys())

    # Create archive directory
    archive_dir.mkdir(parents=True, exist_ok=True)

    # Write to monthly archive files
    for month, month_entries in sorted(grouped.items()):
        archive_path = archive_dir / f"{month}.md"

        # Read existing archive content if it exists
        existing_content = ""
        if archive_path.exists():
            with open(archive_path, "r", encoding="utf-8") as f:
                existing_content = f.read()
        else:
            # Create header for new archive file
            existing_content = f"# Session Summary Archive - {month}\n\n"
            existing_content += f"Archived from `agent_session_summary.md` on {datetime.now().strftime('%Y-%m-%d')}.\n\n"
            existing_content += "---\n\n"

        # Append entries (sorted by date)
        month_entries_sorted = sorted(month_entries, key=lambda x: x[1])
        new_content = "\n\n".join(cont.strip() for _, _, cont in month_entries_sorted)

        with open(archive_path, "w", encoding="utf-8") as f:
            f.write(existing_content.rstrip() + "\n\n" + new_content + "\n")

        archive_files.append(str(archive_path))
        print(f"  Archived {len(month_entries)} entries to {archive_path}")

    # Rebuild main file with only recent entries
    recent_content = "\n\n".join(cont.strip() for _, _, cont in sorted(recent_entries, key=lambda x: x[1]))

    with open(summary_file, "w", encoding="utf-8") as f:
        f.write(frontmatter)
        if recent_content:
            f.write(recent_content + "\n")

    print(f"  Kept {len(recent_entries)} recent entries in main file.")

    return len(old_entries), archive_files


def main():
    parser = argparse.ArgumentParser(
        description="Archive old session summary entries to monthly files."
    )
    parser.add_argument(
        "--summary-file",
        type=str,
        default=DEFAULT_SUMMARY_FILE,
        help=f"Path to session summary file (default: {DEFAULT_SUMMARY_FILE})",
    )
    parser.add_argument(
        "--archive-dir",
        type=str,
        default=DEFAULT_ARCHIVE_DIR,
        help=f"Path to archive directory (default: {DEFAULT_ARCHIVE_DIR})",
    )
    parser.add_argument(
        "--threshold",
        type=int,
        default=DEFAULT_LINE_THRESHOLD,
        help=f"Line count threshold to trigger archive (default: {DEFAULT_LINE_THRESHOLD})",
    )
    parser.add_argument(
        "--retention-days",
        type=int,
        default=DEFAULT_RETENTION_DAYS,
        help=f"Days to retain in main file (default: {DEFAULT_RETENTION_DAYS})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without writing files",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Archive regardless of line threshold",
    )

    args = parser.parse_args()

    # Resolve paths relative to repo root
    repo_root = Path(__file__).parent.parent
    summary_file = repo_root / args.summary_file
    archive_dir = repo_root / args.archive_dir

    if not summary_file.exists():
        print(f"Error: Summary file not found: {summary_file}")
        sys.exit(1)

    # Check line count
    line_count = count_lines(summary_file)
    print(f"Session summary: {line_count} lines (threshold: {args.threshold})")

    if line_count <= args.threshold and not args.force:
        print(f"Below threshold. No archive needed.")
        sys.exit(0)

    # Archive old entries
    print(f"\nArchiving entries older than {args.retention_days} days...")
    archived_count, archive_files = archive_old_entries(
        summary_file,
        archive_dir,
        args.retention_days,
        args.dry_run,
    )

    if archived_count > 0:
        new_line_count = count_lines(summary_file)
        print(f"\nArchived {archived_count} entries.")
        if not args.dry_run:
            print(f"New line count: {new_line_count}")

    sys.exit(0)


if __name__ == "__main__":
    main()
