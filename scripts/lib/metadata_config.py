"""
---
id: SCRIPT-0046
type: script
owner: platform-team
status: active
maturity: 2
dry_run:
  supported: true
  command_hint: --dry-run
test:
  runner: pytest
  command: pytest -q tests/scripts/test_script_0046.py
  evidence: declared
risk_profile:
  production_impact: low
  security_risk: low
  coupling_risk: low
---
"""

import os
import yaml
from typing import Any, Dict, List, Optional


class PlatformYamlDumper(yaml.SafeDumper):
    """
    Standardized YAML dumper for the Golden Path IDP.
    Ensures consistent indentation (especially for lists) to match yamllint and pre-commit.
    """

    def increase_indent(self, flow=False, indentless=False):
        return super(PlatformYamlDumper, self).increase_indent(flow, False)


def platform_yaml_dump(data: Any, stream=None, **kwargs) -> Optional[str]:
    """
    Helper function to dump YAML using the PlatformYamlDumper with standardized settings.
    """
    settings = {
        "sort_keys": False,
        "default_flow_style": False,
        "allow_unicode": True,
        "indent": 2,
        "Dumper": PlatformYamlDumper,
    }
    settings.update(kwargs)
    return yaml.dump(data, stream, **settings)


def platform_yaml_dump_all(
    documents: List[Any], stream=None, **kwargs
) -> Optional[str]:
    """
    Helper function to dump multiple YAML documents using the PlatformYamlDumper.
    """
    settings = {
        "sort_keys": False,
        "default_flow_style": False,
        "allow_unicode": True,
        "indent": 2,
        "Dumper": PlatformYamlDumper,
        "explicit_start": True,
    }
    settings.update(kwargs)
    return yaml.dump_all(documents, stream, **settings)


