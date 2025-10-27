"""
Unit tests for JenkinsDoc listeners module
"""

import os
import sys
import unittest
from unittest.mock import MagicMock, Mock, patch

# Add tests directory to path for test_helpers
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from helpers import setup_sublime_mocks, sublime_mock, sublime_plugin_mock

# Add the plugin's directory to the Python path (go up from unit/ -> tests/ -> plugin root)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))

# Mock Sublime Text modules before importing plugin code
sys.modules["sublime"] = sublime_mock
sys.modules["sublime_plugin"] = sublime_plugin_mock

from modules import listeners, utils


class TestJenkinsDocStatusBar(unittest.TestCase):
    """Test the JenkinsDocStatusBar class"""

    def setUp(self):
        """Set up test fixtures"""
        self.status_bar = listeners.JenkinsDocStatusBar()
        self.view = Mock()
        self.settings = Mock()

        # Mock jenkins data
        self.jenkins_data = {
            "plugins": [],
            "instructions": [{"command": "echo"}, {"command": "sh"}],
            "sections": [],
            "directives": [],
            "environmentVariables": [],
        }

        utils.set_settings(self.settings)
        utils.set_jenkins_data(self.jenkins_data)

    def test_update_status_enabled(self):
        """Test status bar update when plugin is enabled"""
        self.settings.get.side_effect = lambda key, default=None: {
            "show_status_bar": True,
            "status_bar_text": "JenkinsDoc",
            "show_instruction_count": False,
            "enabled": True,
            "detect_groovy_files": True,
            "detect_jenkinsfile": True,
            "additional_file_patterns": [],
        }.get(key, default)

        syntax_mock = Mock()
        syntax_mock.scope = "source.groovy"
        self.view.syntax.return_value = syntax_mock
        self.view.file_name.return_value = "test.groovy"

        self.status_bar._update_status(self.view)

        # Should set status
        self.view.set_status.assert_called_once()
        call_args = self.view.set_status.call_args
        self.assertEqual(call_args[0][0], "jenkins_doc")
        self.assertIn("JenkinsDoc", call_args[0][1])

    def test_update_status_with_instruction_count(self):
        """Test status bar shows instruction count"""
        self.settings.get.side_effect = lambda key, default=None: {
            "show_status_bar": True,
            "status_bar_text": "JenkinsDoc",
            "show_instruction_count": True,
            "enabled": True,
            "detect_groovy_files": True,
            "detect_jenkinsfile": True,
            "additional_file_patterns": [],
        }.get(key, default)

        syntax_mock = Mock()
        syntax_mock.scope = "source.groovy"
        self.view.syntax.return_value = syntax_mock
        self.view.file_name.return_value = "test.groovy"

        self.status_bar._update_status(self.view)

        # Should set status with count
        call_args = self.view.set_status.call_args
        self.assertIn("2 steps", call_args[0][1])

    def test_update_status_disabled(self):
        """Test status bar when show_status_bar is disabled"""
        self.settings.get.side_effect = lambda key, default=None: {"show_status_bar": False}.get(key, default)

        self.status_bar._update_status(self.view)

        # Should erase status
        self.view.erase_status.assert_called_once_with("jenkins_doc")
        self.view.set_status.assert_not_called()

    def test_update_status_non_jenkins_file(self):
        """Test status bar clears for non-Jenkins files"""
        self.settings.get.side_effect = lambda key, default=None: {
            "show_status_bar": True,
            "enabled": True,
            "detect_groovy_files": False,
            "detect_jenkinsfile": False,
            "additional_file_patterns": [],
        }.get(key, default)

        self.view.syntax.return_value = None
        self.view.file_name.return_value = "test.txt"

        self.status_bar._update_status(self.view)

        # Should erase status for non-Jenkins files
        self.view.erase_status.assert_called_once_with("jenkins_doc")


