#!/usr/bin/env python3
import argparse
import pathlib
import re
import shutil
import sys

import json

try:
    import yaml
except ImportError:
    yaml = None


VALUE_PATTERN = re.compile(r"{{\s*values\.([a-zA-Z0-9_]+)\s*}}")


def load_values(path):
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        data = json.loads(text)
    else:
        if yaml is None:
            raise ValueError("PyYAML is required for non-JSON values files")
        data = yaml.safe_load(text) or {}
    if not isinstance(data, dict):
        raise ValueError("values file must be a mapping")
    return data


def render_text(text, values):
    def replace(match):
        key = match.group(1)
        if key in values:
            return str(values[key])
        return match.group(0)

    return VALUE_PATTERN.sub(replace, text)


def render_tree(template_dir, output_dir, values):
    if output_dir.exists():
        shutil.rmtree(output_dir)
    shutil.copytree(template_dir, output_dir)

    for path in output_dir.rglob("*"):
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        rendered = render_text(text, values)
        if rendered != text:
            path.write_text(rendered, encoding="utf-8")


def assert_no_placeholders(output_dir):
    unresolved = []
    for path in output_dir.rglob("*"):
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if VALUE_PATTERN.search(text):
            unresolved.append(str(path))
    if unresolved:
        files = "\n".join(unresolved)
        raise ValueError(f"Unresolved placeholders in:\n{files}")


def main():
    parser = argparse.ArgumentParser(
        description="Render Backstage-style values.* placeholders in a template."
    )
    parser.add_argument("template_dir", type=pathlib.Path)
    parser.add_argument("output_dir", type=pathlib.Path)
    parser.add_argument("values_file", type=pathlib.Path)
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail if any {{ values.* }} placeholders remain after render",
    )
    args = parser.parse_args()

    if not args.template_dir.is_dir():
        print(f"template_dir not found: {args.template_dir}", file=sys.stderr)
        sys.exit(1)
    if not args.values_file.is_file():
        print(f"values_file not found: {args.values_file}", file=sys.stderr)
        sys.exit(1)

    values = load_values(args.values_file)
    render_tree(args.template_dir, args.output_dir, values)
    if args.strict:
        assert_no_placeholders(args.output_dir)


if __name__ == "__main__":
    main()
