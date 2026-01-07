import os
import sys
import shutil
import tempfile
import unittest
import yaml

# Add project root to path
sys.path.append(os.getcwd())
from scripts.lib.metadata_config import MetadataConfig

class TestMetadataInheritance(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.old_cwd = os.getcwd()
        os.chdir(self.test_dir)
        
        # Setup mock schemas and enums
        os.makedirs("schemas/metadata")
        with open("schemas/metadata/enums.yaml", "w") as f:
            yaml.dump({"owners": ["platform-team", "app-team"], "domains": ["delivery", "security"]}, f)
            
        with open("schemas/metadata/metadata.schema.yaml", "w") as f:
            yaml.dump({
                "properties": {
                    "owner": {"enum_from": "owners"},
                    "domain": {"enum_from": "domains"},
                    "exempt": {"type": "boolean"}
                }
            }, f)
            
        self.cfg = MetadataConfig(schemas_dir="schemas/metadata", enums_file="schemas/metadata/enums.yaml")

    def tearDown(self):
        os.chdir(self.old_cwd)
        shutil.rmtree(self.test_dir)

    def test_find_parent_metadata(self):
        # Create parent metadata
        os.makedirs("apps")
        parent_meta = {"owner": "platform-team", "domain": "delivery"}
        with open("apps/metadata.yaml", "w") as f:
            yaml.dump(parent_meta, f)
            
        # Create child dir
        os.makedirs("apps/my-service")
        child_file = "apps/my-service/info.md"
        
        found = self.cfg.find_parent_metadata(child_file)
        self.assertEqual(found["owner"], "platform-team")

    def test_get_effective_metadata_merging(self):
        # Parent
        os.makedirs("apps")
        with open("apps/metadata.yaml", "w") as f:
            yaml.dump({"owner": "platform-team", "domain": "delivery"}, f)
            
        # Child with override
        os.makedirs("apps/my-service")
        local_data = {"id": "MY_SERVICE", "domain": "security"}
        
        effective = self.cfg.get_effective_metadata("apps/my-service/metadata.yaml", local_data)
        
        self.assertEqual(effective["owner"], "platform-team") # Inherited
        self.assertEqual(effective["domain"], "security")     # Local Override
        self.assertEqual(effective["id"], "MY_SERVICE")      # Local Identity

    def test_id_never_inherited(self):
        # Parent with ID (bad practice but should be handled)
        os.makedirs("apps")
        with open("apps/metadata.yaml", "w") as f:
            yaml.dump({"id": "PARENT_ID", "owner": "platform-team"}, f)
            
        os.makedirs("apps/my-service")
        local_data = {"owner": "app-team"}
        
        effective = self.cfg.get_effective_metadata("apps/my-service/metadata.yaml", local_data)
        
        self.assertEqual(effective["owner"], "app-team")
        self.assertNotIn("id", effective) # ID should be stripped if not in local

if __name__ == "__main__":
    unittest.main()
