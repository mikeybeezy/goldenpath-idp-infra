#!/usr/bin/env python3
"""
Backstage Documentation Entity Generator

Generates individual Backstage Component entities for ADRs and changelog entries,
making all governance documentation discoverable in the Backstage catalog.
"""

import os
import yaml
import re
from pathlib import Path

ADR_DIR = "docs/adrs"
CHANGELOG_DIR = "docs/changelog/entries"
OUTPUT_DIR = "backstage-helm/demo-catalog/docs"

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
                    "github.com/project-slug": "mikeybeezy/goldenpath-idp-infra"
                },
                "tags": ["adr", "governance", "documentation"],
                "links": [{
                    "url": f"https://github.com/mikeybeezy/goldenpath-idp-infra/blob/development/docs/adrs/{adr_file.name}",
                    "title": "View on GitHub",
                    "icon": "docs"
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
        with open(output_file, 'w') as f:
            yaml.dump(entity, f, sort_keys=False)
        
        entities.append(f"./docs/adrs/{component_name}.yaml")
    
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
                    "github.com/project-slug": "mikeybeezy/goldenpath-idp-infra"
                },
                "tags": ["changelog", "release-notes", "documentation"],
                "links": [{
                    "url": f"https://github.com/mikeybeezy/goldenpath-idp-infra/blob/development/docs/changelog/entries/{cl_file.name}",
                    "title": "View on GitHub",
                    "icon": "docs"
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
        with open(output_file, 'w') as f:
            yaml.dump(entity, f, sort_keys=False)
        
        entities.append(f"./docs/changelogs/{component_name}.yaml")
    
    print(f"✅ Generated {len(entities)} changelog entities")
    return entities

def create_location_files(adr_entities, changelog_entities):
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
    
    with open(output_dir / "all-adrs.yaml", 'w') as f:
        yaml.dump(adr_location, f, sort_keys=False)
    
    with open(output_dir / "all-changelogs.yaml", 'w') as f:
        yaml.dump(cl_location, f, sort_keys=False)
    
    print(f"✅ Created location files with ALL entities")

if __name__ == "__main__":
    print("🚀 Generating Backstage documentation entities...")
    
    adr_entities = generate_adr_entities()
    changelog_entities = generate_changelog_entities()
    create_location_files(adr_entities, changelog_entities)
    
    print(f"\n📊 Summary:")
    print(f"   - Total ADRs: {len(adr_entities)}")
    print(f"   - Total Changelogs: {len(changelog_entities)}")
    print(f"   - Output: {OUTPUT_DIR}")
    print(f"\n✅ All entities included in catalog locations")
