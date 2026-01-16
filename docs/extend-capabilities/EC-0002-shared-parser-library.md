---
id: EC-0002-shared-parser-library
title: Shared Parser Library for Contract-Driven Requests
status: proposed
dependencies:
  - 3+ parser scripts in production
  - RDS and Secret parsers stable
relates_to:
  - scripts/rds_request_parser.py
  - scripts/secret_request_parser.py
  - docs/85-how-it-works/self-service/CONTRACT_DRIVEN_ARCHITECTURE.md
type: extension_capability
priority: low
vq_class: efficiency
estimated_roi: Reduced duplication, faster new parser development
effort_estimate: 2-3 weeks
owner: platform-team
---

## Shared Parser Library for Contract-Driven Requests

This document proposes extracting common functionality from parser scripts into a shared library to reduce duplication and accelerate new parser development.

**Status**: Parked until 3+ parser scripts exist.

## Executive Summary

As Golden Path IDP adds more self-service request types (RDS, Secrets, ECR, Knative Services), each parser script duplicates common functionality: YAML loading, enum validation, file writing, and policy enforcement. Extracting these into a shared library (`scripts/lib/`) would:

- **Reduce Duplication**: Common patterns implemented once
- **Accelerate Development**: New parsers inherit validated patterns
- **Improve Consistency**: Single source of truth for validation logic
- **Enable Testing**: Shared test utilities across parsers

**Trigger**: Revisit when 3+ parser scripts exist and duplication becomes painful.

## Problem Statement

Current parser scripts (`secret_request_parser.py`, `rds_request_parser.py`) share significant common code:

1. **YAML/JSON Loading**: `load_yaml()`, `write_yaml()`, `write_json()`
2. **Enum Validation**: Loading from `schemas/metadata/enums.yaml`, checking values
3. **Path Generation**: Building output paths for tfvars and ExternalSecrets
4. **CLI Patterns**: `--mode`, `--dry-run`, `--enums`, `--input-files`
5. **Error Handling**: Collecting failures, exit codes

As we add ECR, Knative, and other parsers, this duplication compounds.

## Proposed Solution

### Directory Structure

```text
scripts/
  lib/
    __init__.py
    schema_loader.py    # YAML/JSON loading utilities
    validation.py       # Enum validation helpers
    render.py           # Template rendering (tfvars, ExternalSecret)
    fs.py               # File system operations (mkdir, write)
    policy.py           # Policy enforcement (env-specific rules)
  parsers/
    __init__.py
    base.py             # BaseParser class
    rds.py              # RdsRequestParser (refactored)
    secret.py           # SecretRequestParser (refactored)
    ecr.py              # EcrRequestParser (future)
  rds_request_parser.py      # Thin CLI wrapper
  secret_request_parser.py   # Thin CLI wrapper
  validate_request.py        # Generic validation CLI
  validate_schemas.py        # Schema validation CLI
```

### Shared Modules

#### `schema_loader.py`

```python
"""Schema and YAML loading utilities."""
from pathlib import Path
from typing import Any, Dict
import yaml

def load_yaml(path: Path) -> Dict[str, Any]:
    """Load YAML file with error handling."""
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}

def load_enums(enums_path: Path, section: str) -> Dict[str, list]:
    """Load enum values from metadata file."""
    data = load_yaml(enums_path)
    # Handle nested sections (e.g., 'rds', 'security')
    ...
```

#### `validation.py`

```python
"""Validation helpers for request contracts."""
from typing import List

def check_enum(field: str, value: str, allowed: List[str], src_path: Path) -> None:
    """Validate value against allowed enum values."""
    if value not in allowed:
        raise ValueError(f"{src_path}: invalid {field}='{value}'. Allowed: {allowed}")

def check_required(fields: Dict[str, Any], src_path: Path) -> None:
    """Validate all required fields are present."""
    missing = [k for k, v in fields.items() if not v]
    if missing:
        raise ValueError(f"{src_path}: missing required fields: {', '.join(missing)}")
```

#### `render.py`

```python
"""Template rendering for generated artifacts."""
from typing import Any, Dict

def render_externalsecret(
    name: str,
    namespace: str,
    secret_key: str,
    labels: Dict[str, str],
    target_name: str,
) -> Dict[str, Any]:
    """Generate ExternalSecret manifest."""
    return {
        "apiVersion": "external-secrets.io/v1beta1",
        "kind": "ExternalSecret",
        "metadata": {
            "name": name,
            "namespace": namespace,
            "labels": labels,
        },
        "spec": {
            "refreshInterval": "1h",
            "secretStoreRef": {"name": "aws-secretsmanager", "kind": "ClusterSecretStore"},
            "target": {"name": target_name, "creationPolicy": "Owner"},
            "dataFrom": [{"extract": {"key": secret_key}}],
        },
    }
```

#### `fs.py`

