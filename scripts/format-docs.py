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

        # 1. Standardize frontmatter markers (no leading/trailing whitespace on the marker line)
        lines = []
        for line in content.splitlines():
            stripped = line.strip()
            if stripped == '---':
                lines.append('---')
            else:
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
