#!/usr/bin/env python3
"""
Backstage Documentation Entity Generator

Generates individual Backstage Component entities for ADRs and changelog entries,
making all governance documentation discoverable in the Backstage catalog.
"""

import os
import re
from pathlib import Path

import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'lib'))
from metadata_config import platform_yaml_dump

ADR_DIR = "docs/adrs"
CHANGELOG_DIR = "docs/changelog/entries"
GOVERNANCE_DIR = "docs/10-governance"
OUTPUT_DIR = "backstage-helm/catalog/docs"
REPO_SLUG = "mikeybeezy/goldenpath-idp-infra"
REPO_BRANCH = "main"
BLOB_BASE = f"https://github.com/{REPO_SLUG}/blob/{REPO_BRANCH}"
EDIT_BASE = f"https://github.com/{REPO_SLUG}/edit/{REPO_BRANCH}"


def dump_yaml(data, path: Path) -> None:
    with open(path, 'w', encoding='utf-8') as f:
        platform_yaml_dump(data, f)

def build_urls(rel_path: str) -> tuple[str, str]:
    view_url = f"{BLOB_BASE}/{rel_path}"
    edit_url = f"{EDIT_BASE}/{rel_path}"
    return view_url, edit_url

def extract_frontmatter_and_content(file_path):
    """Extract YAML frontmatter and first paragraph from markdown file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check for frontmatter
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            frontmatter = yaml.safe_load(parts[1]) or {}
            body = parts[2].strip()
        else:
            frontmatter = {}
            body = content
    else:
        frontmatter = {}
        body = content

    # Extract first paragraph (description)
    paragraphs = [p.strip() for p in body.split('\n\n') if p.strip() and not p.strip().startswith('#')]
    description = paragraphs[0][:200] + '...' if paragraphs and len(paragraphs[0]) > 200 else (paragraphs[0] if paragraphs else "")

    # Get title from first H1 or filename
    title_match = re.search(r'^#\s+(.+)$', body, re.MULTILINE)
    title = title_match.group(1) if title_match else Path(file_path).stem

    return frontmatter, title, description

def generate_adr_entities():
    """Generate Backstage entities for all ADRs."""
    adr_output_dir = Path(OUTPUT_DIR) / "adrs"
    adr_output_dir.mkdir(parents=True, exist_ok=True)

    adr_files = sorted(Path(ADR_DIR).glob("ADR-*.md"))
    entities = []

    for adr_file in adr_files:
        frontmatter, title, description = extract_frontmatter_and_content(adr_file)
        rel_path = f"docs/adrs/{adr_file.name}"
        view_url, edit_url = build_urls(rel_path)

        # Extract ADR number from filename
        adr_number = adr_file.stem.split('-')[1]
        component_name = f"adr-{adr_number}"

        entity = {
            "apiVersion": "backstage.io/v1alpha1",
            "kind": "Component",
            "metadata": {
                "name": component_name,
                "title": title,
                "description": description,
                "annotations": {
                    "github.com/project-slug": REPO_SLUG,
                    "backstage.io/view-url": view_url,
                    "backstage.io/edit-url": edit_url
                },
                "tags": ["adr", "governance", "documentation"],
                "links": [{
                    "url": view_url,
                    "title": "View on GitHub",
                    "icon": "github"
                }]
            },
            "spec": {
                "type": "documentation",
                "lifecycle": frontmatter.get("status", "active").lower(),
                "owner": frontmatter.get("owner", "platform-team"),
                "subcomponentOf": "architecture-decision-records"
            }
        }

        # Write individual entity file
        output_file = adr_output_dir / f"{component_name}.yaml"
        dump_yaml(entity, output_file)

        entities.append(f"./adrs/{component_name}.yaml")

    print(f"✅ Generated {len(entities)} ADR entities")
    return entities

def generate_changelog_entities():
    """Generate Backstage entities for all changelog entries."""
    cl_output_dir = Path(OUTPUT_DIR) / "changelogs"
    cl_output_dir.mkdir(parents=True, exist_ok=True)

    cl_files = sorted(Path(CHANGELOG_DIR).glob("CL-*.md"))
    entities = []

    for cl_file in cl_files:
        frontmatter, title, description = extract_frontmatter_and_content(cl_file)
        rel_path = f"docs/changelog/entries/{cl_file.name}"
        view_url, edit_url = build_urls(rel_path)

        # Extract CL number from filename
        cl_number = cl_file.stem.split('-')[1]
        component_name = f"changelog-{cl_number}"

        entity = {
            "apiVersion": "backstage.io/v1alpha1",
            "kind": "Component",
            "metadata": {
                "name": component_name,
                "title": title,
                "description": description,
                "annotations": {
                    "github.com/project-slug": REPO_SLUG,
                    "backstage.io/view-url": view_url,
                    "backstage.io/edit-url": edit_url
                },
                "tags": ["cl", "changelog", "release-notes", "documentation"],
                "links": [{
                    "url": view_url,
                    "title": "View on GitHub",
                    "icon": "github"
                }]
            },
            "spec": {
                "type": "documentation",
                "lifecycle": "production",
                "owner": "platform-team",
                "subcomponentOf": "changelog-documentation"
            }
        }

        # Write individual entity file
        output_file = cl_output_dir / f"{component_name}.yaml"
        dump_yaml(entity, output_file)

        entities.append(f"./changelogs/{component_name}.yaml")

    print(f"✅ Generated {len(entities)} changelog entities")
    return entities

def generate_governance_entities():
    """Generate Backstage entities for governance docs."""
    gov_output_dir = Path(OUTPUT_DIR) / "governance"
    gov_output_dir.mkdir(parents=True, exist_ok=True)

    gov_files = sorted(Path(GOVERNANCE_DIR).rglob("*.md"))
    entities = []

    for gov_file in gov_files:
        frontmatter, title, description = extract_frontmatter_and_content(gov_file)

        rel_path = gov_file.relative_to(GOVERNANCE_DIR).as_posix()
        doc_path = f"docs/10-governance/{rel_path}"
        view_url, edit_url = build_urls(doc_path)
        component_name = f"governance-{rel_path}".replace("/", "-").replace("_", "-").replace(".md", "").lower()

        tags = ["gove", "governance", "documentation"]
        doc_type = frontmatter.get("type")
        if doc_type and doc_type not in tags:
            tags.append(doc_type)

        entity = {
            "apiVersion": "backstage.io/v1alpha1",
            "kind": "Component",
            "metadata": {
                "name": component_name,
                "title": title,
                "description": description,
                "annotations": {
                    "github.com/project-slug": REPO_SLUG,
                    "backstage.io/view-url": view_url,
                    "backstage.io/edit-url": edit_url
                },
                "tags": tags,
                "links": [{
                    "url": view_url,
                    "title": "View on GitHub",
                    "icon": "github"
                }]
            },
            "spec": {
                "type": "documentation",
                "lifecycle": frontmatter.get("status", "active").lower(),
                "owner": frontmatter.get("owner", "platform-team"),
                "subcomponentOf": "governance-documentation"
            }
        }

        output_file = gov_output_dir / f"{component_name}.yaml"
        dump_yaml(entity, output_file)

        entities.append(f"./governance/{component_name}.yaml")

    print(f"✅ Generated {len(entities)} governance entities")
    return entities

def create_location_files(adr_entities, changelog_entities, governance_entities):
    """Create Location files that reference all generated entities."""

    # ADR Location - ALL entities
    adr_location = {
        "apiVersion": "backstage.io/v1alpha1",
        "kind": "Location",
        "metadata": {
            "name": "all-adrs",
            "description": "All Architecture Decision Records"
        },
        "spec": {
            "targets": adr_entities  # ALL ADRS
        }
    }

    # Changelog Location - ALL entities
    cl_location = {
        "apiVersion": "backstage.io/v1alpha1",
        "kind": "Location",
        "metadata": {
            "name": "all-changelogs",
            "description": "All Changelog Entries"
        },
        "spec": {
            "targets": changelog_entities  # ALL CHANGELOGS
        }
    }

    output_dir = Path(OUTPUT_DIR)

    dump_yaml(adr_location, output_dir / "adrs-index.yaml")

    dump_yaml(cl_location, output_dir / "changelogs-index.yaml")

    # Governance Location - ALL entities
    gov_location = {
        "apiVersion": "backstage.io/v1alpha1",
        "kind": "Location",
        "metadata": {
            "name": "all-governance",
            "description": "All Governance Documentation"
        },
        "spec": {
            "targets": governance_entities
        }
    }
    dump_yaml(gov_location, output_dir / "governance-index.yaml")

    print(f"✅ Created location files with ALL entities")

if __name__ == "__main__":
    print("🚀 Generating Backstage documentation entities...")

    adr_entities = generate_adr_entities()
    changelog_entities = generate_changelog_entities()
    governance_entities = generate_governance_entities()
    create_location_files(adr_entities, changelog_entities, governance_entities)

    print(f"\n📊 Summary:")
    print(f"   - Total ADRs: {len(adr_entities)}")
    print(f"   - Total Changelogs: {len(changelog_entities)}")
    print(f"   - Total Governance Docs: {len(governance_entities)}")
    print(f"   - Output: {OUTPUT_DIR}")
    print(f"\n✅ All entities included in catalog locations")
