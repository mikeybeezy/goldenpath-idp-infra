#!/usr/bin/env python3
"""
---
id: SCRIPT-0035
type: script
owner: platform-team
status: active
maturity: 1
dry_run:
  supported: true
  command_hint: --dry-run
test:
  runner: pytest
  command: pytest -q tests/scripts/test_script_0035.py
  evidence: declared
risk_profile:
  production_impact: medium
  security_risk: medium
  coupling_risk: low
relates_to:
  - PRD-0001-rds-user-db-provisioning
  - ADR-0165-rds-user-db-provisioning-automation
---

RDS User and Database Provisioning Script.

Reads application_databases from Terraform tfvars, fetches credentials from
AWS Secrets Manager, and creates PostgreSQL roles and databases idempotently.

Usage:
    python3 scripts/rds_provision.py \\
        --env dev \\
        --tfvars envs/dev-rds/terraform.tfvars \\
        --master-secret goldenpath/dev/rds/master \\
        [--build-id 16-01-26-01] \\
        [--run-id 12345678] \\
        [--dry-run]

Features:
    - Idempotent: Safe to re-run without side effects
    - Auditable: Emits structured logs with build_id and run_id
    - Secure: Uses SSL connections, no password logging
    - Fail-fast: Exits immediately on missing secrets or connection errors
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import re
import socket
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%SZ",
)
logger = logging.getLogger(__name__)


# =============================================================================
# Data Classes
# =============================================================================


# Access level to SQL grants mapping
ACCESS_LEVELS = {
    "owner": {
        "database": "ALL PRIVILEGES",
        "schema": "ALL",
        "tables": "ALL",
        "sequences": "ALL",
        "default_tables": "ALL",
        "default_sequences": "ALL",
    },
    "editor": {
        "database": "CONNECT",
        "schema": "USAGE",
        "tables": "SELECT, INSERT, UPDATE, DELETE",
        "sequences": "USAGE, SELECT",
        "default_tables": "SELECT, INSERT, UPDATE, DELETE",
        "default_sequences": "USAGE, SELECT",
    },
    "reader": {
        "database": "CONNECT",
        "schema": "USAGE",
        "tables": "SELECT",
        "sequences": "SELECT",
        "default_tables": "SELECT",
        "default_sequences": "SELECT",
    },
}


@dataclass
class AppDatabase:
    """Application database definition from tfvars."""

    name: str
    database_name: str
    username: str
    access_level: str = "owner"  # owner, editor, reader


@dataclass
class RdsCredentials:
    """RDS connection credentials from Secrets Manager."""

    host: str
    port: int
    username: str
    password: str
    dbname: str

    def __repr__(self) -> str:
        """Mask password in repr for security."""
        return f"RdsCredentials(host={self.host}, port={self.port}, username={self.username}, dbname={self.dbname})"


@dataclass
class ProvisionResult:
    """Result of a provisioning operation."""

    database: str
    username: str
    action: str
    status: str  # success, no_change, error
    duration_ms: int
    message: str


@dataclass
class AuditRecord:
    """Audit record for governance tracking."""

    timestamp_utc: str
    environment: str
    build_id: str
    run_id: str
    database: str
    username: str
    action: str
    status: str
    duration_ms: int
    message: str

    def to_csv_row(self) -> str:
        """Format as CSV row."""
        return ",".join(
            [
                self.timestamp_utc,
                self.environment,
                self.build_id,
                self.run_id,
                self.database,
                self.username,
                self.action,
                self.status,
                str(self.duration_ms),
                self.message.replace(",", ";"),  # Escape commas
            ]
        )


# =============================================================================
# Pre-flight Validation Data Classes
# =============================================================================


@dataclass
class HostnameValidationResult:
    """Result of hostname DNS validation."""

    success: bool
    ip_address: Optional[str] = None
    error_message: str = ""
    remediation: str = ""


@dataclass
class PreflightCheckResult:
    """Result of all pre-flight checks."""

    passed: bool
    failed_checks: List[str] = field(default_factory=list)
    remediation: str = ""


# =============================================================================
# Pre-flight Validation Functions
# =============================================================================


def validate_rds_hostname(hostname: str, env: str = "dev") -> HostnameValidationResult:
    """
    Validate that an RDS hostname can be resolved via DNS.

    This is a pre-flight check to catch the common case where an RDS instance
    doesn't exist but the provisioning script tries to connect anyway.

    Args:
        hostname: The RDS endpoint hostname to validate
        env: Environment name for remediation messaging

    Returns:
        HostnameValidationResult with success status and error details
    """
    try:
        ip_address = socket.gethostbyname(hostname)
        return HostnameValidationResult(
            success=True,
            ip_address=ip_address,
            error_message="",
            remediation=""
        )
    except socket.gaierror as e:
        # Extract the identifier from the hostname for clearer messaging
        # Format: identifier.random.region.rds.amazonaws.com
        identifier = hostname.split(".")[0] if "." in hostname else hostname

        error_message = (
            f"RDS instance does not exist or is not reachable. "
            f"Hostname '{identifier}' could not be resolved. "
            f"DNS error: {e}"
        )

        remediation = (
            f"The RDS instance may not have been created. To fix:\n"
            f"  1. Run: make rds-apply ENV={env}\n"
            f"  2. Or run: cd envs/{env}-rds && terraform apply\n"
            f"  3. Verify the RDS instance exists in AWS Console\n"
            f"  4. If the instance was deleted, check Terraform state with: terraform state list"
        )

        return HostnameValidationResult(
            success=False,
            ip_address=None,
            error_message=error_message,
            remediation=remediation
        )


def is_running_in_kubernetes() -> bool:
    """
    Detect if we're running inside a Kubernetes pod.

    Returns:
        True if running inside K8s, False otherwise
    """
    # K8s sets these environment variables in pods
    return (
        os.environ.get("KUBERNETES_SERVICE_HOST") is not None
        or os.path.exists("/var/run/secrets/kubernetes.io/serviceaccount/token")
    )


def run_preflight_checks(
    creds: "RdsCredentials",
    env: str = "dev",
    skip_preflight: bool = False
) -> PreflightCheckResult:
    """
    Run all pre-flight checks before attempting to provision.

    Checks:
    1. Hostname is resolvable (RDS instance exists)
    2. Port is reachable (network connectivity)

    Note: For private RDS (PubliclyAccessible=false), these checks only pass
    when running from inside the VPC (e.g., from within the EKS cluster).
    Use skip_preflight=True or --skip-preflight when running from outside.

    Args:
        creds: RDS credentials to validate
        env: Environment name for remediation messaging
        skip_preflight: Skip all pre-flight checks

    Returns:
        PreflightCheckResult with overall status and any failures
    """
    # Skip preflight if explicitly requested or running inside K8s
    if skip_preflight:
        logger.info("Pre-flight checks skipped (--skip-preflight flag)")
        return PreflightCheckResult(passed=True, failed_checks=[], remediation="")

    if is_running_in_kubernetes():
        logger.info("Pre-flight checks skipped (running inside Kubernetes)")
        return PreflightCheckResult(passed=True, failed_checks=[], remediation="")

    failed_checks: List[str] = []
    remediation_steps: List[str] = []

    # Check 1: Hostname resolution
    logger.info(f"Pre-flight check: Validating RDS hostname {creds.host}...")
    hostname_result = validate_rds_hostname(creds.host, env)

    if not hostname_result.success:
        # For private RDS, provide better guidance
        error_message = (
            f"Cannot resolve RDS hostname from this network.\n"
            f"  Hostname: {creds.host}\n"
            f"  This is expected if RDS is in a private subnet (PubliclyAccessible=false)."
        )
        failed_checks.append(error_message)
        remediation_steps.append(
            f"For private RDS, run provisioning from inside the cluster:\n"
            f"  1. Use: make rds-provision-k8s ENV={env}\n"
            f"  2. Or create a K8s Job to run provisioning inside the VPC\n"
            f"  3. Or use --skip-preflight if you know RDS is reachable"
        )
        return PreflightCheckResult(
            passed=False,
            failed_checks=failed_checks,
            remediation="\n".join(remediation_steps)
        )

    logger.info(f"Pre-flight check: Hostname resolved to {hostname_result.ip_address}")

    # Check 2: Port reachability
    logger.info(f"Pre-flight check: Testing port {creds.port} reachability...")
    try:
        conn = socket.create_connection(
            (creds.host, creds.port),
            timeout=10
        )
        conn.close()
        logger.info("Pre-flight check: Port is reachable")
    except socket.timeout:
        failed_checks.append(
            f"Port {creds.port} not reachable on {creds.host}: Connection timed out"
        )
        remediation_steps.append(
            f"Check security group rules allow inbound traffic on port {creds.port}\n"
            f"Verify the RDS instance is in an available state"
        )
    except socket.error as e:
        failed_checks.append(
            f"Port {creds.port} not reachable on {creds.host}: {e}"
        )
        remediation_steps.append(
            f"Check security group rules and network connectivity\n"
            f"Verify the RDS instance is in an available state"
        )

    return PreflightCheckResult(
        passed=len(failed_checks) == 0,
        failed_checks=failed_checks,
        remediation="\n".join(remediation_steps) if remediation_steps else ""
    )


# =============================================================================
# Secrets Manager Functions
# =============================================================================


def fetch_secret(secret_path: str, region: str = "eu-west-2") -> Dict[str, Any]:
    """
    Fetch secret from AWS Secrets Manager.

    Args:
        secret_path: The secret name/path in Secrets Manager
        region: AWS region

    Returns:
        Parsed JSON secret as dict

    Raises:
        RuntimeError: If secret cannot be fetched
    """
    try:
        import boto3
        from botocore.exceptions import ClientError
    except ImportError:
        raise RuntimeError("boto3 is required. Install with: pip install boto3")

    client = boto3.client("secretsmanager", region_name=region)

    try:
        response = client.get_secret_value(SecretId=secret_path)
        return json.loads(response["SecretString"])
    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code", "Unknown")
        if error_code == "ResourceNotFoundException":
            raise RuntimeError(f"Secret not found: {secret_path}")
        elif error_code == "AccessDeniedException":
            raise RuntimeError(f"Access denied to secret: {secret_path}")
        else:
            raise RuntimeError(f"Failed to fetch secret {secret_path}: {e}")


def parse_credentials(secret_dict: Dict[str, Any]) -> RdsCredentials:
    """Parse credentials from Secrets Manager secret."""
    required = ["host", "port", "username", "password", "dbname"]
    missing = [k for k in required if k not in secret_dict]
    if missing:
        raise ValueError(f"Secret missing required fields: {missing}")

    return RdsCredentials(
        host=secret_dict["host"],
        port=int(secret_dict["port"]),
        username=secret_dict["username"],
        password=secret_dict["password"],
        dbname=secret_dict["dbname"],
    )


# =============================================================================
# Terraform tfvars Parsing
# =============================================================================


def parse_tfvars(tfvars_path: str) -> List[AppDatabase]:
    """
    Parse application_databases from terraform.tfvars.

    Uses regex to extract the HCL map structure. For production use,
    consider using a proper HCL parser like python-hcl2.

    Args:
        tfvars_path: Path to terraform.tfvars file

    Returns:
        List of AppDatabase objects
    """
    path = Path(tfvars_path)
    if not path.exists():
        raise FileNotFoundError(f"tfvars file not found: {tfvars_path}")

    content = path.read_text()

    # Find application_databases block
    # Pattern matches: application_databases = { ... } including nested braces
    pattern = r"application_databases\s*=\s*\{([\s\S]*?)\n\}"
    match = re.search(pattern, content)

    if not match:
        logger.warning("No application_databases found in tfvars")
        return []

    block = match.group(1)
    databases: List[AppDatabase] = []

    # Parse each app entry - handles multiline HCL format
    # Pattern matches:
    #   app_name = {
    #     database_name = "..."
    #     username      = "..."
    #   }
    app_pattern = r'(\w+)\s*=\s*\{[^}]*database_name\s*=\s*"([^"]+)"[^}]*username\s*=\s*"([^"]+)"[^}]*\}'
    for app_match in re.finditer(app_pattern, block, re.DOTALL):
        app_name, db_name, username = app_match.groups()
        databases.append(
            AppDatabase(name=app_name, database_name=db_name, username=username)
        )

    return databases


# =============================================================================
# Database Connection
# =============================================================================


def connect_rds(creds: RdsCredentials):
    """
    Connect to PostgreSQL RDS with SSL required.

    Args:
        creds: RDS credentials

    Returns:
        psycopg2 connection object

    Raises:
        RuntimeError: If connection fails
    """
    try:
        import psycopg2
    except ImportError:
        raise RuntimeError(
            "psycopg2 is required. Install with: pip install psycopg2-binary"
        )

    try:
        conn = psycopg2.connect(
            host=creds.host,
            port=creds.port,
            user=creds.username,
            password=creds.password,
            database=creds.dbname,
            sslmode="require",
            connect_timeout=10,
        )
        conn.autocommit = True
        return conn
    except psycopg2.Error as e:
        raise RuntimeError(f"Failed to connect to RDS: {e}")


# =============================================================================
# Provisioning Functions
# =============================================================================


def provision_role(
    conn, username: str, password: str, dry_run: bool = False
) -> ProvisionResult:
    """
    Create or update PostgreSQL role idempotently.

    Roles are created with LOGIN and CREATEDB privileges. CREATEDB is required
    because applications like Backstage dynamically create plugin databases
    at startup (e.g., backstage_plugin_app, backstage_plugin_catalog).

    Args:
        conn: Database connection (can be None if dry_run=True)
        username: Role name
        password: Role password
        dry_run: If True, don't execute

    Returns:
        ProvisionResult with status
    """
    start_time = time.time()
    action = "create_role"

    if dry_run:
        message = f"[DRY-RUN] Would create/update role: {username} (with LOGIN CREATEDB)"
        logger.info(message)
        return ProvisionResult(
            database="",
            username=username,
            action=action,
            status="dry_run",
            duration_ms=int((time.time() - start_time) * 1000),
            message=message,
        )

    # Check if role exists
    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", (username,))
        role_exists = cur.fetchone() is not None

    try:
        with conn.cursor() as cur:
            if role_exists:
                # Update password and ensure CREATEDB for existing role
                cur.execute(
                    "ALTER ROLE %s WITH LOGIN CREATEDB PASSWORD %%s" % username, (password,)
                )
                message = f"Updated role with CREATEDB: {username}"
                status = "no_change"
            else:
                # Create new role with LOGIN and CREATEDB
                # CREATEDB required for apps that create plugin databases (e.g., Backstage)
                cur.execute(
                    "CREATE ROLE %s WITH LOGIN CREATEDB PASSWORD %%s" % username, (password,)
                )
                message = f"Created role with CREATEDB: {username}"
                status = "success"

        logger.info(f"[{status.upper()}] {message}")
        return ProvisionResult(
            database="",
            username=username,
            action=action,
            status=status,
            duration_ms=int((time.time() - start_time) * 1000),
            message=message,
        )

    except Exception as e:
        message = f"Failed to provision role {username}: {e}"
        logger.error(message)
        return ProvisionResult(
            database="",
            username=username,
            action=action,
            status="error",
            duration_ms=int((time.time() - start_time) * 1000),
            message=message,
        )


def provision_database(
    conn, db_name: str, owner: str, dry_run: bool = False
) -> ProvisionResult:
    """
    Create PostgreSQL database idempotently.

    Args:
        conn: Database connection (can be None if dry_run=True)
        db_name: Database name
        owner: Owner role name
        dry_run: If True, don't execute

    Returns:
        ProvisionResult with status
    """
    start_time = time.time()
    action = "create_database"

    if dry_run:
        message = f"[DRY-RUN] Would create database: {db_name} with owner {owner}"
        logger.info(message)
        return ProvisionResult(
            database=db_name,
            username=owner,
            action=action,
            status="dry_run",
            duration_ms=int((time.time() - start_time) * 1000),
            message=message,
        )

    # Check if database exists
    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
        db_exists = cur.fetchone() is not None

    try:
        if db_exists:
            # Check if owner matches
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT pg_catalog.pg_get_userbyid(d.datdba)
                    FROM pg_database d
                    WHERE d.datname = %s
                    """,
                    (db_name,),
                )
                current_owner = cur.fetchone()[0]

            if current_owner != owner:
                message = f"Database {db_name} exists but owner is {current_owner}, expected {owner}"
                logger.warning(message)
                return ProvisionResult(
                    database=db_name,
                    username=owner,
                    action=action,
                    status="warning",
                    duration_ms=int((time.time() - start_time) * 1000),
                    message=message,
                )
            else:
                message = f"Database already exists with correct owner: {db_name}"
                status = "no_change"
        else:
            # Create database
            # Note: CREATE DATABASE cannot be parameterized, use identifier quoting
            with conn.cursor() as cur:
                # Validate identifiers to prevent SQL injection
                if not re.match(r"^[a-z][a-z0-9_]*$", db_name):
                    raise ValueError(f"Invalid database name: {db_name}")
                if not re.match(r"^[a-z][a-z0-9_]*$", owner):
                    raise ValueError(f"Invalid owner name: {owner}")

                cur.execute(f'CREATE DATABASE "{db_name}" OWNER "{owner}"')
            message = f"Created database: {db_name} with owner {owner}"
            status = "success"

        logger.info(f"[{status.upper()}] {message}")
        return ProvisionResult(
            database=db_name,
            username=owner,
            action=action,
            status=status,
            duration_ms=int((time.time() - start_time) * 1000),
            message=message,
        )

    except Exception as e:
        message = f"Failed to provision database {db_name}: {e}"
        logger.error(message)
        return ProvisionResult(
            database=db_name,
            username=owner,
            action=action,
            status="error",
            duration_ms=int((time.time() - start_time) * 1000),
            message=message,
        )


