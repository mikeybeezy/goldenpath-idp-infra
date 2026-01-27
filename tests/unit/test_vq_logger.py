import os
import sys
import unittest

# Add project root to path
sys.path.append(os.getcwd())
from scripts.lib.vq_logger import get_total_reclaimed_hours, get_script_value


class TestVQLogger(unittest.TestCase):
    """
    Tests for VQ Logger functionality.
    Note: These tests use the actual .goldenpath/value_ledger.json file
    since vq_logger uses REPO_ROOT absolute paths.
    """

    def test_get_total_reclaimed_hours_returns_number(self):
        """Test that get_total_reclaimed_hours returns a numeric value"""
        total = get_total_reclaimed_hours()
        self.assertIsInstance(total, (int, float))
        self.assertGreaterEqual(total, 0.0)

    def test_get_script_value_handles_missing_file(self):
        """Test that get_script_value handles missing metadata gracefully"""
        vq = get_script_value("nonexistent_script_xyz.py")
        self.assertIsInstance(vq, (int, float))
        # Should return a default value (either 0.0 or 1.0)
        self.assertIn(vq, [0.0, 1.0])

    def test_get_script_value_with_existing_script(self):
        """Test that get_script_value can read metadata from an actual script"""
        # Use a known script that has VQ metadata
        vq = get_script_value("standardize_metadata.py")
        self.assertIsInstance(vq, (int, float))
        self.assertGreaterEqual(vq, 0.0)


if __name__ == "__main__":
    unittest.main()
