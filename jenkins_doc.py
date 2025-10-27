"""
Jenkins Documentation for Sublime Text

A Sublime Text plugin that provides documentation and autocompletion
for Jenkins Pipeline syntax.

Version: 1.0.0
Author: Tsahi Elkayam
LinkedIn: https://www.linkedin.com/in/etsahi/
Repository: https://github.com/Tsahi-Elkayam/JenkinsDoc
License: GPL-3.0
Inspired by: JenkinsDocExtension for VSCode by Ryan Martinet (Maarti)
"""

__version__ = "1.0.0"
__author__ = "Tsahi Elkayam"
__linkedin__ = "https://www.linkedin.com/in/etsahi/"
__license__ = "GPL-3.0"
__repository__ = "https://github.com/Tsahi-Elkayam/JenkinsDoc"

import sublime
import sublime_plugin
import webbrowser

# Import utilities and listeners from modules
# Try relative imports first (when loaded as a package), fall back to absolute (for tests)
try:
    from .modules import utils
    from .modules.listeners import (
        JenkinsDocStatusBar,
        JenkinsDocHoverCommand,
        JenkinsCompletions,
        JenkinsGoToDefinitionCommand,
    )
    from .modules.diagnostics import JenkinsDocTestCompletionsCommand, JenkinsDocDiagnosticsCommand
except ImportError:
    from modules import utils
    from modules.listeners import (
        JenkinsDocStatusBar,
        JenkinsDocHoverCommand,
        JenkinsCompletions,
        JenkinsGoToDefinitionCommand,
    )
    from modules.diagnostics import JenkinsDocTestCompletionsCommand, JenkinsDocDiagnosticsCommand


def plugin_loaded():
    """Load plugin data when Sublime starts"""
    # Load settings
    settings = sublime.load_settings("JenkinsDoc.sublime-settings")
    utils.set_settings(settings)

    # Load data
    jenkins_data = utils.load_jenkins_data(settings)

    # Build lookup indices for O(1) access
    if jenkins_data:
        jenkins_data["_lookup"] = {
            "instructions": {i["command"]: i for i in jenkins_data.get("instructions", [])},
            "environmentVariables": {e["name"]: e for e in jenkins_data.get("environmentVariables", [])},
            "sections": {s["name"]: s for s in jenkins_data.get("sections", [])},
            "directives": {d["name"]: d for d in jenkins_data.get("directives", [])},
        }

    utils.set_jenkins_data(jenkins_data)

    # Show loading status in console if enabled
    if settings.get("show_console_messages", True) and jenkins_data:
        plugin_count = len(jenkins_data.get("plugins", []))
        instruction_count = len(jenkins_data.get("instructions", []))
        print("JenkinsDoc: Successfully loaded {} plugins with {} instructions".format(plugin_count, instruction_count))


class JenkinsDocShowCommand(sublime_plugin.WindowCommand):
    """Show Jenkins Documentation plugin information"""

    def run(self):
        """Display plugin information dialog"""
        message = """Jenkins Documentation for Sublime Text

Version: {version}
Author: Tsahi Elkayam

A comprehensive Jenkins Pipeline documentation and autocompletion
plugin for Sublime Text.

Features:
• Hover documentation for Jenkins Pipeline steps
• Intelligent autocompletion with parameter hints
• Environment variable completion (env.)
• Go to definition for Groovy functions
• Context-aware completions
• Status bar indicator
• Fully configurable settings

Repository:
https://github.com/Tsahi-Elkayam/JenkinsDoc

Inspired by the VSCode JenkinsDocExtension by Ryan Martinet (Maarti).

© 2025 Tsahi Elkayam
""".format(
            version=__version__
        )

        sublime.message_dialog(message)


class JenkinsDocReloadCommand(sublime_plugin.WindowCommand):
    """Reload Jenkins Documentation plugin settings and data"""

    def run(self):
        """Reload settings and data"""
        # Reload settings
        settings = sublime.load_settings("JenkinsDoc.sublime-settings")
        utils.set_settings(settings)

        # Reload data
        jenkins_data = utils.load_jenkins_data(settings)
        utils.set_jenkins_data(jenkins_data)

        # Show status
        if jenkins_data:
            plugin_count = len(jenkins_data.get("plugins", []))
            instruction_count = len(jenkins_data.get("instructions", []))
            sublime.status_message(
                "JenkinsDoc: Reloaded {} plugins with {} instructions".format(plugin_count, instruction_count)
            )
            if settings.get("show_console_messages", True):
                print("JenkinsDoc: Reloaded {} plugins with {} instructions".format(plugin_count, instruction_count))
        else:
            sublime.status_message("JenkinsDoc: Failed to reload data")
            if settings.get("show_console_messages", True):
                print("JenkinsDoc: Failed to reload data")


class OpenUrlCommand(sublime_plugin.ApplicationCommand):
    """Command to open URLs in the default browser"""

    def run(self, url):
        """Open URL in default browser"""
        webbrowser.open(url)