def apply_grants(
    conn, db_name: str, username: str, access_level: str = "owner", dry_run: bool = False
) -> ProvisionResult:
    """
    Apply grants and default privileges for database access.

    Args:
        conn: Database connection (can be None if dry_run=True)
        db_name: Database name
        username: User to grant access to
        access_level: Access level (owner, editor, reader)
        dry_run: If True, don't execute

    Returns:
        ProvisionResult with status
    """
    start_time = time.time()
    action = "apply_grants"

    # Validate access level
    if access_level not in ACCESS_LEVELS:
        return ProvisionResult(
            database=db_name,
            username=username,
            action=action,
            status="error",
            duration_ms=int((time.time() - start_time) * 1000),
            message=f"Invalid access_level: {access_level}. Must be one of: {list(ACCESS_LEVELS.keys())}",
        )

    grants = ACCESS_LEVELS[access_level]

    if dry_run:
        message = f"[DRY-RUN] Would grant {access_level} access on {db_name} to {username}"
        logger.info(message)
        return ProvisionResult(
            database=db_name,
            username=username,
            action=action,
            status="dry_run",
            duration_ms=int((time.time() - start_time) * 1000),
            message=message,
        )

    try:
        # Validate identifiers
        if not re.match(r"^[a-z][a-z0-9_]*$", db_name):
            raise ValueError(f"Invalid database name: {db_name}")
        if not re.match(r"^[a-z][a-z0-9_]*$", username):
            raise ValueError(f"Invalid username: {username}")

        with conn.cursor() as cur:
            # Grant on database
            cur.execute(f'GRANT {grants["database"]} ON DATABASE "{db_name}" TO "{username}"')

            # Grant on schema (requires connecting to the target database)
            # For now, grant on public schema from current connection
            cur.execute(f'GRANT {grants["schema"]} ON SCHEMA public TO "{username}"')

            # Grant on existing tables and sequences
            cur.execute(f'GRANT {grants["tables"]} ON ALL TABLES IN SCHEMA public TO "{username}"')
            cur.execute(f'GRANT {grants["sequences"]} ON ALL SEQUENCES IN SCHEMA public TO "{username}"')

            # Set default privileges for future objects
            cur.execute(f'ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT {grants["default_tables"]} ON TABLES TO "{username}"')
            cur.execute(f'ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT {grants["default_sequences"]} ON SEQUENCES TO "{username}"')

        message = f"Granted {access_level} access on {db_name} to {username} (with default privileges)"
        logger.info(f"[SUCCESS] {message}")

        return ProvisionResult(
            database=db_name,
            username=username,
            action=action,
            status="success",
            duration_ms=int((time.time() - start_time) * 1000),
            message=message,
        )

    except Exception as e:
        message = f"Failed to apply grants on {db_name} to {username}: {e}"
        logger.error(message)
        return ProvisionResult(
            database=db_name,
            username=username,
            action=action,
            status="error",
            duration_ms=int((time.time() - start_time) * 1000),
            message=message,
        )


