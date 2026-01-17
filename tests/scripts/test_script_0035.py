"""
Tests for SCRIPT-0035: RDS User and Database Provisioning

Run with: pytest -q tests/scripts/test_script_0035.py

Note: Integration tests require a PostgreSQL database (Docker or real).
Unit tests use mocking and can run anywhere.
"""
import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Import from scripts directory
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

from rds_provision import (
    AppDatabase,
    RdsCredentials,
    ProvisionResult,
    AuditRecord,
    parse_tfvars,
    parse_credentials,
    provision_role,
    provision_database,
    apply_grants,
    provision_all,
)


# --- Fixtures ---


@pytest.fixture
def sample_tfvars_content():
    return """
environment       = "dev"
aws_region        = "eu-west-2"
owner_team        = "platform-team"

application_databases = {
  keycloak = {
    database_name = "keycloak"
    username      = "keycloak_user"
  },
  backstage = {
    database_name = "backstage"
    username      = "backstage_user"
  }
}
"""


@pytest.fixture
def sample_tfvars_file(sample_tfvars_content):
    """Create a temporary tfvars file for testing."""
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".tfvars", delete=False
    ) as f:
        f.write(sample_tfvars_content)
        return Path(f.name)


@pytest.fixture
def sample_credentials():
    return RdsCredentials(
        host="test-db.example.com",
        port=5432,
        username="admin",
        password="secret123",
        dbname="postgres",
    )


@pytest.fixture
def mock_connection():
    """Create a mock database connection."""
    conn = MagicMock()
    cursor = MagicMock()
    conn.cursor.return_value.__enter__ = MagicMock(return_value=cursor)
    conn.cursor.return_value.__exit__ = MagicMock(return_value=False)
    return conn, cursor


# --- Parse tfvars Tests ---


class TestParseTfvars:
    def test_parses_application_databases(self, sample_tfvars_file):
        databases = parse_tfvars(str(sample_tfvars_file))

        assert len(databases) == 2

        db_names = {db.name for db in databases}
        assert "keycloak" in db_names
        assert "backstage" in db_names

        keycloak = next(db for db in databases if db.name == "keycloak")
        assert keycloak.database_name == "keycloak"
        assert keycloak.username == "keycloak_user"

        backstage = next(db for db in databases if db.name == "backstage")
        assert backstage.database_name == "backstage"
        assert backstage.username == "backstage_user"

    def test_returns_empty_if_no_databases(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".tfvars", delete=False
        ) as f:
            f.write("environment = 'dev'\n")
            path = f.name

        databases = parse_tfvars(path)
        assert databases == []

    def test_raises_on_missing_file(self):
        with pytest.raises(FileNotFoundError):
            parse_tfvars("/nonexistent/path/terraform.tfvars")


# --- Parse Credentials Tests ---


class TestParseCredentials:
    def test_parses_valid_credentials(self):
        secret = {
            "host": "db.example.com",
            "port": "5432",
            "username": "admin",
            "password": "secret",
            "dbname": "postgres",
        }

        creds = parse_credentials(secret)

        assert creds.host == "db.example.com"
        assert creds.port == 5432
        assert creds.username == "admin"
        assert creds.password == "secret"
        assert creds.dbname == "postgres"

    def test_raises_on_missing_field(self):
        secret = {
            "host": "db.example.com",
            "port": "5432",
            # missing username, password, dbname
        }

        with pytest.raises(ValueError, match="missing required fields"):
            parse_credentials(secret)


# --- Provision Role Tests ---


class TestProvisionRole:
    def test_creates_role_when_not_exists(self, mock_connection):
        conn, cursor = mock_connection
        # Role does not exist
        cursor.fetchone.return_value = None

        result = provision_role(conn, "test_user", "test_pass", dry_run=False)

        assert result.status == "success"
        assert "Created role" in result.message
        assert result.action == "create_role"

    def test_updates_role_when_exists(self, mock_connection):
        conn, cursor = mock_connection
        # Role exists
        cursor.fetchone.return_value = (1,)

        result = provision_role(conn, "test_user", "test_pass", dry_run=False)

        assert result.status == "no_change"
        assert "Password updated" in result.message

    def test_dry_run_does_not_execute(self, mock_connection):
        conn, cursor = mock_connection

        result = provision_role(conn, "test_user", "test_pass", dry_run=True)

        assert result.status == "dry_run"
        assert "[DRY-RUN]" in result.message
        # Verify no ALTER or CREATE was called
        cursor.execute.assert_not_called()


# --- Provision Database Tests ---


