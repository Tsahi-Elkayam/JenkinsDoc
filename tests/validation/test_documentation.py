"""
Validation tests for code documentation
Ensures all public functions and classes have docstrings
"""

import inspect
import os
import sys
import unittest
from unittest.mock import Mock

# Add tests directory to path for test_helpers
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from helpers import sublime_mock, sublime_plugin_mock

# Mock sublime before importing
sys.modules["sublime"] = sublime_mock
sys.modules["sublime_plugin"] = sublime_plugin_mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))

from modules import diagnostics, listeners, utils


class TestDocumentation(unittest.TestCase):
    """Test that all public classes and functions have docstrings"""

    def test_utils_module_has_docstring(self):
        """Test that utils module has docstring"""
        self.assertIsNotNone(utils.__doc__)

    def test_listeners_module_has_docstring(self):
        """Test that listeners module has docstring"""
        self.assertIsNotNone(listeners.__doc__)

    def test_diagnostics_module_has_docstring(self):
        """Test that diagnostics module has docstring"""
        self.assertIsNotNone(diagnostics.__doc__)

    def test_public_functions_have_docstrings(self):
        """Test that public functions have docstrings"""
        modules_to_check = [utils, listeners, diagnostics]

        for module in modules_to_check:
            for name, obj in inspect.getmembers(module):
                if inspect.isfunction(obj) and not name.startswith("_"):
                    self.assertIsNotNone(obj.__doc__, f"Function {module.__name__}.{name} missing docstring")

    def test_command_classes_have_docstrings(self):
        """Test that diagnostic command classes have docstrings"""
        command_classes = [
            diagnostics.JenkinsDocTestCompletionsCommand,
            diagnostics.JenkinsDocDiagnosticsCommand,
        ]

        for cls in command_classes:
            self.assertIsNotNone(cls.__doc__, f"Class {cls.__name__} missing docstring")
            self.assertTrue(cls.__doc__.strip())

    def test_listener_classes_have_docstrings(self):
        """Test that listener classes have docstrings"""
        listener_classes = [
            listeners.JenkinsDocStatusBar,
            listeners.JenkinsDocHoverCommand,
            listeners.JenkinsCompletions,
            listeners.JenkinsGoToDefinitionCommand,
        ]

        for cls in listener_classes:
            self.assertIsNotNone(cls.__doc__, f"Class {cls.__name__} missing docstring")


if __name__ == "__main__":
    unittest.main()
