"""
Purpose: Global Formatting & Whitespace Normalizer
Achievement: Enforces strict EOF newlines, strips trailing whitespace, and standardizes
             frontmatter terminators across all text-based files.
Value: Ensures a premium, consistent look-and-feel across the entire documentation estate
       while preventing "noise" in git diffs caused by erratic whitespace.
"""
import os

def is_binary(filepath):
    try:
        with open(filepath, 'tr') as f:
            f.read(1024)
            return False
    except:
        return True

def fix_formatting(filepath):
    if is_binary(filepath):
        return False

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # 1. Standardize frontmatter markers safely
        lines = []
        in_frontmatter = False
        frontmatter_done = False

        for i, line in enumerate(content.splitlines()):
            stripped = line.strip()

            # Standardize frontmatter markers ONLY if they appear at the start of the file
            if not frontmatter_done:
                if i == 0 and stripped == '---':
                    in_frontmatter = True
                    lines.append('---')
                    continue
                elif in_frontmatter and stripped == '---':
                    in_frontmatter = False
                    frontmatter_done = True
                    lines.append('---')
                    continue

            # For all other lines, only remove trailing whitespace
            lines.append(line.rstrip())

        # 2. Strip all trailing empty lines
        while lines and not lines[-1]:
            lines.pop()

        # 3. Ensure exactly one trailing newline
        if not lines:
            new_content = ''
        else:
            new_content = '\n'.join(lines) + '\n'

        if content != new_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return True
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
    return False

def scan_and_fix(start_root='.'):
    fixed_count = 0
    for root, dirs, files in os.walk(start_root):
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != 'node_modules' and d != 'api_server']
        for file in files:
            if file.startswith('.') or file.endswith(('.png', '.jpg', '.jpeg', '.gif', '.ico', '.pdf', '.webp', '.tfstate', '.tfvars')):
                continue
            filepath = os.path.join(root, file)
            if fix_formatting(filepath):
                print(f"Fixed: {filepath}")
                fixed_count += 1
    print(f"Total files fixed: {fixed_count}")

if __name__ == '__main__':
    scan_and_fix()
