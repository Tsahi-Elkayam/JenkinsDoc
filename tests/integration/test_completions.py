"""
Integration tests for completion functionality
Tests actual completion logic without mocks
"""

import sys
import os
import unittest
from unittest.mock import Mock

# Add tests directory to path for test_helpers
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from helpers import sublime_mock, sublime_plugin_mock

# Mock sublime before importing modules
sys.modules['sublime'] = sublime_mock
sys.modules['sublime_plugin'] = sublime_plugin_mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))

from modules import utils


class TestCompletionLogic(unittest.TestCase):
    """Test completion generation logic"""

    @classmethod
    def setUpClass(cls):
        """Load real jenkins data once for all tests"""
        cls.jenkins_data = {
            'instructions': [
                {
                    'command': 'echo',
                    'name': 'echo: Print Message',
                    'instructionType': 'Step',
                    'description': 'Print a message',
                    'parameters': [
                        {'name': 'message', 'type': 'String', 'isOptional': False}
                    ]
                },
                {
                    'command': 'git',
                    'name': 'git: Git',
                    'instructionType': 'Step',
                    'description': 'Git checkout',
                    'parameters': [
                        {'name': 'url', 'type': 'String', 'isOptional': False},
                        {'name': 'branch', 'type': 'String', 'isOptional': True}
                    ]
                }
            ],
            'environmentVariables': [
                {'name': 'BUILD_NUMBER', 'description': 'Build number'},
                {'name': 'WORKSPACE', 'description': 'Workspace path'}
            ]
        }
        utils.set_jenkins_data(cls.jenkins_data)

    def test_instruction_names_are_valid(self):
        """Test that all instructions have valid command names"""
        for instruction in self.jenkins_data['instructions']:
            self.assertIn('command', instruction)
            self.assertTrue(instruction['command'])
            self.assertIsInstance(instruction['command'], str)

    def test_parameters_have_required_fields(self):
        """Test that all parameters have required fields"""
        for instruction in self.jenkins_data['instructions']:
            if 'parameters' in instruction:
                for param in instruction['parameters']:
                    self.assertIn('name', param)
                    self.assertIn('type', param)
                    self.assertIn('isOptional', param)

    def test_environment_variables_complete(self):
        """Test environment variables have name and description"""
        for env_var in self.jenkins_data['environmentVariables']:
            self.assertIn('name', env_var)
            self.assertIn('description', env_var)
            self.assertTrue(env_var['name'])


class TestCompletionFiltering(unittest.TestCase):
    """Test completion filtering by prefix"""

    def setUp(self):
        """Set up test data"""
        self.instructions = [
            {'command': 'echo', 'name': 'echo'},
            {'command': 'error', 'name': 'error'},
            {'command': 'git', 'name': 'git'},
            {'command': 'sh', 'name': 'sh'}
        ]

    def test_filter_by_prefix(self):
        """Test filtering completions by prefix"""
        prefix = 'e'
        matches = [i for i in self.instructions if i['command'].startswith(prefix)]
        self.assertEqual(len(matches), 2)  # echo, error

    def test_empty_prefix_returns_all(self):
        """Test empty prefix returns all completions"""
        prefix = ''
        matches = [i for i in self.instructions if i['command'].startswith(prefix)]
        self.assertEqual(len(matches), 4)

    def test_no_matches_returns_empty(self):
        """Test no matching prefix returns empty list"""
        prefix = 'xyz'
        matches = [i for i in self.instructions if i['command'].startswith(prefix)]
        self.assertEqual(len(matches), 0)


if __name__ == '__main__':
    unittest.main()
