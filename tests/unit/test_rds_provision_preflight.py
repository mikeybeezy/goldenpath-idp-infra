"""
Tests for RDS provisioning pre-flight checks.

These tests validate that the rds_provision.py script properly validates
the RDS hostname is reachable BEFORE attempting to connect, providing
clear error messaging when the RDS instance doesn't exist.

TDD RED PHASE: These tests define the expected behavior.
"""

import socket
import pytest
from unittest.mock import patch, MagicMock


class TestRdsHostnameValidation:
    """Test pre-flight hostname validation."""

    def test_validate_hostname_success(self):
        """Hostname validation should succeed for resolvable hosts."""
        # Import the function we're going to implement
        from scripts.rds_provision import validate_rds_hostname

        # Mock socket.gethostbyname to return an IP
        with patch("socket.gethostbyname") as mock_dns:
            mock_dns.return_value = "10.0.1.100"

            result = validate_rds_hostname("valid-host.rds.amazonaws.com")

            assert result.success is True
            assert result.ip_address == "10.0.1.100"
            mock_dns.assert_called_once_with("valid-host.rds.amazonaws.com")

    def test_validate_hostname_failure_unresolvable(self):
        """Hostname validation should fail with clear message for unresolvable hosts."""
        from scripts.rds_provision import validate_rds_hostname

        # Mock socket.gethostbyname to raise an exception
        with patch("socket.gethostbyname") as mock_dns:
            mock_dns.side_effect = socket.gaierror(8, "nodename nor servname provided")

            result = validate_rds_hostname("nonexistent-host.rds.amazonaws.com")

            assert result.success is False
            assert "RDS instance does not exist" in result.error_message
            assert "nonexistent-host" in result.error_message

    def test_validate_hostname_provides_remediation_steps(self):
        """Validation failure should include remediation steps."""
        from scripts.rds_provision import validate_rds_hostname

        with patch("socket.gethostbyname") as mock_dns:
            mock_dns.side_effect = socket.gaierror(8, "nodename nor servname provided")

            result = validate_rds_hostname("nonexistent.rds.amazonaws.com")

            assert result.success is False
            # Should tell user how to fix the problem
            assert (
                "make rds-apply" in result.remediation
                or "terraform apply" in result.remediation
            )


class TestRdsPreflightCheck:
    """Test the complete pre-flight check before provisioning."""

    def test_preflight_check_runs_before_connect(self):
        """Pre-flight check should run before attempting database connection."""
        from scripts.rds_provision import run_preflight_checks, RdsCredentials

        creds = RdsCredentials(
            host="nonexistent.rds.amazonaws.com",
            port=5432,
            username="admin",
            password="secret",
            dbname="platform",
        )

        with patch("socket.gethostbyname") as mock_dns:
            mock_dns.side_effect = socket.gaierror(8, "nodename nor servname provided")

            result = run_preflight_checks(creds)

            assert result.passed is False
            assert "hostname" in result.failed_checks[0].lower()

    def test_preflight_check_validates_port_reachable(self):
        """Pre-flight should check if the RDS port is reachable."""
        from scripts.rds_provision import run_preflight_checks, RdsCredentials

        creds = RdsCredentials(
            host="existing.rds.amazonaws.com",
            port=5432,
            username="admin",
            password="secret",
            dbname="platform",
        )

        with (
            patch("socket.gethostbyname") as mock_dns,
            patch("socket.create_connection") as mock_conn,
        ):
            mock_dns.return_value = "10.0.1.100"
            mock_conn.side_effect = socket.timeout("Connection timed out")

            result = run_preflight_checks(creds)

            assert result.passed is False
            assert any(
                "port" in check.lower() or "reachable" in check.lower()
                for check in result.failed_checks
            )

    def test_preflight_check_success_allows_provisioning(self):
        """Successful pre-flight check should allow provisioning to proceed."""
        from scripts.rds_provision import run_preflight_checks, RdsCredentials

        creds = RdsCredentials(
            host="valid.rds.amazonaws.com",
            port=5432,
            username="admin",
            password="secret",
            dbname="platform",
        )

        with (
            patch("socket.gethostbyname") as mock_dns,
            patch("socket.create_connection") as mock_conn,
        ):
            mock_dns.return_value = "10.0.1.100"
            mock_conn.return_value = MagicMock()

            result = run_preflight_checks(creds)

            assert result.passed is True
            assert len(result.failed_checks) == 0


