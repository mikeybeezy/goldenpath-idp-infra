"""
---
id: SCRIPT-0047
type: script
owner: platform-team
status: active
maturity: 2
dry_run:
  supported: true
  command_hint: --dry-run
test:
  runner: pytest
  command: pytest -q tests/scripts/test_script_0047.py
  evidence: declared
risk_profile:
  production_impact: low
  security_risk: low
  coupling_risk: low
---
"""

"""
Shared utilities for parsing and validating script metadata headers.
"""
import re
import yaml
from pathlib import Path

def extract_frontmatter(content: str) -> str:
    """
    Extracts YAML frontmatter from Python docstrings or Bash comment blocks.
    
    Args:
        content (str): The full file content.
        
    Returns:
        str or None: The raw YAML string if found, else None.
    """
    if not content:
        return None

    # 1. Python Docstring Format: """\n---\n...---\n"""
    # Matches triple-quoted block starting immediately with YAML separator
    py_match = re.search(r'"""\s*\n---\n(.*?)\n---\s*\n', content, re.DOTALL)
    if py_match:
        return py_match.group(1)
        
    # 2. Bash/Shell Comment Format: # ---\n# ...\n# ---
    lines = content.splitlines()
    yaml_lines = []
    in_block = False
    
    for line in lines:
        # Robustly handle indentation:
        # Match optional leading whitespace, then '#', then optional single space
        # Capture strictly the rest of the line (which contains YAML indent)
        match = re.match(r'^\s*# ?(.*)', line)
        if not match:
            continue
            
        cleaned = match.group(1).rstrip()
        
        # Detect separator (---)
        if cleaned == '---':
            if in_block:
                in_block = False
                break
            else:
                in_block = True
                continue
        
        if in_block:
            yaml_lines.append(cleaned)
            
    if yaml_lines:
        return "\n".join(yaml_lines)
        
    return None

def parse_header(content: str) -> dict:
    """Extracts and parses the metadata header."""
    fm = extract_frontmatter(content)
    if not fm:
        return None
    try:
        return yaml.safe_load(fm)
    except yaml.YAMLError:
        return None
