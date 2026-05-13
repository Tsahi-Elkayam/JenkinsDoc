"""Top-level entry point for the JenkinsDoc Sublime Text plugin.

Sublime Text only scans top-level files of a Package for plugin classes
(EventListener / Command subclasses), so the listener and command classes
defined in :mod:`modules` are re-exported here.

Two import contexts are supported:

* Sublime loads this file as part of the ``JenkinsDoc`` package, so relative
  imports (``from .modules ...``) work.
* The unit tests insert the plugin root onto ``sys.path`` and import
  ``jenkins_doc`` as a top-level module, so the fallback ``from modules ...``
  is needed.
"""

import webbrowser

import sublime
import sublime_plugin

try:
    from .modules import log as _log
    from .modules import utils
    from .modules.diagnostics import (
        JenkinsDocDiagnosticsCommand,
        JenkinsDocTestCompletionsCommand,
    )
    from .modules.listeners import (
        JenkinsCompletions,
        JenkinsDocHoverCommand,
        JenkinsDocStatusBar,
        JenkinsGoToDefinitionCommand,
    )
except ImportError:
    from modules import log as _log
    from modules import utils
    from modules.diagnostics import (
        JenkinsDocDiagnosticsCommand,
        JenkinsDocTestCompletionsCommand,
    )
    from modules.listeners import (
        JenkinsCompletions,
        JenkinsDocHoverCommand,
        JenkinsDocStatusBar,
        JenkinsGoToDefinitionCommand,
    )

__version__ = "0.1.0"

SETTINGS_FILE = "JenkinsDoc.sublime-settings"
REPO_URL = "https://github.com/Tsahi-Elkayam/JenkinsDoc"

# Re-exports kept referenced so linters don't drop them. Sublime registers
# any EventListener / Command subclass that lives in this module's namespace.
_RE_EXPORTS = (
    JenkinsDocStatusBar,
    JenkinsDocHoverCommand,
    JenkinsCompletions,
    JenkinsGoToDefinitionCommand,
    JenkinsDocDiagnosticsCommand,
    JenkinsDocTestCompletionsCommand,
)


def _load_data(settings):
    _log.configure(settings)
    utils.set_settings(settings)
    return utils.load_jenkins_data(settings)


def plugin_loaded():
    settings = sublime.load_settings(SETTINGS_FILE)
    data = _load_data(settings)
    utils.set_jenkins_data(data)


def plugin_unloaded():
    try:
        sublime.load_settings(SETTINGS_FILE).clear_on_change("jenkins_doc_reload")
    except Exception:
        pass


class JenkinsDocReloadCommand(sublime_plugin.WindowCommand):
    """Reload Jenkins data and settings from disk."""

    def run(self):
        settings = sublime.load_settings(SETTINGS_FILE)
        data = _load_data(settings)
        utils.set_jenkins_data(data)

        if data:
            sublime.status_message(
                "JenkinsDoc: Reloaded {} plugins, {} instructions".format(
                    len(data.get("plugins", [])),
                    len(data.get("instructions", [])),
                )
            )
        else:
            sublime.status_message("JenkinsDoc: Failed to reload data")


class JenkinsDocShowCommand(sublime_plugin.WindowCommand):
    """Show plugin information dialog."""

    def run(self):
        sublime.message_dialog(
            "Jenkins Documentation\n"
            "Version: {0}\n"
            "Author: Tsahi Elkayam\n\n"
            "Features:\n"
            "  - Hover documentation for Jenkins keywords\n"
            "  - Autocompletion for steps, sections, directives\n"
            "  - Environment variable completions\n"
            "  - Go to definition for Groovy helpers\n\n"
            "Repository: {1}\n".format(__version__, REPO_URL)
        )


class OpenUrlCommand(sublime_plugin.ApplicationCommand):
    """Open a URL in the system default browser."""

    def run(self, url):
        webbrowser.open(url)
