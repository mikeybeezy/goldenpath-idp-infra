#!/usr/bin/env python3
"""
Header Injection Script
Adds 'Breadcrumb' headers to critical files to guide unmanaged agents.
"""
import os
import sys

HEADER_MD = "<!-- AGENT_CONTEXT: Read .agent/README.md for rules -->"
HEADER_PY = "# AGENT_CONTEXT: Read .agent/README.md for rules"
HEADER_TF = "# AGENT_CONTEXT: Read .agent/README.md for rules"

TARGET_EXTS = {
    '.md': HEADER_MD,
    '.py': HEADER_PY,
    '.tf': HEADER_TF,
}

def inject_header(filepath):
    ext = os.path.splitext(filepath)[1]
    if ext not in TARGET_EXTS:
        return
    
    header = TARGET_EXTS[ext]
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    if header in content:
        return # Already injected
    
    print(f"Injecting header into {filepath}")
    with open(filepath, 'w') as f:
        f.write(header + "\n" + content)

def main():
    # Only scan likely targets to avoid noise
    target_dirs = ['.agent', 'docs', 'scripts', 'envs']
    repo_root = os.getcwd()
    
    for target in target_dirs:
        path = os.path.join(repo_root, target)
        if not os.path.exists(path):
            continue
            
        for root, _, files in os.walk(path):
            for file in files:
                if file.endswith(('.md', '.py', '.tf')):
                    inject_header(os.path.join(root, file))

    # Also target root files
    for file in os.listdir(repo_root):
         if file.endswith(('.md', '.py', '.tf')):
            inject_header(os.path.join(repo_root, file))

if __name__ == "__main__":
    main()
