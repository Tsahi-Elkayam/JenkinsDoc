"""
Unit tests for JenkinsDoc command classes
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

import jenkins_doc

# Now we can import our modules
from modules import listeners, utils


class TestJenkinsDocReloadCommand(unittest.TestCase):
    """Test the JenkinsDocReloadCommand class"""

    def setUp(self):
        """Set up test fixtures"""
        # Reset sublime mocks to clear call history from other tests
        sublime_mock.status_message.reset_mock()

        self.window = Mock()
        self.command = jenkins_doc.JenkinsDocReloadCommand(self.window)

        # Mock settings
        self.mock_settings = Mock()
        sublime_mock.load_settings.return_value = self.mock_settings

    @patch("modules.utils.load_jenkins_data")
    def test_reload_success(self, mock_load):
        """Test successful reload"""
        mock_data = {
            "plugins": [{"name": "test"}],
            "instructions": [{"command": "echo"}],
            "sections": [],
            "directives": [],
            "environmentVariables": [],
        }
        mock_load.return_value = mock_data
        self.mock_settings.get.return_value = True

        # Reset the mock to clear any calls from setUp
        sublime_mock.load_settings.reset_mock()

        self.command.run()

        # Should load settings and data
        sublime_mock.load_settings.assert_called()
        mock_load.assert_called_once()

        # Should show success message
        sublime_mock.status_message.assert_called_once()
        call_args = sublime_mock.status_message.call_args[0][0]
        self.assertIn("Reloaded", call_args)
        self.assertIn("1 plugins", call_args)
        self.assertIn("1 instructions", call_args)

    @patch("modules.utils.load_jenkins_data")
    def test_reload_failure(self, mock_load):
        """Test reload with no data"""
        mock_load.return_value = None
        self.mock_settings.get.return_value = True

        self.command.run()

        # Should show failure message
        sublime_mock.status_message.assert_called_once()
        call_args = sublime_mock.status_message.call_args[0][0]
        self.assertIn("Failed", call_args)


class TestJenkinsDocDiagnosticsCommand(unittest.TestCase):
    """Test the JenkinsDocDiagnosticsCommand class"""

    def setUp(self):
        """Set up test fixtures"""
        # Reset sublime mocks to clear call history from other tests
        sublime_mock.message_dialog.reset_mock()
        sublime_mock.set_clipboard.reset_mock()

        self.window = Mock()
        self.command = jenkins_doc.JenkinsDocDiagnosticsCommand(self.window)

        # Mock data
        self.mock_data = {
            "plugins": [{"name": "test"}],
            "instructions": [{"command": "echo"}],
            "sections": [{"name": "pipeline"}],
            "directives": [{"name": "agent"}],
            "environmentVariables": [{"name": "BUILD_NUMBER"}],
        }

        self.mock_settings = Mock()
        self.mock_settings.get.side_effect = lambda key, default=None: {
            "enabled": True,
            "enable_autocompletion": True,
            "show_hover_docs": True,
            "show_status_bar": True,
            "debug_mode": False,
        }.get(key, default)

        utils.set_jenkins_data(self.mock_data)
        utils.set_settings(self.mock_settings)

    def test_diagnostics_with_data(self):
        """Test diagnostics output with loaded data"""
        view = Mock()
        view.file_name.return_value = "/path/to/Jenkinsfile"
        syntax_mock = Mock()
        syntax_mock.name = "Groovy"
        syntax_mock.scope = "source.groovy"
        view.syntax.return_value = syntax_mock

        self.window.active_view.return_value = view

        self.command.run()

        # Should show dialog
        sublime_mock.message_dialog.assert_called_once()
        output = sublime_mock.message_dialog.call_args[0][0]

        # Check output contains expected info
        self.assertIn("JenkinsDoc Diagnostics", output)
        self.assertIn("Data loaded: Yes", output)
        self.assertIn("Plugins: 1", output)
        self.assertIn("Instructions: 1", output)
        self.assertIn("Settings loaded: Yes", output)

    def test_diagnostics_without_data(self):
        """Test diagnostics output without data"""
        utils.set_jenkins_data(None)

        self.window.active_view.return_value = None

        self.command.run()

        sublime_mock.message_dialog.assert_called_once()
        output = sublime_mock.message_dialog.call_args[0][0]

        self.assertIn("Data loaded: No", output)

    def test_diagnostics_copies_to_clipboard(self):
        """Test that diagnostics are copied to clipboard"""
        self.window.active_view.return_value = None

        self.command.run()

        # Should copy to clipboard
        sublime_mock.set_clipboard.assert_called_once()


class TestJenkinsDocShowCommand(unittest.TestCase):
    """Test the JenkinsDocShowCommand class"""

    def setUp(self):
        """Set up test fixtures"""
        # Reset sublime mocks to clear call history from other tests
        sublime_mock.message_dialog.reset_mock()

        self.window = Mock()
        self.command = jenkins_doc.JenkinsDocShowCommand(self.window)

    def test_show_info(self):
        """Test showing plugin information"""
        self.command.run()

        # Should display message dialog
        sublime_mock.message_dialog.assert_called_once()
        message = sublime_mock.message_dialog.call_args[0][0]

        # Check message contains expected info
        self.assertIn("Jenkins Documentation", message)
        self.assertIn("Version:", message)
        self.assertIn("Tsahi Elkayam", message)
        self.assertIn("Features:", message)
        self.assertIn("Repository:", message)


class TestJenkinsDocTestCompletionsCommand(unittest.TestCase):
    """Test the JenkinsDocTestCompletionsCommand class"""

    def setUp(self):
        """Set up test fixtures"""
        # Reset sublime mocks to clear call history from other tests
        sublime_mock.message_dialog.reset_mock()

        self.window = Mock()
        self.command = jenkins_doc.JenkinsDocTestCompletionsCommand(self.window)

    def test_with_active_view(self):
        """Test test completions with active view"""
        view = Mock()
        sel_mock = Mock()
        sel_mock.begin.return_value = 0
        view.sel.return_value = [sel_mock]

        self.window.active_view.return_value = view

        self.command.run()

        # Should run auto_complete command
        view.run_command.assert_called_once_with(
            "auto_complete",
            {"disable_auto_insert": True, "api_completions_only": False, "next_completion_if_showing": False},
        )

        # Should show message
        sublime_mock.message_dialog.assert_called_once()

    def test_without_active_view(self):
        """Test test completions without active view"""
        self.window.active_view.return_value = None

        self.command.run()

        # Should show error message
        sublime_mock.message_dialog.assert_called_once()
        message = sublime_mock.message_dialog.call_args[0][0]
        self.assertIn("No active view", message)


class TestOpenUrlCommand(unittest.TestCase):
    """Test the OpenUrlCommand class"""

    @patch("webbrowser.open")
    def test_open_url(self, mock_open):
        """Test opening URL in browser"""
        command = jenkins_doc.OpenUrlCommand()
        test_url = "https://www.jenkins.io/doc/pipeline/steps/"

        command.run(test_url)

        # Should call webbrowser.open
        mock_open.assert_called_once_with(test_url)


class TestPluginLoaded(unittest.TestCase):
    """Test the plugin_loaded function"""

    @patch("modules.utils.load_jenkins_data")
    def test_plugin_loaded_success(self, mock_load):
        """Test successful plugin loading"""
        mock_data = {
            "plugins": [{"name": "test"}],
            "instructions": [{"command": "echo"}],
            "sections": [],
            "directives": [],
            "environmentVariables": [],
        }
        mock_load.return_value = mock_data

        mock_settings = Mock()
        mock_settings.get.return_value = True
        sublime_mock.load_settings.return_value = mock_settings

        # Call plugin_loaded
        jenkins_doc.plugin_loaded()

        # Should load settings and data
        sublime_mock.load_settings.assert_called_with("JenkinsDoc.sublime-settings")
        mock_load.assert_called_once()

        # Data should be set
        loaded_data = utils.get_jenkins_data()
        self.assertEqual(loaded_data, mock_data)

    @patch("modules.utils.load_jenkins_data")
    def test_plugin_loaded_with_console_messages_disabled(self, mock_load):
        """Test plugin loading with console messages disabled"""
        mock_data = {"plugins": [], "instructions": [], "sections": [], "directives": [], "environmentVariables": []}
        mock_load.return_value = mock_data

        mock_settings = Mock()
        mock_settings.get.side_effect = lambda key, default=None: {"show_console_messages": False}.get(key, default)
        sublime_mock.load_settings.return_value = mock_settings

        # Reset print mock if it was called before
        with patch("builtins.print") as mock_print:
            jenkins_doc.plugin_loaded()

            # Should not print anything
            mock_print.assert_not_called()


class TestIntegrationScenarios(unittest.TestCase):
    """Integration tests for common usage scenarios"""

    def setUp(self):
        """Set up test fixtures"""
        # Comprehensive mock data
        self.mock_data = {
            "plugins": [{"name": "Pipeline", "url": "https://plugins.jenkins.io/workflow-aggregator/"}],
            "instructions": [
                {
                    "command": "echo",
                    "name": "Echo",
                    "description": "Print a message to the console",
                    "parameters": [
                        {
                            "name": "message",
                            "type": "String",
                            "description": "The message to print",
                            "isOptional": False,
                        }
                    ],
                    "url": "https://www.jenkins.io/doc/pipeline/steps/workflow-basic-steps/#echo",
                },
                {
                    "command": "sh",
                    "name": "Shell Script",
                    "description": "Execute a shell script",
                    "parameters": [
                        {
                            "name": "script",
                            "type": "String",
                            "description": "The script to execute",
                            "isOptional": False,
                        },
                        {
                            "name": "returnStatus",
                            "type": "boolean",
                            "description": "Return the status code",
                            "isOptional": True,
                        },
                    ],
                    "url": "https://www.jenkins.io/doc/pipeline/steps/workflow-durable-task-step/#sh",
                },
                {
                    "command": "timeout",
                    "name": "Timeout",
                    "description": "Execute with a timeout",
                    "parameters": [
                        {"name": "time", "type": "int", "description": "The timeout duration", "isOptional": False},
                        {
                            "name": "unit",
                            "type": "Enum",
                            "description": "The time unit",
                            "isOptional": True,
                            "values": ["SECONDS", "MINUTES", "HOURS", "DAYS"],
                        },
                    ],
                    "url": "https://www.jenkins.io/doc/pipeline/steps/workflow-basic-steps/#timeout",
                },
            ],
            "sections": [
                {
                    "name": "pipeline",
                    "description": "The declarative pipeline section",
                    "url": "https://www.jenkins.io/doc/book/pipeline/syntax/#declarative-pipeline",
                },
                {
                    "name": "stages",
                    "description": "Contains multiple stage directives",
                    "url": "https://www.jenkins.io/doc/book/pipeline/syntax/#stages",
                },
                {
                    "name": "post",
                    "description": "Post-build actions",
                    "innerInstructions": ["always", "success", "failure", "unstable"],
                    "url": "https://www.jenkins.io/doc/book/pipeline/syntax/#post",
                },
            ],
            "directives": [
                {
                    "name": "agent",
                    "description": "Specifies where the pipeline will execute",
                    "url": "https://www.jenkins.io/doc/book/pipeline/syntax/#agent",
                },
                {
                    "name": "options",
                    "description": "Pipeline-specific options",
                    "url": "https://www.jenkins.io/doc/book/pipeline/syntax/#options",
                },
            ],
            "environmentVariables": [
                {"name": "BUILD_NUMBER", "description": "The current build number"},
                {"name": "JOB_NAME", "description": "Name of the project of this build"},
                {"name": "WORKSPACE", "description": "The absolute path of the workspace"},
            ],
        }

        self.mock_settings = Mock()
        self.mock_settings.get.side_effect = lambda key, default=None: {
            "enabled": True,
            "detect_groovy_files": True,
            "detect_jenkinsfile": True,
            "additional_file_patterns": [],
            "show_hover_docs": True,
            "show_status_bar": True,
            "enable_autocompletion": True,
            "debug_mode": False,
        }.get(key, default)

        utils.set_jenkins_data(self.mock_data)
        utils.set_settings(self.mock_settings)

    def test_complete_workflow_jenkinsfile(self):
        """Test complete workflow for a Jenkinsfile"""
        # 1. Check file detection
        view = Mock()
        view.syntax.return_value = None
        view.file_name.return_value = "/project/Jenkinsfile"

        is_jenkins = utils.is_jenkins_file(view, self.mock_settings)
        self.assertTrue(is_jenkins)

        # 2. Get completions
        completions_handler = listeners.JenkinsCompletions()
        completions = completions_handler._get_instruction_completions(self.mock_data, self.mock_settings, "")

        self.assertGreater(len(completions), 0)
        commands = [c[0].split("\t")[0] for c in completions]
        self.assertIn("echo", commands)
        self.assertIn("sh", commands)

        # 3. Get hover documentation
        hover_handler = listeners.JenkinsDocHoverCommand()
        doc = hover_handler._find_documentation("echo", self.mock_data)

        self.assertIsNotNone(doc)
        self.assertIn("Print a message", doc)

    def test_complete_workflow_groovy_file(self):
        """Test complete workflow for a .groovy file"""
        # 1. Check file detection by syntax
        view = Mock()
        syntax_mock = Mock()
        syntax_mock.scope = "source.groovy"
        view.syntax.return_value = syntax_mock
        view.file_name.return_value = "/project/vars/myLibrary.groovy"

        is_jenkins = utils.is_jenkins_file(view, self.mock_settings)
        self.assertTrue(is_jenkins)

        # 2. Get environment variable completions
        completions_handler = listeners.JenkinsCompletions()
        env_completions = completions_handler._get_env_completions(self.mock_data, include_prefix=False)

        self.assertEqual(len(env_completions), 3)
        vars = [c[1] for c in env_completions]
        self.assertIn("BUILD_NUMBER", vars)
        self.assertIn("JOB_NAME", vars)
        self.assertIn("WORKSPACE", vars)

    def test_parameter_completion_workflow(self):
        """Test parameter completion for a command"""
        completions_handler = listeners.JenkinsCompletions()

        # User types inside a block "{ sh(" - should get parameter completions
        completions = completions_handler._get_parameter_completions(self.mock_data, "stage('build') { sh(")

        self.assertEqual(len(completions), 2)  # script and returnStatus
        params = [c[0].split("\t")[0] for c in completions]
        self.assertIn("script", params)
        self.assertIn("returnStatus", params)

    def test_enum_parameter_values(self):
        """Test that enum parameter shows available values"""
        hover_handler = listeners.JenkinsDocHoverCommand()

        # timeout command has enum parameter with values
        timeout_instruction = next(i for i in self.mock_data["instructions"] if i["command"] == "timeout")
        doc = hover_handler._format_instruction_doc(timeout_instruction)

        # Should show enum values
        self.assertIn("Values:", doc)
        self.assertIn("SECONDS", doc)
        self.assertIn("MINUTES", doc)
        self.assertIn("HOURS", doc)
        self.assertIn("DAYS", doc)

    def test_section_with_inner_instructions(self):
        """Test section that has inner instructions"""
        completions_handler = listeners.JenkinsCompletions()

        # post section has innerInstructions
        post_section = next(s for s in self.mock_data["sections"] if s["name"] == "post")

        completions = completions_handler._get_section_completions(self.mock_data)

        # Find post completion
        post_completion = next(c for c in completions if "post" in c[0])

        # Should include hint about inner instructions
        self.assertIn("always", post_completion[0])


if __name__ == "__main__":
    unittest.main(verbosity=2)