class MetadataConfig:
    """
    Central configuration manager for metadata governance.
    Loads enums and schemas to provide a config-driven interface for scripts.
    """

    def __init__(
        self,
        schemas_dir: str = "schemas/metadata",
        enums_file: str = "schemas/metadata/enums.yaml",
    ):
        self.schemas_dir = schemas_dir
        self.enums_file = enums_file
        self.enums = self._load_enums()
        self.schemas = self._load_schemas()
        self.access_file = "schemas/governance/access.yaml"

    def _load_enums(self) -> Dict[str, List[Any]]:
        try:
            with open(self.enums_file, "r") as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            print(f"⚠️ Warning: Could not load enums from {self.enums_file}: {e}")
            return {}

    def _load_schemas(self) -> Dict[str, Dict[str, Any]]:
        schemas = {}
        if not os.path.isdir(self.schemas_dir):
            return schemas

        for f in os.listdir(self.schemas_dir):
            if f.endswith(".schema.yaml"):
                kind = f.replace(".schema.yaml", "")
                try:
                    with open(os.path.join(self.schemas_dir, f), "r") as s:
                        schemas[kind] = yaml.safe_load(s) or {}
                except Exception as e:
                    print(f"⚠️ Warning: Could not load schema {f}: {e}")
        return schemas

    def get_enum_values(self, enum_name: str) -> List[Any]:
        return self.enums.get(enum_name, [])

    def get_schema(self, kind: str) -> Optional[Dict[str, Any]]:
        return self.schemas.get(kind)

    def get_access_config(self) -> Dict[str, Any]:
        """
        Loads the access control list from the governance directory.
        """
        try:
            if os.path.exists(self.access_file):
                with open(self.access_file, "r") as f:
                    return yaml.safe_load(f) or {}
            print(f"⚠️ Warning: Access file {self.access_file} not found.")
        except Exception as e:
            print(f"⚠️ Error loading access config: {e}")
        return {}

    def get_required_fields(self, kind: str) -> List[str]:
        schema = self.get_schema(kind)
        if schema:
            return schema.get("required", [])
        return []

    def validate_field(self, kind: str, field: str, value: Any) -> List[str]:
        """
        Validates a single field against the schema and enums.
        Returns a list of error messages (empty if valid).
        """
        errors = []
        schema = self.get_schema(kind)
        if not schema:
            return errors

        props = schema.get("properties", {})
        if field not in props:
            return errors  # Field not defined in schema, skipping deep validation

        field_schema = props[field]

        # Check enum_from constraint
        enum_name = field_schema.get("enum_from")
        if enum_name:
            allowed = self.get_enum_values(enum_name)
            if value not in allowed:
                errors.append(
                    f"Value '{value}' for field '{field}' is not in allowed enums for '{enum_name}'"
                )

        # Check type constraint for arrays
        if field_schema.get("type") == "array" and isinstance(value, list):
            items_schema = field_schema.get("items", {})
            item_enum_name = items_schema.get("enum_from")
            if item_enum_name:
                allowed = self.get_enum_values(item_enum_name)
                for item in value:
                    if item not in allowed:
                        errors.append(
                            f"Item '{item}' in field '{field}' is not in allowed enums for '{item_enum_name}'"
                        )

        return errors

    def get_skeleton(self, kind: str) -> Dict[str, Any]:
        """
        Generates a default skeleton for a specific document kind based on its schema.
        """
        schema = self.get_schema(kind)
        if not schema:
            return {}

        skeleton = {}
        props = schema.get("properties", {})
        for field, details in props.items():
            if "default" in details:
                skeleton[field] = details["default"]
            elif details.get("type") == "array":
                skeleton[field] = []
            elif details.get("type") == "object":
                skeleton[field] = {}
            elif field in [
                "id",
                "title",
                "type",
                "owner",
                "risk_profile",
                "reliability",
                "value_quantification",
            ]:
                # Mandatory identity/ownership fields and specific object fields should be present even if empty
                if details.get("type") == "object":
                    skeleton[field] = {}
                else:
                    skeleton[field] = ""
        return skeleton

    def find_all_parents_metadata(self, filepath: str) -> List[Dict[str, Any]]:
        """
        Walks up the directory tree to find all parent metadata.yaml files.
        Returns them in order from root-most to leaf-most.
        """
        all_parent_data = []
        abs_filepath = os.path.abspath(filepath)
        current_dir = os.path.dirname(abs_filepath)
        root_dir = os.getcwd()

        # Collect all parents
        while current_dir.startswith(root_dir):
            parent_metadata_file = os.path.join(current_dir, "metadata.yaml")
            if parent_metadata_file != abs_filepath and os.path.exists(
                parent_metadata_file
            ):
                try:
                    with open(parent_metadata_file, "r") as f:
                        data = yaml.safe_load(f)
                        if isinstance(data, dict):
                            all_parent_data.append(data)
                except:
                    pass

            # Move up
            next_dir = os.path.dirname(current_dir)
            if next_dir == current_dir or current_dir == root_dir:
                break
            current_dir = next_dir

        # Reverse so root-most is first (for proper merging)
        all_parent_data.reverse()
        return all_parent_data

    def find_parent_metadata(self, filepath: str) -> Optional[Dict[str, Any]]:
        """
        Nearest parent metadata.yaml. Provided for backward compatibility.
        """
        parents = self.find_all_parents_metadata(filepath)
        return parents[-1] if parents else None

    def get_effective_metadata(
        self, filepath: str, local_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Merges local metadata with inherited parent defaults recursively (root -> leaf -> local).
        """
        parents_data = self.find_all_parents_metadata(filepath)

        # Identity (ID/Title) should NEVER be inherited
        identity_fields = ["id", "title"]

        effective = {}
        # Merge all parents starting from root-most
        for parent in parents_data:
            for k, v in parent.items():
                if k not in identity_fields and v is not None and v != "":
                    effective[k] = v

        # Finally, merge local data (overrides parents)
        for k, v in local_data.items():
            if v is not None and v != "" and v != {} and v != []:
                effective[k] = v

        return effective
