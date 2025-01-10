import unittest
import sys
import os
# Add the parent directory to Python's path so we can import modules from there.
# This is needed because the test file is in a subdirectory (tests/) but needs to import
# from the parent directory's classes/ folder. Without this, Python wouldn't find the imports.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the Tataru and FFXIVItem classes from the parent directory's classes/ folder.
from classes.tataru import Tataru
from classes.ffxivitem import FFXIVItem 

class TestTataru(unittest.TestCase):

    def setUp(self):
        print("\nSetting up Tataru test instance...")
        self.tataru = Tataru(config_path='config.ini', testing_mode=True)

    def test_internal_variables(self):
        print("\nTesting internal variables...")
        self.assertIsNotNone(self.tataru.ROLE_ID)  # Corrected attribute name
        print("✓ ROLE_ID exists")
        self.assertIsNotNone(self.tataru.SERVER_NAME)  # Corrected attribute name
        print("✓ SERVER_NAME exists") 
        self.assertIsNotNone(self.tataru.TOKEN)  # Corrected attribute name
        print("✓ TOKEN exists")
        self.assertIsNotNone(self.tataru.csvdb)
        print("✓ CSVDB exists")

    def test_csvdb(self):
        print("\nTesting CSVDB functionality...")
        # Check if csvdb can load worlds
        worlds = self.tataru.csvdb.load_worlds()
        self.assertIsInstance(worlds, dict)
        self.assertGreater(len(worlds), 0)
        print(f"✓ Loaded {len(worlds)} worlds successfully")

        # Check if we can get item 10335
        print("\nTesting item lookup by ID...")
        item = self.tataru.csvdb.search_item_by_id(10335)
        self.assertIsNotNone(item)
        self.assertEqual(item.item_id, 10335)
        print(f"✓ Found item {item.item_name} (ID: {item.item_id})")

        # Check if we can search for an item by name "Magitek Repair Materials"
        print("\nTesting item lookup by name...")
        item = self.tataru.csvdb.search_item_by_name("Magitek Repair Materials")
        self.assertIsNotNone(item)
        self.assertEqual(item.item_name, "Magitek Repair Materials")
        print(f"✓ Found item {item.item_name} by name search")

    def test_ffxivitem(self):
        print("\nTesting FFXIVItem class...")
        # Create a sample FFXIVItem
        print("Creating test item...")
        item = FFXIVItem(
            item_name="Magitek Repair Materials",
            item_id=10335,
            emoji="🔧",
            category="Crafting Material",
            icon_url="https://xivapi.com/i/000000/000000.png"
        )

        # Check if the item properties are set correctly
        print("Testing basic item properties...")
        self.assertEqual(item.item_name, "Magitek Repair Materials")
        self.assertEqual(item.item_id, 10335)
        self.assertEqual(item.emoji, "🔧")
        self.assertEqual(item.category, "Crafting Material")
        self.assertEqual(item.icon_url, "https://xivapi.com/i/000000/000000.png")
        print("✓ All basic properties set correctly")

        # Check if the auto_fill_info_from_xivapi method works correctly for STABLE format
        print("\nTesting STABLE format XIVAPI response...")
        stable_result = {
            "ID": 10335,
            "Name": "Magitek Repair Materials",
            "ItemUICategory": {"Name": "Crafting Material"},
            "Icon": "/i/000000/000000.png"
        }
        item.auto_fill_info_from_xivapi(stable_result)
        self.assertEqual(item.item_id, 10335)
        self.assertEqual(item.item_name, "Magitek Repair Materials")
        self.assertEqual(item.category, "Crafting Material")
        self.assertEqual(item.icon_url, "https://xivapi.com/i/000000/000000.png")
        self.assertEqual(item.emoji, "🛠️")
        print("✓ STABLE format handled correctly")

        # Check if the auto_fill_info_from_xivapi method works correctly for BETA format
        print("\nTesting BETA format XIVAPI response...")
        beta_result = {
            "row_id": 10335,
            "fields": {
                "Name": "Magitek Repair Materials",
                "ItemSearchCategory": {"fields": {"Name": "Crafting Material"}},
                "Icon": {"path": "i/000000/000000.png"}
            }
        }
        item.auto_fill_info_from_xivapi(beta_result)
        self.assertEqual(item.item_id, 10335)
        self.assertEqual(item.item_name, "Magitek Repair Materials")
        self.assertEqual(item.category, "Crafting Material")
        self.assertEqual(item.icon_url, "https://beta.xivapi.com/api/1/asset/i/000000/000000.png?format=png")
        self.assertEqual(item.emoji, "🛠️")
        print("✓ BETA format handled correctly")

    def test_run(self):
        print("\nTesting Tataru run method...")
        # This is a stub test method for the run method of Tataru class
        self.assertIsNotNone(self.tataru.run)
        print("✓ Run method exists")

if __name__ == '__main__':
    unittest.main()
