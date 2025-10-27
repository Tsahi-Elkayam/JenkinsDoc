"""
Unit tests for JenkinsDoc plugin
"""

import os
import sys
import unittest
from unittest.mock import MagicMock, Mock, mock_open, patch

# Add tests directory to path for test_helpers
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from helpers import setup_sublime_mocks, sublime_mock, sublime_plugin_mock

# Add the plugin's directory to the Python path (go up from unit/ -> tests/ -> plugin root)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))

# Mock Sublime Text modules before importing plugin code
sys.modules["sublime"] = sublime_mock
sys.modules["sublime_plugin"] = sublime_plugin_mock

# Now import the modules we want to test
from modules import utils


class TestLoadJenkinsData(unittest.TestCase):
    """Test the load_jenkins_data function"""

    def setUp(self):
        """Set up test fixtures"""
        self.settings = Mock()
        self.settings.get.return_value = "jenkins_data.json"

    def test_load_valid_json(self):
        """Test loading valid JSON data"""
        mock_data = {
            "plugins": ["plugin1", "plugin2"],
            "instructions": [{"command": "echo", "name": "Echo"}],
            "sections": [],
            "directives": [],
            "environmentVariables": [],
        }

        mock_json = __import__("json").dumps(mock_data)

        with patch("builtins.open", mock_open(read_data=mock_json)):
            data = utils.load_jenkins_data(self.settings)
            self.assertIsNotNone(data)
            self.assertEqual(len(data["plugins"]), 2)
            self.assertEqual(len(data["instructions"]), 1)

    def test_load_missing_file(self):
        """Test handling of missing data file"""
        with patch("builtins.open", side_effect=FileNotFoundError):
            data = utils.load_jenkins_data(self.settings)
            # Should return empty structure instead of crashing
            self.assertIsNotNone(data)
            self.assertIn("plugins", data)
            self.assertIn("instructions", data)
            self.assertEqual(len(data["plugins"]), 0)

    def test_load_invalid_json(self):
        """Test handling of invalid JSON"""
        with patch("builtins.open", mock_open(read_data="invalid json {")):
            data = utils.load_jenkins_data(self.settings)
            # Should return empty structure instead of crashing
            self.assertIsNotNone(data)
            self.assertIn("plugins", data)


class TestIsJenkinsFile(unittest.TestCase):
    """Test the is_jenkins_file function"""

    def setUp(self):
        """Set up a mock view and settings for each test"""
        self.view = Mock()
        self.settings = Mock()

        # Default settings
        self.settings.get.side_effect = self.default_settings

    def default_settings(self, key, default=None):
        """Default settings mock"""
        return {
            "enabled": True,
            "detect_groovy_files": True,
            "detect_jenkinsfile": True,
            "additional_file_patterns": [],
        }.get(key, default)

    def test_groovy_file_by_syntax(self):
        """Test that a file with Groovy syntax is detected"""
        syntax_mock = Mock()
        syntax_mock.scope = "source.groovy"
        self.view.syntax.return_value = syntax_mock
        self.view.file_name.return_value = "my_file.txt"  # Name shouldn't matter

        self.assertTrue(utils.is_jenkins_file(self.view, self.settings))

    def test_jenkinsfile_by_name(self):
        """Test that a file named Jenkinsfile is detected"""
        self.view.syntax.return_value = None  # Syntax shouldn't matter
        self.view.file_name.return_value = "/path/to/Jenkinsfile"

        self.assertTrue(utils.is_jenkins_file(self.view, self.settings))

    def test_jenkinsfile_with_extension(self):
        """Test that Jenkinsfile.groovy is detected"""
        self.view.syntax.return_value = None
        self.view.file_name.return_value = "/path/to/Jenkinsfile.groovy"

        self.assertTrue(utils.is_jenkins_file(self.view, self.settings))

    def test_jenkinsfile_with_suffix(self):
        """Test that Jenkinsfile.dev is detected"""
        self.view.syntax.return_value = None
        self.view.file_name.return_value = "/path/to/Jenkinsfile.dev"

        self.assertTrue(utils.is_jenkins_file(self.view, self.settings))

    def test_additional_pattern_match(self):
        """Test detection by additional user-defined patterns"""
        self.settings.get.side_effect = lambda key, default=None: {
            "enabled": True,
            "detect_groovy_files": False,
            "detect_jenkinsfile": False,
            "additional_file_patterns": ["*.jenkins", "*.pipeline"],
        }.get(key, default)

        self.view.syntax.return_value = None
        self.view.file_name.return_value = "/path/to/my_pipeline.jenkins"

        self.assertTrue(utils.is_jenkins_file(self.view, self.settings))

    def test_not_jenkins_file(self):
        """Test that a regular file is not detected"""
        self.view.syntax.return_value = None
        self.view.file_name.return_value = "/path/to/regular_file.txt"

        self.assertFalse(utils.is_jenkins_file(self.view, self.settings))

    def test_plugin_disabled(self):
        """Test that no file is detected when the plugin is disabled"""
        self.settings.get.side_effect = lambda key, default=None: {"enabled": False}.get(key, default)

        syntax_mock = Mock()
        syntax_mock.scope = "source.groovy"
        self.view.syntax.return_value = syntax_mock
        self.view.file_name.return_value = "Jenkinsfile"

        self.assertFalse(utils.is_jenkins_file(self.view, self.settings))

    def test_groovy_detection_disabled(self):
        """Test that Groovy files are not detected when detection is disabled"""
        self.settings.get.side_effect = lambda key, default=None: {
            "enabled": True,
            "detect_groovy_files": False,
            "detect_jenkinsfile": True,
            "additional_file_patterns": [],
        }.get(key, default)

        syntax_mock = Mock()
        syntax_mock.scope = "source.groovy"
        self.view.syntax.return_value = syntax_mock
        self.view.file_name.return_value = "/path/to/script.groovy"

        self.assertFalse(utils.is_jenkins_file(self.view, self.settings))

    def test_jenkinsfile_detection_disabled(self):
        """Test that Jenkinsfile is not detected when detection is disabled"""
        self.settings.get.side_effect = lambda key, default=None: {
            "enabled": True,
            "detect_groovy_files": False,
            "detect_jenkinsfile": False,
            "additional_file_patterns": [],
        }.get(key, default)

        self.view.syntax.return_value = None
        self.view.file_name.return_value = "/path/to/Jenkinsfile"

        self.assertFalse(utils.is_jenkins_file(self.view, self.settings))