class TestJenkinsDocHoverCommand(unittest.TestCase):
    """Test the JenkinsDocHoverCommand class"""

    def setUp(self):
        """Set up test fixtures"""
        self.hover = listeners.JenkinsDocHoverCommand()
        self.view = Mock()
        self.settings = Mock()

        # Mock jenkins data with complete instruction
        self.jenkins_data = {
            "instructions": [
                {
                    "command": "echo",
                    "name": "Echo",
                    "description": "Print a message",
                    "parameters": [
                        {
                            "name": "message",
                            "type": "String",
                            "description": "The message to print",
                            "isOptional": False,
                        }
                    ],
                    "url": "http://example.com/echo",
                }
            ],
            "environmentVariables": [{"name": "BUILD_NUMBER", "description": "The current build number"}],
            "sections": [
                {"name": "pipeline", "description": "Declarative pipeline", "url": "http://example.com/pipeline"}
            ],
            "directives": [{"name": "agent", "description": "Specify where to run", "url": "http://example.com/agent"}],
        }

        utils.set_settings(self.settings)
        utils.set_jenkins_data(self.jenkins_data)

    def test_find_documentation_instruction(self):
        """Test finding documentation for an instruction"""
        doc = self.hover._find_documentation("echo", self.jenkins_data)
        self.assertIsNotNone(doc)
        self.assertIn("Echo", doc)
        self.assertIn("Print a message", doc)
        self.assertIn("message", doc)

    def test_find_documentation_env_var(self):
        """Test finding documentation for environment variable"""
        doc = self.hover._find_documentation("BUILD_NUMBER", self.jenkins_data)
        self.assertIsNotNone(doc)
        self.assertIn("BUILD_NUMBER", doc)
        self.assertIn("build number", doc)

    def test_find_documentation_section(self):
        """Test finding documentation for section"""
        doc = self.hover._find_documentation("pipeline", self.jenkins_data)
        self.assertIsNotNone(doc)
        self.assertIn("pipeline", doc)
        self.assertIn("Declarative", doc)

    def test_find_documentation_directive(self):
        """Test finding documentation for directive"""
        doc = self.hover._find_documentation("agent", self.jenkins_data)
        self.assertIsNotNone(doc)
        self.assertIn("agent", doc)
        self.assertIn("where to run", doc)

    def test_find_documentation_not_found(self):
        """Test finding documentation returns None for unknown word"""
        doc = self.hover._find_documentation("unknown_command", self.jenkins_data)
        self.assertIsNone(doc)

    def test_format_instruction_doc_with_parameters(self):
        """Test formatting instruction with parameters"""
        instruction = self.jenkins_data["instructions"][0]
        html = self.hover._format_instruction_doc(instruction)

        self.assertIn("Echo", html)
        self.assertIn("Print a message", html)
        self.assertIn("Parameters", html)
        self.assertIn("message", html)
        self.assertIn("String", html)

    def test_format_instruction_doc_with_optional_parameter(self):
        """Test formatting instruction with optional parameter"""
        instruction = {
            "command": "test",
            "name": "Test",
            "description": "Test command",
            "parameters": [
                {"name": "optional_param", "type": "String", "description": "Optional parameter", "isOptional": True}
            ],
            "url": "http://example.com",
        }
        html = self.hover._format_instruction_doc(instruction)

        self.assertIn("optional_param", html)
        self.assertIn("Optional", html)

    def test_format_instruction_doc_with_enum_values(self):
        """Test formatting instruction with enum parameter"""
        instruction = {
            "command": "test",
            "name": "Test",
            "description": "Test command",
            "parameters": [
                {
                    "name": "level",
                    "type": "Enum",
                    "description": "Log level",
                    "isOptional": False,
                    "values": ["DEBUG", "INFO", "WARN", "ERROR"],
                }
            ],
            "url": "http://example.com",
        }
        html = self.hover._format_instruction_doc(instruction)

        self.assertIn("level", html)
        self.assertIn("Values:", html)
        self.assertIn("DEBUG", html)
        self.assertIn("INFO", html)

    def test_format_env_var_doc(self):
        """Test formatting environment variable documentation"""
        env_var = self.jenkins_data["environmentVariables"][0]
        html = self.hover._format_env_var_doc(env_var)

        self.assertIn("BUILD_NUMBER", html)
        self.assertIn("build number", html)
        self.assertIn("Environment Variable", html)


