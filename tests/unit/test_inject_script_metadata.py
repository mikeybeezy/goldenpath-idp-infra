#!/usr/bin/env python3
"""
Unit tests for logic in scripts/inject_script_metadata.py
"""

import unittest
import tempfile
import shutil
from pathlib import Path

# Import the module under test
# We need to add scripts/ to path
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "../../scripts"))
import inject_script_metadata


class TestInjector(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.root = Path(self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_inject_py_preserves_shebang(self):
        """Ensure #! remains on line 1"""
        p = self.root / "script_with_shebang.py"
        original_content = '#!/usr/bin/env python3\nprint("Hello")\n'
        p.write_text(original_content, encoding="utf-8")

        meta = {
            "id": "TEST-001",
            "type": "script",
            "owner": "test",
            "maturity": 1,
            "dry_run": {"supported": True},
            "test": {
                "runner": "pytest",
                "command": "echo test",
                "evidence": "declared",
            },
            "risk_profile": {"production_impact": "low"},
        }

        # Run injection
        inject_script_metadata.inject_py(p, meta)

        lines = p.read_text().splitlines()
        self.assertEqual(
            lines[0], "#!/usr/bin/env python3", "Shebang must be first line"
        )
        self.assertTrue(
            lines[1].startswith('"""'), "Metadata block should start on line 2"
        )
        self.assertIn(
            'print("Hello")', p.read_text(), "Original code must be preserved"
        )

    def test_inject_py_no_shebang(self):
        """Ensure metadata is at top if no shebang"""
        p = self.root / "plain.py"
        p.write_text("import os\n", encoding="utf-8")

        meta = {"id": "TEST-002", "risk_profile": {"production_impact": "low"}}
        inject_script_metadata.inject_py(p, meta)

        content = p.read_text()
        self.assertTrue(
            content.startswith('"""\n---'), "Metadata should be at very top"
        )

    def test_id_allocation(self):
        """Test registry increments"""
        reg = {"next": 10, "map": {}}
        sid = inject_script_metadata.alloc_id(reg, "scripts/foo.py")
        self.assertEqual(sid, "SCRIPT-0010")
        self.assertEqual(reg["next"], 11)
        self.assertEqual(reg["map"]["scripts/foo.py"], "SCRIPT-0010")

        # Idempotency
        sid2 = inject_script_metadata.alloc_id(reg, "scripts/foo.py")
        self.assertEqual(sid2, "SCRIPT-0010", "Should return existing ID")
        self.assertEqual(reg["next"], 11, "Should not increment")


if __name__ == "__main__":
    unittest.main()
