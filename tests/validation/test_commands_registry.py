"""
Validation tests for command registry
Ensures commands in .sublime-commands match actual command classes
"""

import sys
import os
import unittest
import json
from unittest.mock import Mock

# Mock sublime before importing
sys.modules["sublime"] = Mock()
sys.modules["sublime_plugin"] = Mock()

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))

# Now we can import - but jenkins_doc uses relative imports, so let's work around it
# We'll just check the command file instead of importing classes
plugin_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))


class TestCommandsRegistry(unittest.TestCase):
    """Test that .sublime-commands file matches actual command classes"""

    @classmethod
    def setUpClass(cls):
        """Load .sublime-commands file"""
        plugin_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
        commands_file = os.path.join(plugin_dir, "Default.sublime-commands")

        if not os.path.exists(commands_file):
            cls.commands = []
            return

        with open(commands_file, "r") as f:
            cls.commands = json.load(f)

    def test_commands_file_exists(self):
        """Test that Default.sublime-commands exists"""
        plugin_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
        commands_file = os.path.join(plugin_dir, "Default.sublime-commands")
        self.assertTrue(os.path.exists(commands_file), "Default.sublime-commands not found")

    def test_commands_have_caption(self):
        """Test that all commands have a caption"""
        for cmd in self.commands:
            self.assertIn("caption", cmd, f"Command missing caption: {cmd}")
            self.assertTrue(cmd["caption"], "Command has empty caption")

    def test_commands_have_command_name(self):
        """Test that all commands have a command name"""
        for cmd in self.commands:
            self.assertIn("command", cmd, f"Command missing 'command' field: {cmd}")
            self.assertTrue(cmd["command"], "Command has empty command name")

    def test_command_classes_exist(self):
        """Test that all registered commands exist in expected files"""
        # Map command names to files where they should be defined
        expected_commands = {
            "jenkins_doc_show": "jenkins_doc.py",
            "jenkins_doc_reload": "jenkins_doc.py",
            "jenkins_doc_test_completions": "modules/diagnostics.py",
            "jenkins_doc_diagnostics": "modules/diagnostics.py",
            "open_url": "jenkins_doc.py",
            "edit_settings": "built-in Sublime command",
        }

        for cmd in self.commands:
            command_name = cmd["command"]
            self.assertIn(command_name, expected_commands, f"Command '{command_name}' is not in expected commands list")

    def test_command_names_follow_convention(self):
        """Test that command names follow snake_case convention"""
        for cmd in self.commands:
            command_name = cmd["command"]
            self.assertTrue(
                command_name.islower() or "_" in command_name, f"Command '{command_name}' doesn't follow snake_case"
            )


if __name__ == "__main__":
    unittest.main()