```python
"""File system operations."""
from pathlib import Path
from typing import Any, Dict
import json
import yaml

def write_yaml(path: Path, obj: Dict[str, Any]) -> None:
    """Write YAML file with directory creation."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(obj, f, sort_keys=False)

def write_json(path: Path, obj: Dict[str, Any]) -> None:
    """Write JSON file with directory creation."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, sort_keys=True)
        f.write("\n")
```

#### `policy.py`

```python
"""Policy enforcement for request validation."""
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class PolicyResult:
    passed: bool
    warnings: List[str]
    errors: List[str]

def enforce_env_policies(environment: str, request: Any) -> PolicyResult:
    """Apply environment-specific policy rules."""
    warnings = []
    errors = []

    if environment == "prod":
        # Production-specific rules
        ...
    elif environment == "dev":
        # Dev-specific rules
        ...

    return PolicyResult(
        passed=len(errors) == 0,
        warnings=warnings,
        errors=errors,
    )
```

### Base Parser Class

```python
"""Base parser class for contract-driven requests."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Type

from scripts.lib.schema_loader import load_yaml, load_enums
from scripts.lib.validation import check_required
from scripts.lib.fs import write_yaml, write_json

@dataclass
class ParseResult:
    success: bool
    request: Any
    tfvars_path: Path
    externalsecret_path: Path
    errors: List[str]

class BaseParser(ABC):
    """Base class for request parsers."""

    def __init__(self, enums_path: Path):
        self.enums = self.load_enums(enums_path)

    @abstractmethod
    def load_enums(self, enums_path: Path) -> Dict[str, List[str]]:
        """Load parser-specific enums."""
        pass

    @abstractmethod
    def parse_request(self, doc: Dict[str, Any], src_path: Path) -> Any:
        """Parse YAML document into request dataclass."""
        pass

    @abstractmethod
    def validate_enums(self, request: Any, src_path: Path) -> None:
        """Validate request fields against enums."""
        pass

    @abstractmethod
    def generate_tfvars(self, request: Any) -> Dict[str, Any]:
        """Generate Terraform variables."""
        pass

    @abstractmethod
    def generate_externalsecret(self, request: Any) -> Dict[str, Any]:
        """Generate ExternalSecret manifest."""
        pass

    def process(self, src_path: Path, mode: str, dry_run: bool = False) -> ParseResult:
        """Process a single request file."""
        doc = load_yaml(src_path)
        request = self.parse_request(doc, src_path)
        self.validate_enums(request, src_path)

        if mode == "generate":
            tfvars = self.generate_tfvars(request)
            externalsecret = self.generate_externalsecret(request)

            if not dry_run:
                write_json(self.tfvars_output_path(request), tfvars)
                write_yaml(self.externalsecret_output_path(request), externalsecret)

        return ParseResult(...)
```

### CLI Tools

#### `validate_request.py`

```bash
# Validate any request against its schema
python3 scripts/validate_request.py \
  --type rds \
  --input docs/20-contracts/rds-requests/dev/RDS-0001.yaml
```

#### `validate_schemas.py`

```bash
# Validate all schemas in schemas/requests/
python3 scripts/validate_schemas.py --schemas-dir schemas/requests/
```

## Migration Strategy

### Phase 1: Extract Library (No Breaking Changes)

1. Create `scripts/lib/` with shared modules
2. Existing parsers continue to work unchanged
3. New code imports from lib

### Phase 2: Refactor Existing Parsers

1. Refactor `secret_request_parser.py` to use lib
2. Refactor `rds_request_parser.py` to use lib
3. Maintain CLI compatibility

### Phase 3: Add Base Parser

1. Create `BaseParser` class
2. Create parser subclasses in `scripts/parsers/`
3. CLI wrappers delegate to parser classes

## Prerequisites Before Starting

- [ ] 3+ parser scripts exist (currently: 2)
- [ ] Duplication causing maintenance pain
- [ ] Clear patterns emerged from existing parsers
- [ ] Test coverage for existing parsers

## Success Metrics

- **Code Reduction**: 30%+ reduction in parser LOC
- **New Parser Time**: <1 day to create new parser (vs. current ~3 days)
- **Test Coverage**: Shared lib at 90%+ coverage
- **Consistency**: All parsers follow identical patterns

## Risk Analysis

|Risk|Impact|Mitigation|
|------|--------|------------|
|**Premature Abstraction**|Medium|Wait for 3+ parsers before extracting|
|**Breaking Changes**|Low|Maintain CLI compatibility throughout|
|**Over-Engineering**|Medium|Start with simple extractions, not full framework|

## References

- [Contract-Driven Architecture](../85-how-it-works/self-service/CONTRACT_DRIVEN_ARCHITECTURE.md)
- [RDS Parser](../../scripts/rds_request_parser.py): SCRIPT-0034
- [Secret Parser](../../scripts/secret_request_parser.py): SCRIPT-0033

---

**Status**: Proposed (parked until trigger condition met)
**Trigger**: Revisit when 3+ parser scripts exist
**Contact**: @platform-team for questions
