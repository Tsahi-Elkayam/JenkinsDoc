"""
Integration tests for file detection functionality
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


class TestFileDetection(unittest.TestCase):
    """Test file type detection logic"""

    def setUp(self):
        """Set up mock settings"""
        self.settings = Mock()
        self.settings.get = Mock(side_effect=self._get_setting)

        self.settings_dict = {
            'detect_jenkinsfile': True,
            'detect_groovy_files': True,
            'additional_file_patterns': []
        }
        utils.set_settings(self.settings)

    def _get_setting(self, key, default=None):
        """Mock settings.get()"""
        return self.settings_dict.get(key, default)

    def test_jenkinsfile_detection(self):
        """Test detection of Jenkinsfile"""
        view = Mock()
        view.file_name = Mock(return_value='/path/to/Jenkinsfile')
        # Mock syntax to return None (file name detection will still work)
        view.syntax = Mock(return_value=None)

        result = utils.is_jenkins_file(view, self.settings)
        self.assertTrue(result)

    def test_groovy_file_detection(self):
        """Test detection of .groovy files"""
        view = Mock()
        view.file_name = Mock(return_value='/path/to/test.groovy')
        # Mock syntax with groovy scope
        syntax_mock = Mock()
        syntax_mock.scope = 'source.groovy'
        view.syntax = Mock(return_value=syntax_mock)

        result = utils.is_jenkins_file(view, self.settings)
        self.assertTrue(result)

    def test_jenkinsfile_with_extension(self):
        """Test detection of Jenkinsfile.production"""
        view = Mock()
        view.file_name = Mock(return_value='/path/to/Jenkinsfile.production')
        view.syntax = Mock(return_value=None)

        result = utils.is_jenkins_file(view, self.settings)
        self.assertTrue(result)

    def test_non_jenkins_file(self):
        """Test that non-Jenkins files are not detected"""
        view = Mock()
        view.file_name = Mock(return_value='/path/to/test.py')
        # Mock syntax with python scope (not groovy)
        syntax_mock = Mock()
        syntax_mock.scope = 'source.python'
        view.syntax = Mock(return_value=syntax_mock)

        result = utils.is_jenkins_file(view, self.settings)
        self.assertFalse(result)

    def test_additional_patterns(self):
        """Test custom file patterns"""
        self.settings_dict['additional_file_patterns'] = ['*.jenkins']

        view = Mock()
        view.file_name = Mock(return_value='/path/to/test.jenkins')
        view.syntax = Mock(return_value=None)

        result = utils.is_jenkins_file(view, self.settings)
        self.assertTrue(result)

    def test_detection_disabled(self):
        """Test when detection is disabled"""
        self.settings_dict['detect_jenkinsfile'] = False
        self.settings_dict['detect_groovy_files'] = False

        view = Mock()
        view.file_name = Mock(return_value='/path/to/Jenkinsfile')
        view.syntax = Mock(return_value=None)

        result = utils.is_jenkins_file(view, self.settings)
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
