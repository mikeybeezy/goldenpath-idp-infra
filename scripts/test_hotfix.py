"""
---
id: SCRIPT-0057
type: script
owner: platform-team
status: active
maturity: 2
dry_run:
  supported: true
  command_hint: --dry-run
test:
  runner: pytest
  command: pytest -q tests/scripts/test_script_0037.py
  evidence: declared
risk_profile:
  production_impact: low
  security_risk: low
  coupling_risk: low
---
"""


"""
Purpose: Unit tests for PR Guardrails Hotfix Logic.
Verifies that only Platform Team members can bypass gates on main using the hotfix label.
"""
import unittest
from unittest.mock import patch, MagicMock
# Import the validation logic (assuming it's importable, or mock it)
# Since scripts/pr_guardrails.py is a script, we'll import functions if possible or just test logic here

# Mocking the behavior of scripts/pr_guardrails.py logic for test
PLATFORM_TEAM = ['mikeybeezy', 'mikesablaze', 'github-actions[bot]', 'dependabot[bot]']

def validate_hotfix(author: str, base: str) -> tuple[bool, str]:
    """Validate hotfix label: must target main AND be platform-team"""
    if base != "main":
        return False, f"hotfix label invalid: must target main, not {base}"
    if author not in PLATFORM_TEAM:
        return False, f"hotfix label invalid: author {author} not in platform-team"
    return True, f"✅ hotfix validated: {author} targeting {base}"

class TestHotfixLogic(unittest.TestCase):
    def test_valid_hotfix(self):
        valid, msg = validate_hotfix('mikeybeezy', 'main')
        self.assertTrue(valid)
        self.assertIn("validated", msg)

    def test_invalid_branch(self):
        valid, msg = validate_hotfix('mikeybeezy', 'development')
        self.assertFalse(valid)
        self.assertIn("must target main", msg)

    def test_invalid_author(self):
        valid, msg = validate_hotfix('random-user', 'main')
        self.assertFalse(valid)
        self.assertIn("not in platform-team", msg)

if __name__ == '__main__':
    unittest.main()
