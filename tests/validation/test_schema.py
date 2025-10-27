"""
Validation tests for settings schema
Ensures settings file is valid JSON with expected structure
"""

import sys
import os
import unittest
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))


class TestSettingsSchema(unittest.TestCase):
    """Test that JenkinsDoc.sublime-settings is valid"""

    @classmethod
    def setUpClass(cls):
        """Load settings file"""
        plugin_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
        settings_file = os.path.join(plugin_dir, "JenkinsDoc.sublime-settings")

        if not os.path.exists(settings_file):
            cls.settings = {}
            return

        with open(settings_file, "r") as f:
            # Remove comments and trailing commas for JSON parsing
            content = f.read()
            lines = []
            for line in content.split("\n"):
                # Skip lines that start with //
                stripped = line.strip()
                if stripped.startswith("//"):
                    continue
                # Remove inline // comments
                if "//" in line:
                    line = line.split("//")[0].rstrip()
                # Remove trailing commas before closing braces/brackets
                line = line.rstrip()
                if line.endswith(",}"):
                    line = line[:-2] + "}"
                elif line.endswith(",]"):
                    line = line[:-2] + "]"
                if line.strip():
                    lines.append(line)
            content = "\n".join(lines)
            cls.settings = json.loads(content)

    def test_settings_file_exists(self):
        """Test that JenkinsDoc.sublime-settings exists"""
        plugin_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
        settings_file = os.path.join(plugin_dir, "JenkinsDoc.sublime-settings")
        self.assertTrue(os.path.exists(settings_file), "JenkinsDoc.sublime-settings not found")

    def test_settings_have_enabled_flag(self):
        """Test that settings have 'enabled' flag"""
        self.assertIn("enabled", self.settings)
        self.assertIsInstance(self.settings["enabled"], bool)

    def test_settings_have_autocompletion_flag(self):
        """Test that settings have 'enable_autocompletion' flag"""
        self.assertIn("enable_autocompletion", self.settings)
        self.assertIsInstance(self.settings["enable_autocompletion"], bool)

    def test_settings_have_hover_docs_flag(self):
        """Test that settings have 'show_hover_docs' flag"""
        self.assertIn("show_hover_docs", self.settings)
        self.assertIsInstance(self.settings["show_hover_docs"], bool)

    def test_settings_have_valid_types(self):
        """Test that all settings have valid types"""
        expected_types = {
            "enabled": bool,
            "show_status_bar": bool,
            "show_hover_docs": bool,
            "enable_autocompletion": bool,
            "detect_jenkinsfile": bool,
            "detect_groovy_files": bool,
            "additional_file_patterns": list,
        }

        for key, expected_type in expected_types.items():
            if key in self.settings:
                self.assertIsInstance(
                    self.settings[key], expected_type, f"Setting '{key}' should be {expected_type.__name__}"
                )


if __name__ == "__main__":
    unittest.main()