# =============================================================================
# Main Provisioning Logic
# =============================================================================


class ProvisionError(Exception):
    """Raised when provisioning fails and should abort."""

    pass


def provision_all(
    env: str,
    tfvars_path: str,
    master_secret_path: str,
    build_id: str,
    run_id: str,
    dry_run: bool = False,
    fail_fast: bool = True,
    region: str = "eu-west-2",
    audit_output_path: Optional[str] = None,
    skip_preflight: bool = False,
) -> List[AuditRecord]:
    """
    Provision all application databases.

    Args:
        env: Environment name (dev, staging, prod)
        tfvars_path: Path to terraform.tfvars
        master_secret_path: Secrets Manager path for master credentials
        build_id: Build ID for audit
        run_id: CI run ID for audit
        dry_run: If True, don't execute changes
        fail_fast: If True, exit on first error (PRD requirement)
        region: AWS region
        audit_output_path: Optional path to persist audit CSV
        skip_preflight: If True, skip pre-flight network checks

    Returns:
        List of audit records

    Raises:
        ProvisionError: If fail_fast=True and an error occurs
    """
    audit_records: List[AuditRecord] = []
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Parse application_databases
    logger.info(f"Parsing tfvars: {tfvars_path}")
    databases = parse_tfvars(tfvars_path)

    if not databases:
        logger.info("No application databases to provision")
        return audit_records

    logger.info(f"Found {len(databases)} application databases to provision")

    # Fetch master credentials
    if not dry_run:
        logger.info(f"Fetching master credentials from: {master_secret_path}")
        master_secret = fetch_secret(master_secret_path, region)
        master_creds = parse_credentials(master_secret)

        # Run pre-flight checks before attempting to connect
        logger.info("Running pre-flight checks...")
        preflight_result = run_preflight_checks(master_creds, env, skip_preflight)

        if not preflight_result.passed:
            logger.error("=" * 70)
            logger.error("PRE-FLIGHT CHECKS FAILED")
            logger.error("=" * 70)
            for check in preflight_result.failed_checks:
                logger.error(f"  FAILED: {check}")
            logger.error("")
            logger.error("REMEDIATION:")
            logger.error(preflight_result.remediation)
            logger.error("=" * 70)
            raise ProvisionError(
                f"Pre-flight checks failed: {'; '.join(preflight_result.failed_checks)}"
            )

        logger.info("Pre-flight checks passed")
        logger.info(f"Connecting to RDS: {master_creds.host}:{master_creds.port}")
        conn = connect_rds(master_creds)
    else:
        logger.info("[DRY-RUN] Skipping credential fetch and connection")
        conn = None

    def record_and_check(record: AuditRecord) -> None:
        """Record audit and check for fail-fast."""
        audit_records.append(record)
        if fail_fast and record.status == "error":
            # Persist audit before raising
            if audit_output_path:
                persist_audit_records(audit_records, audit_output_path)
            raise ProvisionError(f"Fail-fast triggered: {record.message}")

    # Provision each application database
    for app_db in databases:
        logger.info(f"\n--- Provisioning: {app_db.name} ---")

        # Fetch app-specific password from Secrets Manager
        app_secret_path = f"goldenpath/{env}/{app_db.name}/postgres"

        if not dry_run:
            try:
                app_secret = fetch_secret(app_secret_path, region)
                app_password = app_secret.get("password")
                if not app_password:
                    raise ValueError("Secret missing 'password' field")
            except Exception as e:
                error_msg = f"Failed to fetch app secret {app_secret_path}: {e}"
                logger.error(error_msg)
                record_and_check(
                    AuditRecord(
                        timestamp_utc=timestamp,
                        environment=env,
                        build_id=build_id,
                        run_id=run_id,
                        database=app_db.database_name,
                        username=app_db.username,
                        action="fetch_secret",
                        status="error",
                        duration_ms=0,
                        message=error_msg,
                    )
                )
                continue  # Only reached if fail_fast=False
        else:
            app_password = "DRY_RUN_PASSWORD"

        # 1. Provision role
        result = provision_role(conn, app_db.username, app_password, dry_run)
        record_and_check(
            AuditRecord(
                timestamp_utc=timestamp,
                environment=env,
                build_id=build_id,
                run_id=run_id,
                database=app_db.database_name,
                username=app_db.username,
                action=result.action,
                status=result.status,
                duration_ms=result.duration_ms,
                message=result.message,
            )
        )

        if result.status == "error":
            continue  # Only reached if fail_fast=False

        # 2. Provision database
        result = provision_database(conn, app_db.database_name, app_db.username, dry_run)
        record_and_check(
            AuditRecord(
                timestamp_utc=timestamp,
                environment=env,
                build_id=build_id,
                run_id=run_id,
                database=app_db.database_name,
                username=app_db.username,
                action=result.action,
                status=result.status,
                duration_ms=result.duration_ms,
                message=result.message,
            )
        )

        if result.status == "error":
            continue  # Only reached if fail_fast=False

        # 3. Apply grants with access level
        result = apply_grants(
            conn, app_db.database_name, app_db.username, app_db.access_level, dry_run
        )
        record_and_check(
            AuditRecord(
                timestamp_utc=timestamp,
                environment=env,
                build_id=build_id,
                run_id=run_id,
                database=app_db.database_name,
                username=app_db.username,
                action=result.action,
                status=result.status,
                duration_ms=result.duration_ms,
                message=result.message,
            )
        )

    # Close connection
    if conn:
        conn.close()
        logger.info("Connection closed")

    # Persist audit records to file if path provided
    if audit_output_path:
        persist_audit_records(audit_records, audit_output_path)

    return audit_records


