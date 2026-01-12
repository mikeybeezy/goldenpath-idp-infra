"""
---
id: SCRIPT-0030
type: script
owner: platform-team
status: active
maturity: 2
dry_run:
  supported: true
  command_hint: --dry-run
test:
  runner: pytest
  command: pytest -q tests/scripts/test_script_0030.py
  evidence: declared
risk_profile:
  production_impact: low
  security_risk: low
  coupling_risk: low
---
"""

#!/usr/bin/env python3
"""
Doc Scaffold Utility

Purpose:
    Create new Markdown docs with policy-compliant metadata headers derived from
    schemas in schemas/metadata and the rules in docs/90-doc-system/METADATA_STRATEGY.md.
"""
import argparse
import datetime
import os
import re
import sys
from pathlib import Path

import yaml

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT_DIR = SCRIPT_DIR.parent

sys.path.append(str(SCRIPT_DIR / "lib"))
from metadata_config import MetadataConfig, platform_yaml_dump  # noqa: E402

ADR_TEMPLATE = ROOT_DIR / "docs" / "adrs" / "02_adr_template.md"
CHANGELOG_TEMPLATE = ROOT_DIR / "docs" / "changelog" / "Changelog-template.md"




def slug_to_title(value: str) -> str:
    value = value.replace("_", " ").replace("-", " ")
    value = re.sub(r"\s+", " ", value).strip()
    return value.title() if value else value


def infer_doc_type(path: Path, explicit: str | None) -> str:
    if explicit:
        return explicit
    rel = path.as_posix()
    if "/docs/adrs/" in rel:
        return "adr"
    if "/docs/changelog/entries/" in rel:
        return "changelog"
    if "/runbooks/" in rel:
        return "runbook"
    if "/governance/" in rel:
        return "policy"
    if "/contracts/" in rel:
        return "contract"
    if "strategy" in rel:
        return "strategy"
    return "documentation"


def infer_id(path: Path, doc_type: str, explicit: str | None) -> str:
    if explicit:
        return explicit

    base = path.stem
    if doc_type == "adr":
        match = re.match(r"(ADR)-(\d{4})", base, re.IGNORECASE)
        if match:
            return f"{match.group(1).upper()}-{match.group(2)}"
        raise ValueError("ADR docs require an ID like ADR-0001 or filename ADR-0001-*.md")
    if doc_type == "changelog":
        match = re.match(r"(CL)-(\d{4})", base, re.IGNORECASE)
        if match:
            return f"{match.group(1).upper()}-{match.group(2)}"
        raise ValueError("Changelog docs require an ID like CL-0001 or filename CL-0001-*.md")

    return base


def infer_title(path: Path, doc_type: str, explicit: str | None, doc_id: str) -> str:
    if explicit:
        return explicit

    base = path.stem
    if doc_type in {"adr", "changelog"}:
        rest = re.sub(r"^(ADR|CL)-\d{4}-?", "", base, flags=re.IGNORECASE)
        if rest:
            return slug_to_title(rest)
        return doc_id
    return slug_to_title(base)


def build_metadata(cfg: MetadataConfig, doc_type: str, doc_id: str, title: str, args) -> dict:
    skeleton = cfg.get_skeleton(doc_type) or cfg.get_skeleton("documentation") or {}

    data = dict(skeleton)
    data["id"] = doc_id
    data["title"] = title
    data["type"] = doc_type

    if args.owner:
        data["owner"] = args.owner
    if args.status:
        data["status"] = args.status
    if args.domain:
        data["domain"] = args.domain
    if args.category:
        data["category"] = args.category
    elif doc_type == "changelog":
        data["category"] = "changelog"

    if args.date:
        data["date"] = args.date
    elif doc_type in {"adr", "changelog"}:
        data["date"] = datetime.date.today().isoformat()

    return data


def render_frontmatter(metadata: dict) -> str:
    fm = platform_yaml_dump(metadata)
    return f"---\n{fm}---\n\n"


def render_body(template_path: Path | None, doc_type: str, doc_id: str, title: str, args, meta_date: str) -> str:
    if template_path and template_path.exists():
        content = template_path.read_text(encoding="utf-8")
        content = re.sub(r"ADR-XXXX", doc_id, content)
        content = re.sub(r"CL-0001", doc_id, content)
        content = content.replace("<short title>", title)
        content = content.replace("<YYYY-MM-DD>", meta_date or "")
        content = content.replace("<team or person>", args.owner or "")
        content = content.replace("<envs or components>", args.scope or "")
        content = content.replace("<ADR/PR/Issue links>", args.related or "")
        return content.split("---", 2)[-1].lstrip()

    heading = f"# {doc_id}: {title}" if doc_type in {"adr", "changelog"} else f"# {title}"
    return f"{heading}\n\n## Summary\n\n- TODO\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a new doc with compliant frontmatter.")
    parser.add_argument("--path", required=True, help="Path to the new Markdown doc.")
    parser.add_argument("--type", dest="doc_type", default=None, help="Override doc type (adr, changelog, policy).")
    parser.add_argument("--id", dest="doc_id", default=None, help="Override document ID.")
    parser.add_argument("--title", default=None, help="Override document title.")
    parser.add_argument("--owner", default=None, help="Override owner (enum value).")
    parser.add_argument("--status", default=None, help="Override status.")
    parser.add_argument("--domain", default=None, help="Override domain.")
    parser.add_argument("--category", default=None, help="Override category (enum value).")
    parser.add_argument("--date", default=None, help="Date (YYYY-MM-DD).")
    parser.add_argument("--scope", default="", help="Changelog scope placeholder.")
    parser.add_argument("--related", default="", help="Related links placeholder.")
    parser.add_argument("--force", action="store_true", help="Overwrite existing file.")
    args = parser.parse_args()

    path = Path(args.path)
    if path.suffix != ".md":
        raise ValueError("Path must end with .md")

    if path.exists() and not args.force:
        raise FileExistsError(f"File already exists: {path}")

    doc_type = infer_doc_type(path, args.doc_type)
    doc_id = infer_id(path, doc_type, args.doc_id)
    title = infer_title(path, doc_type, args.title, doc_id)

    cfg = MetadataConfig()
    metadata = build_metadata(cfg, doc_type, doc_id, title, args)
    frontmatter = render_frontmatter(metadata)

    template_path = None
    if doc_type == "adr":
        template_path = ADR_TEMPLATE
    elif doc_type == "changelog":
        template_path = CHANGELOG_TEMPLATE

    body = render_body(template_path, doc_type, doc_id, title, args, metadata.get("date", ""))

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(frontmatter + body, encoding="utf-8")

    print(f"✅ Created {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
