#!/usr/bin/env python3
"""
Governance Vocabulary Generator

Purpose:
    Pivots enums.yaml into a human-readable Markdown table for stakeholders.
"""

import os
import sys
import yaml

# Add lib to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'lib'))
from metadata_config import MetadataConfig

cfg = MetadataConfig()

def generate_vocab():
    output = "# Governance Vocabulary & Allowed Values\n\n"
    output += "This document is auto-generated from `schemas/metadata/enums.yaml`. These are the canonical values allowed in `metadata.yaml` sidecars.\n\n"
    
    enums = cfg.enums
    for section, values in enums.items():
        if section == 'version': continue
        
        output += f"## {section.replace('_', ' ').title()}\n"
        output += "| Value | Description |\n"
        output += "| :--- | :--- |\n"
        for val in values:
            output += f"| `{val}` | Allowed value |\n"
        output += "\n"
        
    with open("docs/governance/GOVERNANCE_VOCABULARY.md", "w") as f:
        f.write(output)
    print("✅ Successfully generated docs/governance/GOVERNANCE_VOCABULARY.md")

if __name__ == "__main__":
    generate_vocab()
