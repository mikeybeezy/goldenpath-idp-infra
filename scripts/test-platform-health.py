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
