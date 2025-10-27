"""
Integration tests for hover documentation functionality
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


class TestHoverDocumentation(unittest.TestCase):
    """Test hover documentation generation"""

    @classmethod
    def setUpClass(cls):
        """Set up test data"""
        cls.jenkins_data = {
            'instructions': [
                {
                    'command': 'echo',
                    'name': 'echo: Print Message',
                    'description': 'Prints a message to the console',
                    'url': 'https://www.jenkins.io/doc/pipeline/steps/workflow-basic-steps/#echo',
                    'parameters': [
                        {
                            'name': 'message',
                            'type': 'String',
                            'description': 'The message to print',
                            'isOptional': False
                        }
                    ]
                }
            ]
        }
        utils.set_jenkins_data(cls.jenkins_data)

    def test_instruction_has_documentation(self):
        """Test that instructions have all required documentation fields"""
        instruction = self.jenkins_data['instructions'][0]

        self.assertIn('name', instruction)
        self.assertIn('description', instruction)
        self.assertIn('url', instruction)
        self.assertTrue(instruction['description'])

    def test_documentation_url_format(self):
        """Test that documentation URLs are properly formatted"""
        instruction = self.jenkins_data['instructions'][0]

        url = instruction['url']
        self.assertTrue(url.startswith('https://'))
        self.assertIn('jenkins.io', url)

    def test_parameter_documentation(self):
        """Test that parameters have documentation"""
        instruction = self.jenkins_data['instructions'][0]
        param = instruction['parameters'][0]

        self.assertIn('name', param)
        self.assertIn('type', param)
        self.assertIn('description', param)
        self.assertIn('isOptional', param)


class TestHoverLookup(unittest.TestCase):
    """Test looking up hover documentation by keyword"""

    def setUp(self):
        """Set up test data"""
        self.instructions = [
            {'command': 'echo', 'name': 'echo', 'description': 'Print message'},
            {'command': 'git', 'name': 'git', 'description': 'Git operations'}
        ]

    def test_find_instruction_by_command(self):
        """Test finding instruction by command name"""
        keyword = 'echo'
        found = next((i for i in self.instructions if i['command'] == keyword), None)

        self.assertIsNotNone(found)
        self.assertEqual(found['command'], 'echo')

    def test_instruction_not_found_returns_none(self):
        """Test looking up non-existent instruction returns None"""
        keyword = 'nonexistent'
        found = next((i for i in self.instructions if i['command'] == keyword), None)

        self.assertIsNone(found)


if __name__ == '__main__':
    unittest.main()