def persist_audit_records(records: List[AuditRecord], output_path: str) -> None:
    """
    Persist audit records to a CSV file.

    Args:
        records: List of audit records
        output_path: Path to output CSV file
    """
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    # Check if file exists to determine if we need headers
    write_header = not path.exists()

    with path.open("a", encoding="utf-8") as f:
        if write_header:
            f.write(
                "timestamp_utc,environment,build_id,run_id,database,username,action,status,duration_ms,message\n"
            )
        for record in records:
            f.write(record.to_csv_row() + "\n")

    logger.info(f"Audit records persisted to: {output_path}")


def print_audit_summary(records: List[AuditRecord]) -> int:
    """Print audit summary and return exit code."""
    print("\n" + "=" * 70)
    print("AUDIT SUMMARY")
    print("=" * 70)

    # CSV header
    print(
        "timestamp_utc,environment,build_id,run_id,database,username,action,status,duration_ms,message"
    )
    for record in records:
        print(record.to_csv_row())

    print("=" * 70)

    # Count results
    success = sum(1 for r in records if r.status == "success")
    no_change = sum(1 for r in records if r.status == "no_change")
    errors = sum(1 for r in records if r.status == "error")
    dry_run = sum(1 for r in records if r.status == "dry_run")

    print(f"Success: {success}")
    print(f"No Change: {no_change}")
    print(f"Errors: {errors}")
    print(f"Dry Run: {dry_run}")
    print("=" * 70)

    return 1 if errors > 0 else 0


