"""
Diagnostic commands for JenkinsDoc plugin
"""

import sublime
import sublime_plugin

from . import utils


class JenkinsDocTestCompletionsCommand(sublime_plugin.WindowCommand):
    """Test command to verify completions are working"""

    def run(self):
        """Test completions"""
        view = self.window.active_view()
        if not view:
            sublime.message_dialog("No active view")
            return

        # Force create some test completions
        test_completions = [
            ["echo\tJenkins Step", "echo '${1:message}'"],
            ["git\tJenkins Step", "git(url: '${1:url}')"],
            ["sh\tJenkins Step", "sh '${1:script}'"],
            ["stage\tJenkins Section", "stage('${1:name}') {\n\t$0\n}"],
            ["pipeline\tJenkins Section", "pipeline {\n\t$0\n}"]
        ]

        # Get current cursor position
        sel = view.sel()[0]
        point = sel.begin()

        # Show completions at cursor
        view.run_command('auto_complete', {
            'disable_auto_insert': True,
            'api_completions_only': False,
            'next_completion_if_showing': False
        })

        sublime.message_dialog(
            "Test completions triggered!\n\n"
            "If you don't see completions, try:\n"
            "1. Enable debug mode in settings\n"
            "2. Check View → Show Console for errors\n"
            "3. Make sure file is .groovy or Jenkinsfile"
        )


class JenkinsDocDiagnosticsCommand(sublime_plugin.WindowCommand):
    """Show diagnostics for JenkinsDoc plugin"""

    def run(self):
        """Display diagnostic information"""
        # Try to import version from parent package, fallback for tests
        try:
            from .. import __version__
        except (ImportError, ValueError):
            try:
                import jenkins_doc
                __version__ = jenkins_doc.__version__
            except:
                __version__ = '1.0.0'

        view = self.window.active_view()
        settings = utils.get_settings()
        jenkins_data = utils.get_jenkins_data()

        # Gather diagnostic info
        diagnostics = []
        diagnostics.append("=== JenkinsDoc Diagnostics ===\n")

        # Plugin version
        diagnostics.append("Version: {}\n".format(__version__))

        # Data status
        if jenkins_data:
            diagnostics.append("Data loaded: Yes")
            diagnostics.append("  - Plugins: {}".format(len(jenkins_data.get('plugins', []))))
            diagnostics.append("  - Instructions: {}".format(len(jenkins_data.get('instructions', []))))
            diagnostics.append("  - Sections: {}".format(len(jenkins_data.get('sections', []))))
            diagnostics.append("  - Directives: {}".format(len(jenkins_data.get('directives', []))))
            diagnostics.append("  - Environment Variables: {}\n".format(len(jenkins_data.get('environmentVariables', []))))
        else:
            diagnostics.append("Data loaded: No (ERROR!)\n")

        # Settings status
        if settings:
            diagnostics.append("Settings loaded: Yes")
            diagnostics.append("  - Enabled: {}".format(settings.get('enabled', True)))
            diagnostics.append("  - Autocompletion: {}".format(settings.get('enable_autocompletion', True)))
            diagnostics.append("  - Hover docs: {}".format(settings.get('show_hover_docs', True)))
            diagnostics.append("  - Status bar: {}".format(settings.get('show_status_bar', True)))
            diagnostics.append("  - Debug mode: {}\n".format(settings.get('debug_mode', False)))
        else:
            diagnostics.append("Settings loaded: No\n")

        # Current file detection
        if view:
            file_name = view.file_name() or "Untitled"
            syntax = view.syntax()
            syntax_name = syntax.name if syntax else "None"
            is_jenkins = utils.is_jenkins_file(view, settings)

            diagnostics.append("Current file: {}".format(file_name))
            diagnostics.append("Syntax: {}".format(syntax_name))
            diagnostics.append("Detected as Jenkins file: {}\n".format("Yes" if is_jenkins else "No"))

        # Sample completions test
        if jenkins_data and jenkins_data.get('instructions'):
            sample_instructions = list(jenkins_data['instructions'][:3])
            diagnostics.append("Sample instructions:")
            for inst in sample_instructions:
                diagnostics.append("  - {}".format(inst.get('command', 'Unknown')))

        # Show in console
        output = "\n".join(diagnostics)
        print(output)

        # Copy to clipboard
        sublime.set_clipboard(output)

        # Also show in message dialog with clipboard note
        sublime.message_dialog(output + "\n\n(Diagnostics copied to clipboard)")
