#!/usr/bin/env python3
import argparse
import datetime as dt
import os
import sys


INDEX_PATH = os.path.join("docs", "90-doc-system", "00_DOC_INDEX.md")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Check doc freshness based on docs/90-doc-system/00_DOC_INDEX.md."
    )
    parser.add_argument(
        "--fail",
        action="store_true",
        help="Exit non-zero when stale or invalid entries are found.",
    )
    parser.add_argument(
        "--today",
        help="Override today's date (YYYY-MM-DD) for testing.",
    )
    return parser.parse_args()


def parse_date(value):
    return dt.date.fromisoformat(value)


def parse_cycle(value):
    value = value.strip()
    if value.endswith("d"):
        return int(value[:-1])
    raise ValueError("review cycle must end with 'd' (days)")


def load_rows(path):
    rows = []
    with open(path, "r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line.startswith("|"):
                continue
            if "---" in line:
                continue
            parts = [part.strip() for part in line.strip("|").split("|")]
            if len(parts) < 4:
                continue
            if parts[0].lower() == "doc":
                continue
            rows.append(parts)
    return rows


def main():
    args = parse_args()
    today = parse_date(args.today) if args.today else dt.date.today()

    if not os.path.exists(INDEX_PATH):
        print(f"ERROR: Missing {INDEX_PATH}")
        return 1

    rows = load_rows(INDEX_PATH)
    if not rows:
        print("ERROR: No living docs found in index.")
        return 1

    warnings = []
    errors = []

    for row in rows:
        doc_path = row[0]
        owner = row[1]
        review_cycle = row[2]
        last_reviewed = row[3]

        if not doc_path or not owner or not review_cycle or not last_reviewed:
            errors.append(f"Missing fields in row: {row}")
            continue

        if not os.path.exists(doc_path):
            errors.append(f"Missing doc file: {doc_path}")
            continue

        try:
            cycle_days = parse_cycle(review_cycle)
        except ValueError as exc:
            errors.append(f"{doc_path}: {exc}")
            continue

        try:
            reviewed_date = parse_date(last_reviewed)
        except ValueError:
            errors.append(f"{doc_path}: invalid date {last_reviewed}")
            continue

        age_days = (today - reviewed_date).days
        if age_days > cycle_days:
            warnings.append(
                f"{doc_path}: overdue by {age_days - cycle_days}d "
                f"(last reviewed {last_reviewed}, cycle {review_cycle})"
            )

    for item in errors:
        print(f"ERROR: {item}")
    for item in warnings:
        print(f"WARN: {item}")

    if args.fail and (errors or warnings):
        return 1
    if errors:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