class TestProvisionAllWithPreflight:
    """Test that provision_all uses pre-flight checks."""

    def test_provision_all_fails_fast_on_preflight_failure(self):
        """provision_all should fail fast if pre-flight checks fail."""
        from scripts.rds_provision import provision_all, ProvisionError

        with (
            patch("scripts.rds_provision.fetch_secret") as mock_secret,
            patch("scripts.rds_provision.run_preflight_checks") as mock_preflight,
        ):
            mock_secret.return_value = {
                "host": "nonexistent.rds.amazonaws.com",
                "port": "5432",
                "username": "admin",
                "password": "secret",
                "dbname": "platform",
            }

            # Mock preflight to fail
            mock_result = MagicMock()
            mock_result.passed = False
            mock_result.failed_checks = [
                "Hostname unresolvable: RDS instance does not exist"
            ]
            mock_result.remediation = "Run: make rds-apply ENV=dev"
            mock_preflight.return_value = mock_result

            with pytest.raises(ProvisionError) as exc_info:
                provision_all(
                    env="dev",
                    tfvars_path="envs/dev-rds/terraform.tfvars",
                    master_secret_path="goldenpath/dev/rds/master",
                    build_id="test",
                    run_id="test",
                    dry_run=False,
                )

            assert "preflight" in str(exc_info.value).lower() or "RDS" in str(
                exc_info.value
            )

    def test_provision_all_logs_remediation_on_preflight_failure(self):
        """provision_all should log remediation steps when pre-flight fails."""
        from scripts.rds_provision import provision_all, ProvisionError

        with (
            patch("scripts.rds_provision.fetch_secret") as mock_secret,
            patch("scripts.rds_provision.run_preflight_checks") as mock_preflight,
            patch("scripts.rds_provision.logger") as mock_logger,
        ):
            mock_secret.return_value = {
                "host": "nonexistent.rds.amazonaws.com",
                "port": "5432",
                "username": "admin",
                "password": "secret",
                "dbname": "platform",
            }

            mock_result = MagicMock()
            mock_result.passed = False
            mock_result.failed_checks = ["Hostname unresolvable"]
            mock_result.remediation = "Run: make rds-apply ENV=dev"
            mock_preflight.return_value = mock_result

            try:
                provision_all(
                    env="dev",
                    tfvars_path="envs/dev-rds/terraform.tfvars",
                    master_secret_path="goldenpath/dev/rds/master",
                    build_id="test",
                    run_id="test",
                    dry_run=False,
                )
            except ProvisionError:
                pass

            # Should have logged the remediation
            error_calls = [str(call) for call in mock_logger.error.call_args_list]
            assert any(
                "rds-apply" in call.lower() or "remediation" in call.lower()
                for call in error_calls
            )


class TestErrorMessageClarity:
    """Test that error messages are clear and actionable."""

    def test_dns_failure_message_mentions_rds_not_exists(self):
        """DNS failure should clearly state RDS instance doesn't exist."""
        from scripts.rds_provision import validate_rds_hostname

        with patch("socket.gethostbyname") as mock_dns:
            mock_dns.side_effect = socket.gaierror(8, "nodename nor servname provided")

            result = validate_rds_hostname(
                "goldenpath-dev-platform-dev.xyz.rds.amazonaws.com"
            )

            # Message should be clear, not just "DNS failed"
            assert (
                "RDS instance does not exist" in result.error_message
                or "RDS not found" in result.error_message
                or "does not exist" in result.error_message
            )

    def test_dns_failure_message_includes_hostname(self):
        """DNS failure should include the failing hostname for debugging."""
        from scripts.rds_provision import validate_rds_hostname

        with patch("socket.gethostbyname") as mock_dns:
            mock_dns.side_effect = socket.gaierror(8, "nodename nor servname provided")

            result = validate_rds_hostname(
                "goldenpath-dev-platform-dev.xyz.rds.amazonaws.com"
            )

            assert "goldenpath-dev-platform-dev" in result.error_message

    def test_remediation_includes_specific_env(self):
        """Remediation should include environment-specific commands."""
        from scripts.rds_provision import validate_rds_hostname

        with patch("socket.gethostbyname") as mock_dns:
            mock_dns.side_effect = socket.gaierror(8, "nodename nor servname provided")

            # For dev environment
            result = validate_rds_hostname(
                "goldenpath-dev-platform-dev.xyz.rds.amazonaws.com", env="dev"
            )

            assert "dev" in result.remediation.lower()