class TestJenkinsCompletions(unittest.TestCase):
    """Test the JenkinsCompletions class"""

    def setUp(self):
        """Set up test fixtures"""
        self.completions = listeners.JenkinsCompletions()
        self.view = Mock()
        self.settings = Mock()

        # Mock jenkins data
        self.jenkins_data = {
            "instructions": [
                {"command": "echo", "name": "Echo", "parameters": []},
                {"command": "sh", "name": "Shell Script", "parameters": [{"name": "script", "type": "String"}]},
                {"command": "stage", "name": "Stage", "parameters": [{"name": "name", "type": "String"}]},
            ],
            "sections": [
                {"name": "pipeline", "description": "Declarative Pipeline"},
                {"name": "post", "description": "Post actions"},
            ],
            "directives": [{"name": "agent", "description": "Agent"}, {"name": "when", "description": "When"}],
            "environmentVariables": [
                {"name": "BUILD_NUMBER", "description": "Build number"},
                {"name": "JOB_NAME", "description": "Job name"},
            ],
        }

        utils.set_settings(self.settings)
        utils.set_jenkins_data(self.jenkins_data)

    def test_get_instruction_completions_no_prefix(self):
        """Test getting all instruction completions"""
        completions = self.completions._get_instruction_completions(self.jenkins_data, self.settings, "")

        self.assertEqual(len(completions), 3)
        # Check that all instructions are included
        commands = [c[0].split("\t")[0] for c in completions]
        self.assertIn("echo", commands)
        self.assertIn("sh", commands)
        self.assertIn("stage", commands)

    def test_get_instruction_completions_with_prefix(self):
        """Test getting filtered instruction completions"""
        completions = self.completions._get_instruction_completions(self.jenkins_data, self.settings, "s")

        # Should only return 'sh' and 'stage'
        self.assertEqual(len(completions), 2)
        commands = [c[0].split("\t")[0] for c in completions]
        self.assertIn("sh", commands)
        self.assertIn("stage", commands)
        self.assertNotIn("echo", commands)

    def test_get_instruction_completions_with_parameters(self):
        """Test instruction completions include parameter placeholder"""
        completions = self.completions._get_instruction_completions(self.jenkins_data, self.settings, "sh")

        # sh has parameters, should include ${1}
        self.assertEqual(len(completions), 1)  # Only sh matches prefix "sh"
        sh_completion = completions[0]
        self.assertIn("${1}", sh_completion[1])

    def test_get_instruction_completions_without_parameters(self):
        """Test instruction completions for command without parameters"""
        completions = self.completions._get_instruction_completions(self.jenkins_data, self.settings, "echo")

        # echo has no parameters
        self.assertEqual(len(completions), 1)
        self.assertIn("echo()", completions[0][1])

    def test_get_env_completions_without_prefix(self):
        """Test environment variable completions without prefix"""
        completions = self.completions._get_env_completions(self.jenkins_data, include_prefix=True)

        self.assertEqual(len(completions), 2)
        # Should include 'env.' prefix
        self.assertTrue(any("env.BUILD_NUMBER" in c[1] for c in completions))
        self.assertTrue(any("env.JOB_NAME" in c[1] for c in completions))

    def test_get_env_completions_with_prefix(self):
        """Test environment variable completions after 'env.'"""
        completions = self.completions._get_env_completions(self.jenkins_data, include_prefix=False)

        self.assertEqual(len(completions), 2)
        # Should NOT include 'env.' prefix (already typed)
        self.assertTrue(any(c[1] == "BUILD_NUMBER" for c in completions))
        self.assertTrue(any(c[1] == "JOB_NAME" for c in completions))

    def test_get_section_completions(self):
        """Test section completions"""
        completions = self.completions._get_section_completions(self.jenkins_data)

        self.assertEqual(len(completions), 2)
        sections = [c[0].split("\t")[0] for c in completions]
        self.assertIn("pipeline", sections)
        self.assertIn("post", sections)

        # Check snippet format
        for completion in completions:
            self.assertIn("{\n\t", completion[1])

    def test_get_directive_completions(self):
        """Test directive completions"""
        completions = self.completions._get_directive_completions(self.jenkins_data)

        self.assertEqual(len(completions), 2)
        directives = [c[0].split("\t")[0] for c in completions]
        self.assertIn("agent", directives)
        self.assertIn("when", directives)

    def test_get_post_completions(self):
        """Test post condition completions"""
        completions = self.completions._get_post_completions(self.jenkins_data)

        # Should return hardcoded post conditions
        self.assertGreater(len(completions), 0)
        conditions = [c[0].split("\t")[0] for c in completions]
        self.assertIn("always", conditions)
        self.assertIn("success", conditions)
        self.assertIn("failure", conditions)

    def test_get_parameter_completions(self):
        """Test parameter completions for a function"""
        # Pattern needs to be inside a block (with { or {{)
        line = "stage('test') { sh("
        completions = self.completions._get_parameter_completions(self.jenkins_data, line)

        # sh command has 'script' parameter
        self.assertEqual(len(completions), 1)
        self.assertIn("script", completions[0][0])
        self.assertIn("String", completions[0][0])


