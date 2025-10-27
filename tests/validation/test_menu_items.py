"""
Validation tests for menu items
Ensures menu items reference valid commands
"""

import sys
import os
import unittest
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))


class TestMenuItems(unittest.TestCase):
    """Test that Main.sublime-menu references valid commands"""

    @classmethod
    def setUpClass(cls):
        """Load Main.sublime-menu file"""
        plugin_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
        menu_file = os.path.join(plugin_dir, "Main.sublime-menu")

        if not os.path.exists(menu_file):
            cls.menu_items = []
            return

        with open(menu_file, "r") as f:
            cls.menu_items = json.load(f)

    def test_menu_file_exists(self):
        """Test that Main.sublime-menu exists"""
        plugin_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
        menu_file = os.path.join(plugin_dir, "Main.sublime-menu")
        self.assertTrue(os.path.exists(menu_file), "Main.sublime-menu not found")

    def test_menu_is_valid_json(self):
        """Test that menu file is valid JSON"""
        self.assertIsInstance(self.menu_items, list, "Menu file should be a JSON array")

    def test_menu_items_have_required_fields(self):
        """Test that menu items have required fields"""

        def check_item(item):
            if "children" in item:
                for child in item["children"]:
                    check_item(child)
            if "command" in item:
                self.assertIsInstance(item["command"], str)
                self.assertTrue(item["command"], "Menu item has empty command")

        for item in self.menu_items:
            check_item(item)


if __name__ == "__main__":
    unittest.main()
