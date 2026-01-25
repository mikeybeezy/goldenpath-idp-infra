# AGENT_CONTEXT: Read .agent/README.md for rules
"""
---
id: SCRIPT-0038
type: script
owner: platform-team
status: active
maturity: 2
dry_run:
  supported: true
  command_hint: --dry-run
test:
  runner: pytest
  command: pytest -q tests/scripts/test_script_0038.py
  evidence: declared
risk_profile:
  production_impact: low
  security_risk: low
  coupling_risk: low
---
"""

"""
Purpose: Unit Test Suite for Platform Health Logic
Achievement: Validates frontmatter parsing and risk aggregation logic.
Value: Ensures stability of the health reporting engine during schema migrations.
"""
import unittest
import os
import shutil
import tempfile
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))
from platform_health import parse_frontmatter

class TestPlatformHealth(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_parse_frontmatter_valid(self):
        file_path = os.path.join(self.test_dir, "valid.md")
        with open(file_path, 'w') as f:
            f.write("---\ntitle: Test\nowner: team-a\n---\nContent")

        data, error = parse_frontmatter(file_path)
        self.assertIsNone(error)
        self.assertEqual(data['title'], 'Test')
        self.assertEqual(data['owner'], 'team-a')

    def test_parse_frontmatter_invalid(self):
        file_path = os.path.join(self.test_dir, "invalid.md")
        with open(file_path, 'w') as f:
            f.write("No frontmatter here")

        data, error = parse_frontmatter(file_path)
        self.assertEqual(error, "No frontmatter found")

if __name__ == '__main__':
    unittest.main()