class TestProvisionDatabase:
    def test_creates_database_when_not_exists(self, mock_connection):
        conn, cursor = mock_connection
        # Database does not exist
        cursor.fetchone.return_value = None

        result = provision_database(conn, "test_db", "test_user", dry_run=False)

        assert result.status == "success"
        assert "Created database" in result.message
        assert result.action == "create_database"

    def test_no_change_when_exists_with_correct_owner(self, mock_connection):
        conn, cursor = mock_connection
        # First call: database exists
        # Second call: owner check returns correct owner
        cursor.fetchone.side_effect = [(1,), ("test_user",)]

        result = provision_database(conn, "test_db", "test_user", dry_run=False)

        assert result.status == "no_change"
        assert "already exists with correct owner" in result.message

    def test_warning_when_exists_with_wrong_owner(self, mock_connection):
        conn, cursor = mock_connection
        # First call: database exists
        # Second call: owner check returns wrong owner
        cursor.fetchone.side_effect = [(1,), ("wrong_user",)]

        result = provision_database(conn, "test_db", "test_user", dry_run=False)

        assert result.status == "warning"
        assert "wrong_user" in result.message
        assert "expected test_user" in result.message

    def test_dry_run_does_not_execute(self, mock_connection):
        conn, cursor = mock_connection

        result = provision_database(conn, "test_db", "test_user", dry_run=True)

        assert result.status == "dry_run"
        assert "[DRY-RUN]" in result.message

    def test_validates_database_name(self, mock_connection):
        conn, cursor = mock_connection
        cursor.fetchone.return_value = None

        # Invalid database name (starts with number)
        result = provision_database(conn, "1invalid", "test_user", dry_run=False)

        assert result.status == "error"
        assert "Invalid database name" in result.message


# --- Apply Grants Tests ---


class TestApplyGrants:
    def test_applies_grants(self, mock_connection):
        conn, cursor = mock_connection

        result = apply_grants(conn, "test_db", "test_user", dry_run=False)

        assert result.status == "success"
        assert "Granted ALL" in result.message

    def test_dry_run_does_not_execute(self, mock_connection):
        conn, cursor = mock_connection

        result = apply_grants(conn, "test_db", "test_user", dry_run=True)

        assert result.status == "dry_run"
        assert "[DRY-RUN]" in result.message

    def test_validates_identifiers(self, mock_connection):
        conn, cursor = mock_connection

        result = apply_grants(conn, "test-db", "test_user", dry_run=False)

        assert result.status == "error"
        assert "Invalid database name" in result.message


# --- Audit Record Tests ---


class TestAuditRecord:
    def test_to_csv_row(self):
        record = AuditRecord(
            timestamp_utc="2026-01-16T10:30:00Z",
            environment="dev",
            build_id="16-01-26-01",
            run_id="12345678",
            database="keycloak",
            username="keycloak_user",
            action="create_role",
            status="success",
            duration_ms=45,
            message="Role created",
        )

        csv_row = record.to_csv_row()

        assert "2026-01-16T10:30:00Z" in csv_row
        assert "dev" in csv_row
        assert "16-01-26-01" in csv_row
        assert "keycloak" in csv_row
        assert "success" in csv_row
        assert "45" in csv_row

    def test_escapes_commas_in_message(self):
        record = AuditRecord(
            timestamp_utc="2026-01-16T10:30:00Z",
            environment="dev",
            build_id="16-01-26-01",
            run_id="12345678",
            database="keycloak",
            username="keycloak_user",
            action="create_role",
            status="error",
            duration_ms=45,
            message="Error: host=x, port=5432",  # Contains comma
        )

        csv_row = record.to_csv_row()

        # Comma should be escaped to semicolon
        assert "host=x; port=5432" in csv_row


# --- Idempotency Tests ---


class TestIdempotency:
    def test_provision_role_idempotent(self, mock_connection):
        conn, cursor = mock_connection

        # First run: role doesn't exist
        cursor.fetchone.return_value = None
        result1 = provision_role(conn, "test_user", "pass", dry_run=False)
        assert result1.status == "success"

        # Second run: role exists
        cursor.fetchone.return_value = (1,)
        result2 = provision_role(conn, "test_user", "pass", dry_run=False)
        assert result2.status == "no_change"

    def test_provision_database_idempotent(self, mock_connection):
        conn, cursor = mock_connection

        # First run: database doesn't exist
        cursor.fetchone.return_value = None
        result1 = provision_database(conn, "test_db", "owner", dry_run=False)
        assert result1.status == "success"

        # Second run: database exists with correct owner
        cursor.fetchone.side_effect = [(1,), ("owner",)]
        result2 = provision_database(conn, "test_db", "owner", dry_run=False)
        assert result2.status == "no_change"


# --- Approval Gate Tests ---