class TestJenkinsGoToDefinition(unittest.TestCase):
    """Test the JenkinsGoToDefinitionCommand class"""

    def setUp(self):
        """Set up test fixtures"""
        self.goto_def = listeners.JenkinsGoToDefinitionCommand()
        self.view = Mock()
        self.settings = Mock()

        utils.set_settings(self.settings)

    def test_find_function_in_current_file(self):
        """Test finding function definition in current file"""
        # Mock file content with a function definition
        content = """
def myFunction() {
    echo "Hello"
}

def anotherFunction() {
    myFunction()
}
"""
        self.view.size.return_value = len(content)
        self.view.substr.return_value = content
        self.view.text_point.return_value = 10
        self.view.sel.return_value = Mock()

        result = self.goto_def._find_function_in_current_file(self.view, "myFunction")

        self.assertTrue(result)
        # Should have cleared and added to selection
        self.view.sel().clear.assert_called_once()
        self.view.sel().add.assert_called_once()

    def test_find_function_not_in_current_file(self):
        """Test function not found returns False"""
        content = """
def otherFunction() {
    echo "Hello"
}
"""
        self.view.size.return_value = len(content)
        self.view.substr.return_value = content

        result = self.goto_def._find_function_in_current_file(self.view, "nonExistent")

        self.assertFalse(result)

    def test_is_inside_post_block_true(self):
        """Test detection of cursor inside post block"""
        completions_inst = listeners.JenkinsCompletions()
        view = Mock()
        content = """
pipeline {
    post {
        always {
            echo "Done"
        }
    }
}
"""
        point = content.index("echo")
        view.substr.return_value = content[:point]

        result = completions_inst._is_inside_post_block(view, point)

        self.assertTrue(result)

    def test_is_inside_post_block_false(self):
        """Test detection of cursor outside post block"""
        completions_inst = listeners.JenkinsCompletions()
        view = Mock()
        content = """
pipeline {
    stages {
        stage('Build') {
            steps {
                echo "Building"
            }
        }
    }
}
"""
        point = content.index("Building")
        view.substr.return_value = content[:point]

        result = completions_inst._is_inside_post_block(view, point)

        self.assertFalse(result)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling"""

    def test_find_documentation_with_empty_data(self):
        """Test documentation lookup with empty data"""
        hover = listeners.JenkinsDocHoverCommand()
        empty_data = {"instructions": [], "environmentVariables": [], "sections": [], "directives": []}

        doc = hover._find_documentation("echo", empty_data)
        self.assertIsNone(doc)

    def test_get_completions_with_empty_data(self):
        """Test completions with empty data"""
        completions_inst = listeners.JenkinsCompletions()
        empty_data = {"instructions": [], "sections": [], "directives": [], "environmentVariables": []}

        utils.set_jenkins_data(empty_data)
        utils.set_settings(Mock())

        completions = completions_inst._get_instruction_completions(empty_data, Mock(), "")

        self.assertEqual(len(completions), 0)

    def test_format_instruction_without_url(self):
        """Test formatting instruction without URL"""
        hover = listeners.JenkinsDocHoverCommand()
        instruction = {"command": "test", "name": "Test", "description": "Test command", "parameters": []}

        html = hover._format_instruction_doc(instruction)

        self.assertIn("Test", html)
        self.assertNotIn("View Documentation", html)

    def test_format_instruction_without_parameters(self):
        """Test formatting instruction without parameters"""
        hover = listeners.JenkinsDocHoverCommand()
        instruction = {
            "command": "test",
            "name": "Test",
            "description": "Test command",
            "parameters": [],
            "url": "http://example.com",
        }

        html = hover._format_instruction_doc(instruction)

        self.assertIn("Test", html)
        self.assertNotIn("Parameters", html)

    def test_parameter_completions_for_nonexistent_function(self):
        """Test parameter completions for function that doesn't exist"""
        completions_inst = listeners.JenkinsCompletions()
        utils.set_jenkins_data({"instructions": [{"command": "echo", "parameters": []}]})

        completions = completions_inst._get_parameter_completions(None, "nonExistent(")

        self.assertEqual(len(completions), 0)

    def test_parameter_completions_with_no_match(self):
        """Test parameter completions with no regex match"""
        completions_inst = listeners.JenkinsCompletions()
        completions = completions_inst._get_parameter_completions(None, "random text")

        self.assertEqual(len(completions), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
