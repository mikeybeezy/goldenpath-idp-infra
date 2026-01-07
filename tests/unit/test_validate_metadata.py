import os
import sys
import tempfile
import unittest
import yaml

# Add project root to path
sys.path.append(os.getcwd())
from scripts.validate_metadata import verify_injection, extract_metadata, validate_schema

class TestMetadataValidation(unittest.TestCase):
    def setUp(self):
        """Create a temporary test directory"""
        self.test_dir = tempfile.mkdtemp()
        self.old_cwd = os.getcwd()
        os.chdir(self.test_dir)

        # Setup mock schemas
        os.makedirs('schemas/metadata')
        with open('schemas/metadata/enums.yaml', 'w') as f:
            yaml.dump({'owners': ['platform-team'], 'domains': ['delivery']}, f)

    def tearDown(self):
        """Clean up test directory"""
        os.chdir(self.old_cwd)
        import shutil
        shutil.rmtree(self.test_dir)

    def test_verify_injection_inline_pattern(self):
        """Test that verify_injection detects inline 'id:' pattern"""
        # Create test directory with metadata
        os.makedirs('test-dir')

        # Create a K8s manifest with inline ID
        with open('test-dir/deployment.yaml', 'w') as f:
            f.write("""
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
  labels:
    id: TEST_APP_ID
spec:
  replicas: 1
""")

        result = verify_injection('test-dir', 'TEST_APP_ID')
        self.assertTrue(result)

    def test_verify_injection_governance_block(self):
        """Test that verify_injection detects Helm values governance block"""
        # Create test directory with values file
        os.makedirs('test-dir')

        # Create Helm values file with governance block
        with open('test-dir/values.yaml', 'w') as f:
            f.write("""
myapp:
  replicas: 3
governance:
  id: HELM_APP_ID
  owner: platform-team
""")

        result = verify_injection('test-dir', 'HELM_APP_ID')
        self.assertTrue(result)

    def test_verify_injection_no_match(self):
        """Test that verify_injection returns False when ID not found in Helm chart"""
        os.makedirs('test-dir')

        # Create Chart.yaml to make it a Helm chart (required for injection)
        with open('test-dir/Chart.yaml', 'w') as f:
            f.write("name: test-chart\nversion: 1.0.0\n")

        # Create a values file without the expected ID
        with open('test-dir/values.yaml', 'w') as f:
            f.write("some: config\n")

        result = verify_injection('test-dir', 'MISSING_ID')
        self.assertFalse(result)

    def test_extract_metadata_yaml_file(self):
        """Test extracting metadata from standalone YAML file"""
        with open('test.yaml', 'w') as f:
            yaml.dump({'id': 'TEST_ID', 'owner': 'platform-team'}, f)

        data, error = extract_metadata('test.yaml')

        self.assertIsNone(error)
        self.assertEqual(data['id'], 'TEST_ID')
        self.assertEqual(data['owner'], 'platform-team')

    def test_extract_metadata_markdown_frontmatter(self):
        """Test extracting metadata from markdown frontmatter"""
        with open('test.md', 'w') as f:
            f.write("""---
id: DOC_ID
title: Test Document
owner: platform-team
---

# Content here
""")

        data, error = extract_metadata('test.md')

        self.assertIsNone(error)
        self.assertEqual(data['id'], 'DOC_ID')
        self.assertEqual(data['owner'], 'platform-team')

    def test_extract_metadata_missing_file(self):
        """Test that extract_metadata handles missing files gracefully"""
        data, error = extract_metadata('nonexistent.yaml')

        self.assertIsNone(data)
        self.assertIn('Read error', error)

    def test_extract_metadata_invalid_yaml(self):
        """Test that extract_metadata catches invalid YAML"""
        with open('bad.yaml', 'w') as f:
            f.write("invalid: yaml: content:\n  - broken\n   syntax")

        data, error = extract_metadata('bad.yaml')

        self.assertIsNone(data)
        self.assertIn('Invalid YAML', error)

if __name__ == '__main__':
    unittest.main()