class TestDataGettersSetter(unittest.TestCase):
    """Test the getter and setter functions for jenkins_data and settings"""

    def test_set_and_get_jenkins_data(self):
        """Test setting and getting jenkins data"""
        test_data = {"plugins": ["test"], "instructions": []}
        utils.set_jenkins_data(test_data)
        retrieved_data = utils.get_jenkins_data()
        self.assertEqual(retrieved_data, test_data)

    def test_set_and_get_settings(self):
        """Test setting and getting settings"""
        test_settings = Mock()
        test_settings.get.return_value = True
        utils.set_settings(test_settings)
        retrieved_settings = utils.get_settings()
        self.assertEqual(retrieved_settings, test_settings)

    def test_get_jenkins_data_initially_none(self):
        """Test that jenkins_data is initially None"""
        # Reset to None
        utils.set_jenkins_data(None)
        data = utils.get_jenkins_data()
        self.assertIsNone(data)

    def test_get_settings_initially_none(self):
        """Test that settings is initially None"""
        # Reset to None
        utils.set_settings(None)
        settings = utils.get_settings()
        self.assertIsNone(settings)


class TestIntegration(unittest.TestCase):
    """Integration tests for the plugin"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_data = {
            "plugins": [{"name": "Pipeline", "url": "http://example.com"}],
            "instructions": [
                {
                    "command": "echo",
                    "name": "Echo",
                    "description": "Print a message",
                    "parameters": [],
                    "url": "http://example.com/echo",
                },
                {
                    "command": "sh",
                    "name": "Shell Script",
                    "description": "Execute a shell script",
                    "parameters": [{"name": "script", "type": "String", "description": "The script to execute"}],
                    "url": "http://example.com/sh",
                },
            ],
            "sections": [
                {"name": "pipeline", "description": "Declarative Pipeline"},
                {"name": "stage", "description": "Define a stage"},
            ],
            "directives": [{"name": "agent", "description": "Specify where to run"}],
            "environmentVariables": [
                {"name": "BUILD_NUMBER", "description": "The current build number"},
                {"name": "JOB_NAME", "description": "Name of the job"},
            ],
        }

    def test_data_structure_completeness(self):
        """Test that loaded data has all required fields"""
        utils.set_jenkins_data(self.mock_data)
        data = utils.get_jenkins_data()

        self.assertIn("plugins", data)
        self.assertIn("instructions", data)
        self.assertIn("sections", data)
        self.assertIn("directives", data)
        self.assertIn("environmentVariables", data)

    def test_instruction_data_completeness(self):
        """Test that instructions have all required fields"""
        utils.set_jenkins_data(self.mock_data)
        data = utils.get_jenkins_data()

        for instruction in data["instructions"]:
            self.assertIn("command", instruction)
            self.assertIn("name", instruction)
            self.assertIn("description", instruction)
            self.assertIn("parameters", instruction)

    def test_multiple_file_patterns(self):
        """Test that multiple additional file patterns work"""
        settings = Mock()
        settings.get.side_effect = lambda key, default=None: {
            "enabled": True,
            "detect_groovy_files": False,
            "detect_jenkinsfile": False,
            "additional_file_patterns": ["*.jenkins", "*.pipeline", "Jenkinsfile.*"],
        }.get(key, default)

        view = Mock()
        view.syntax.return_value = None

        # Test each pattern
        test_files = ["/path/to/build.jenkins", "/path/to/deploy.pipeline", "/path/to/Jenkinsfile.production"]

        for file_path in test_files:
            view.file_name.return_value = file_path
            self.assertTrue(utils.is_jenkins_file(view, settings), f"Failed to detect {file_path}")


if __name__ == "__main__":
    # Run tests with verbose output
    unittest.main(verbosity=2)
