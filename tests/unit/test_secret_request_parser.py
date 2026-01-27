# Owner: platform
# Description: Unit tests for the SecretRequest parser and policy enforcement engine.
import os
import sys
import unittest
from pathlib import Path

# Add project root to path
sys.path.append(os.getcwd())

from scripts.secret_request_parser import (
    SecretRequest,
    parse_request,
    validate_enums,
    generate_externalsecret,
)


class TestSecretRequestParser(unittest.TestCase):
    """
    Tests for SecretRequest Parser logic and policy enforcement.
    Standard: AAA (Arrange, Act, Assert)
    """

    def setUp(self):
        # Sample enums for validation
        self.enums = {
            "secretType": ["database-credentials", "api-key"],
            "riskTier": ["low", "medium", "high"],
            "rotationClass": ["none", "standard", "high"],
            "lifecycleStatus": ["active"],
        }
        self.dummy_path = Path("test_request.yaml")

    def test_parse_request_valid_camelCase(self):
        """Test happy path for camelCase manifest parsing."""
        # Arrange
        doc = {
            "id": "SEC-TEST",
            "metadata": {
                "name": "test-secret",
                "service": "test",
                "environment": "dev",
                "owner": "platform",
            },
            "spec": {
                "provider": "aws-secrets-manager",
                "secretType": "database-credentials",
                "risk": {"tier": "medium"},
                "rotation": {"rotationClass": "standard"},
                "lifecycle": {"status": "active"},
                "access": {"namespace": "test", "k8sSecretName": "test-creds"},
                "ttlDays": 30,
            },
        }

        # Act
        req = parse_request(doc, self.dummy_path)

        # Assert
        self.assertEqual(req.secret_id, "SEC-TEST")
        self.assertEqual(req.secretType, "database-credentials")
        self.assertEqual(req.rotationClass, "standard")
        self.assertEqual(req.k8sSecretName, "test-creds")

    def test_v1_policy_gate_high_risk_blocks_none_rotation(self):
        """Verify that high risk secrets require rotation != 'none'."""
        # Arrange
        req = SecretRequest(
            secret_id="SEC-0001",
            name="vault",
            service="core",
            environment="prod",
            owner="sec",
            secretType="api-key",
            riskTier="high",
            rotationClass="none",
            lifecycleStatus="active",
            namespace="core",
            k8sSecretName="vault-key",
            provider="aws-secrets-manager",
        )

        # Act & Assert
        with self.assertRaisesRegex(
            ValueError, "riskTier=high requires rotationClass != 'none'"
        ):
            validate_enums(req, self.enums, self.dummy_path)

    def test_generate_externalsecret_contains_correct_mapping(self):
        """Test that generated ExternalSecret has correct IRSA and key mapping."""
        # Arrange
        req = SecretRequest(
            secret_id="SEC-007",
            name="db",
            service="app",
            environment="dev",
            owner="team",
            secretType="db-creds",
            riskTier="low",
            rotationClass="standard",
            lifecycleStatus="active",
            namespace="app",
            k8sSecretName="db-secret",
            provider="aws-secrets-manager",
        )

        # Act
        es = generate_externalsecret(req)

        # Assert
        self.assertEqual(es["spec"]["target"]["name"], "db-secret")
        self.assertEqual(
            es["spec"]["dataFrom"][0]["extract"]["key"], "goldenpath/dev/app/db"
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