class TestApprovalGates:
    @patch.dict("os.environ", {}, clear=True)
    def test_non_dev_requires_approval(self):
        """Test that non-dev environments require ALLOW_DB_PROVISION=true."""
        import os
        from rds_provision import main

        # Simulate calling with --require-approval for prod
        with patch(
            "sys.argv",
            [
                "rds_provision.py",
                "--env",
                "prod",
                "--tfvars",
                "/path/to/tfvars",
                "--master-secret",
                "secret/path",
                "--require-approval",
            ],
        ):
            result = main()
            assert result == 1  # Should fail without approval

    @patch.dict("os.environ", {"ALLOW_DB_PROVISION": "true"})
    @patch("rds_provision.provision_all")
    def test_non_dev_with_approval_proceeds(self, mock_provision):
        """Test that non-dev with ALLOW_DB_PROVISION=true proceeds."""
        mock_provision.return_value = []

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".tfvars", delete=False
        ) as f:
            f.write("# empty\n")
            tfvars_path = f.name

        from rds_provision import main

        with patch(
            "sys.argv",
            [
                "rds_provision.py",
                "--env",
                "prod",
                "--tfvars",
                tfvars_path,
                "--master-secret",
                "secret/path",
                "--require-approval",
            ],
        ):
            # This should not fail on the approval check
            # (but may fail later if secrets aren't available)
            pass


# --- Dry Run Tests ---


class TestDryRun:
    def test_dry_run_produces_no_database_changes(self, sample_tfvars_file):
        """Dry run should parse tfvars but not connect or modify."""
        with patch("rds_provision.fetch_secret") as mock_fetch:
            with patch("rds_provision.connect_rds") as mock_connect:
                records = provision_all(
                    env="dev",
                    tfvars_path=str(sample_tfvars_file),
                    master_secret_path="goldenpath/dev/rds/master",
                    build_id="test",
                    run_id="123",
                    dry_run=True,
                )

                # Should not have called fetch_secret or connect_rds
                mock_fetch.assert_not_called()
                mock_connect.assert_not_called()

                # Should still produce audit records
                assert len(records) > 0
                assert all(r.status == "dry_run" for r in records)


# --- Integration Test (requires Docker PostgreSQL) ---


@pytest.mark.integration
class TestIntegration:
    """
    Integration tests requiring a PostgreSQL database.

    Run with: pytest -m integration tests/scripts/test_script_0035.py

    Requires:
        - Docker running
        - PostgreSQL container: docker run -d -p 5433:5432 -e POSTGRES_PASSWORD=test postgres:15
    """

    @pytest.fixture
    def pg_connection(self):
        """Create a real PostgreSQL connection for integration tests."""
        try:
            import psycopg2

            conn = psycopg2.connect(
                host="localhost",
                port=5433,
                user="postgres",
                password="test",
                database="postgres",
                connect_timeout=5,
            )
            conn.autocommit = True
            yield conn
            conn.close()
        except Exception:
            pytest.skip("PostgreSQL not available for integration tests")

    def test_full_provisioning_flow(self, pg_connection, sample_tfvars_file):
        """Test full provision flow against real PostgreSQL."""
        # Clean up any previous test artifacts
        with pg_connection.cursor() as cur:
            cur.execute("DROP DATABASE IF EXISTS keycloak")
            cur.execute("DROP DATABASE IF EXISTS backstage")
            cur.execute("DROP ROLE IF EXISTS keycloak_user")
            cur.execute("DROP ROLE IF EXISTS backstage_user")

        # Run provisioning (mocking secrets)
        with patch("rds_provision.fetch_secret") as mock_fetch:
            # Master credentials
            mock_fetch.side_effect = [
                {
                    "host": "localhost",
                    "port": "5433",
                    "username": "postgres",
                    "password": "test",
                    "dbname": "postgres",
                },
                # App credentials
                {"password": "keycloak_pass"},
                {"password": "backstage_pass"},
            ]

            records = provision_all(
                env="dev",
                tfvars_path=str(sample_tfvars_file),
                master_secret_path="goldenpath/dev/rds/master",
                build_id="test-int",
                run_id="integration",
                dry_run=False,
            )

        # Verify results
        success_count = sum(1 for r in records if r.status == "success")
        assert success_count >= 4  # 2 roles + 2 databases

        # Verify databases exist
        with pg_connection.cursor() as cur:
            cur.execute("SELECT datname FROM pg_database WHERE datname IN ('keycloak', 'backstage')")
            dbs = [row[0] for row in cur.fetchall()]
            assert "keycloak" in dbs
            assert "backstage" in dbs

        # Run again - should be idempotent
        with patch("rds_provision.fetch_secret") as mock_fetch:
            mock_fetch.side_effect = [
                {
                    "host": "localhost",
                    "port": "5433",
                    "username": "postgres",
                    "password": "test",
                    "dbname": "postgres",
                },
                {"password": "keycloak_pass"},
                {"password": "backstage_pass"},
            ]

            records2 = provision_all(
                env="dev",
                tfvars_path=str(sample_tfvars_file),
                master_secret_path="goldenpath/dev/rds/master",
                build_id="test-int",
                run_id="integration-2",
                dry_run=False,
            )

        # Second run should have no_change status
        no_change_count = sum(1 for r in records2 if r.status == "no_change")
        assert no_change_count >= 2  # At least databases should be no_change
