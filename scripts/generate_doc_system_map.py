#!/usr/bin/env python3
"""
---
id: SCRIPT-0020
type: script
owner: platform-team
status: active
maturity: 2
dry_run:
  supported: true
  command_hint: --dry-run
test:
  runner: pytest
  command: pytest -q tests/scripts/test_script_0020.py
  evidence: declared
risk_profile:
  production_impact: low
  security_risk: low
  coupling_risk: low
---
"""

"""
Generate and refresh the platform documentation system map.

Updates docs/90-doc-system/PLATFORM_SYSTEM_MAP.md with current counts for
living docs, Backstage indexes, and report sidecars.
"""
import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = ROOT / "docs/90-doc-system/PLATFORM_SYSTEM_MAP.md"
DOC_INDEX = ROOT / "docs/90-doc-system/00_DOC_INDEX.md"

BACKSTAGE_INDEXES = {
    "governance": ROOT / "backstage-helm/catalog/docs/governance-index.yaml",
    "adrs": ROOT / "backstage-helm/catalog/docs/adrs-index.yaml",
    "changelogs": ROOT / "backstage-helm/catalog/docs/changelogs-index.yaml",
}

def count_living_docs(path: Path) -> int:
    if not path.exists():
        return 0
    count = 0
    for line in path.read_text().splitlines():
        if line.startswith("| docs/"):
            count += 1
    return count

def count_targets(path: Path) -> int:
    if not path.exists():
        return 0
    count = 0
    for line in path.read_text().splitlines():
        line = line.strip()
        if line.startswith("- "):
            count += 1
    return count

def count_report_sidecars(root: Path) -> int:
    return len(list(root.glob("reports/**/*.metadata.yaml")))

def replace_block(content: str, start: str, end: str, new_block: str) -> str:
    before, rest = content.split(start, 1)
    _, after = rest.split(end, 1)
    return f"{before}{start}\n{new_block}\n{end}{after}"

def main() -> None:
    if not DOC_PATH.exists():
        raise SystemExit(f"Missing doc: {DOC_PATH}")

    living = count_living_docs(DOC_INDEX)
    gov = count_targets(BACKSTAGE_INDEXES["governance"])
    adrs = count_targets(BACKSTAGE_INDEXES["adrs"])
    cls = count_targets(BACKSTAGE_INDEXES["changelogs"])
    reports = count_report_sidecars(ROOT)

    generated = datetime.date.today().isoformat()

    table = "\n".join([
        "| Area | Source of Truth | Backstage Index | Count | Validator/Generator | Notes |",
        "| --- | --- | --- | --- | --- | --- |",
        f"| Living docs | docs/90-doc-system/00_DOC_INDEX.md | n/a | {living} | scripts/check-doc-freshness.py | Review cadence enforced here |",
        f"| Governance docs | docs/10-governance/*.md | backstage-helm/catalog/docs/governance-index.yaml | {gov} | scripts/validate_metadata.py | TechDocs list for governance |",
        f"| ADRs | docs/adrs/*.md | backstage-helm/catalog/docs/adrs-index.yaml | {adrs} | scripts/validate_metadata.py | Backstage ADR list |",
        f"| Changelogs | docs/changelog/entries/*.md | backstage-helm/catalog/docs/changelogs-index.yaml | {cls} | scripts/validate_metadata.py | Backstage changelog list |",
        f"| Reports | reports/** | n/a | {reports} | scripts/validate_metadata.py | Sidecar metadata required |",
        f"| Generated | {generated} | n/a | n/a | generate_doc_system_map.py | Snapshot only |",
    ])

    content = DOC_PATH.read_text()
    content = replace_block(content, "<!-- MAP_TABLE_START -->", "<!-- MAP_TABLE_END -->", table)
    DOC_PATH.write_text(content)

if __name__ == "__main__":
    main()