# =============================================================================
# CLI Interface
# =============================================================================


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="RDS User and Database Provisioning Script",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry run (no changes)
  python3 scripts/rds_provision.py --env dev --tfvars envs/dev-rds/terraform.tfvars --master-secret goldenpath/dev/rds/master --dry-run

  # Actual provisioning
  python3 scripts/rds_provision.py --env dev --tfvars envs/dev-rds/terraform.tfvars --master-secret goldenpath/dev/rds/master

  # With audit tracking
  python3 scripts/rds_provision.py --env dev --tfvars envs/dev-rds/terraform.tfvars --master-secret goldenpath/dev/rds/master --build-id 16-01-26-01 --run-id 12345678
        """,
    )

    parser.add_argument(
        "--env",
        required=True,
        choices=["dev", "test", "staging", "prod"],
        help="Environment name",
    )
    parser.add_argument(
        "--tfvars",
        required=True,
        help="Path to terraform.tfvars file",
    )
    parser.add_argument(
        "--master-secret",
        required=True,
        help="Secrets Manager path for master credentials",
    )
    parser.add_argument(
        "--build-id",
        default="manual",
        help="Build ID for audit trail (default: manual)",
    )
    parser.add_argument(
        "--run-id",
        default="local",
        help="CI run ID for audit trail (default: local)",
    )
    parser.add_argument(
        "--region",
        default="eu-west-2",
        help="AWS region (default: eu-west-2)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be done without executing",
    )
    parser.add_argument(
        "--require-approval",
        action="store_true",
        help="Require ALLOW_DB_PROVISION=true for non-dev environments",
    )
    parser.add_argument(
        "--audit-output",
        default=None,
        help="Path to persist audit CSV (e.g., governance/rds_provision_audit.csv)",
    )
    parser.add_argument(
        "--no-fail-fast",
        action="store_true",
        help="Continue on errors instead of failing fast (not recommended for prod)",
    )
    parser.add_argument(
        "--skip-preflight",
        action="store_true",
        help="Skip pre-flight checks (use when running from inside the VPC/cluster)",
    )

    return parser.parse_args()


def main() -> int:
    """Main entry point."""
    args = parse_args()

    # Check approval gate for non-dev environments
    if args.env != "dev" and args.require_approval:
        allow = os.environ.get("ALLOW_DB_PROVISION", "").lower()
        if allow != "true":
            logger.error(
                f"ALLOW_DB_PROVISION=true required for {args.env} environment"
            )
            return 1

    # Fail-fast is default; --no-fail-fast disables it
    fail_fast = not args.no_fail_fast

    logger.info("=" * 70)
    logger.info("RDS User and Database Provisioning")
    logger.info("=" * 70)
    logger.info(f"Environment: {args.env}")
    logger.info(f"tfvars: {args.tfvars}")
    logger.info(f"Master Secret: {args.master_secret}")
    logger.info(f"Build ID: {args.build_id}")
    logger.info(f"Run ID: {args.run_id}")
    logger.info(f"Region: {args.region}")
    logger.info(f"Dry Run: {args.dry_run}")
    logger.info(f"Fail Fast: {fail_fast}")
    logger.info(f"Skip Preflight: {args.skip_preflight}")
    logger.info(f"Audit Output: {args.audit_output or '(stdout only)'}")
    logger.info("=" * 70)

    try:
        records = provision_all(
            env=args.env,
            tfvars_path=args.tfvars,
            master_secret_path=args.master_secret,
            build_id=args.build_id,
            run_id=args.run_id,
            dry_run=args.dry_run,
            fail_fast=fail_fast,
            region=args.region,
            audit_output_path=args.audit_output,
            skip_preflight=args.skip_preflight,
        )

        return print_audit_summary(records)

    except ProvisionError as e:
        logger.error(f"Provisioning aborted (fail-fast): {e}")
        return 1

    except Exception as e:
        logger.error(f"Fatal error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
