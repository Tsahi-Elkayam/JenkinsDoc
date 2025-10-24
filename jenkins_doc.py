"""
Jenkins Documentation for Sublime Text

A Sublime Text plugin that provides documentation and autocompletion
for Jenkins Pipeline syntax.

Version: 1.0.0
Author: Tsahi Elkayam
Repository: https://github.com/Tsahi-Elkayam/JenkinsDoc
License: GPL-3.0
Inspired by: JenkinsDocExtension for VSCode by Ryan Martinet (Maarti)
"""

__version__ = '1.0.0'
__author__ = 'Tsahi Elkayam'
__license__ = 'GPL-3.0'
__repository__ = 'https://github.com/Tsahi-Elkayam/JenkinsDoc'

import sublime
import sublime_plugin
import json
import os
import re

# Global variables
jenkins_data = {}
settings = None

def plugin_loaded():
    """Load plugin data when Sublime starts"""
    global jenkins_data, settings

    # Load settings
    settings = sublime.load_settings('JenkinsDoc.sublime-settings')

    # Load data
    jenkins_data = load_jenkins_data()

    # Show loading status in console if enabled
    if settings.get('show_console_messages', True) and jenkins_data:
        plugin_count = len(jenkins_data.get('plugins', []))
        instruction_count = len(jenkins_data.get('instructions', []))
        print("JenkinsDoc: Successfully loaded {} plugins with {} instructions".format(
            plugin_count, instruction_count
        ))

def load_jenkins_data():
    """Load Jenkins documentation data from JSON file"""
    plugin_path = os.path.dirname(os.path.realpath(__file__))
    data_file = settings.get('data_file', 'jenkins_data.json') if settings else 'jenkins_data.json'
    data_path = os.path.join(plugin_path, data_file)

    try:
        with open(data_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        if settings and settings.get('show_console_messages', True):
            print("JenkinsDoc Error: Failed to load {} - {}".format(data_file, str(e)))
        # Return empty structure so plugin doesn't crash
        return {
            'plugins': [],
            'instructions': [],
            'sections': [],
            'directives': [],
            'environmentVariables': []
        }

def is_jenkins_file(view):
    """Check if the current file is a Groovy or Jenkinsfile"""
    if not settings or not settings.get('enabled', True):
        return False

    syntax = view.syntax()
    file_name = view.file_name() or ""
    base_name = os.path.basename(file_name)

    # Check if it's a Groovy file by syntax
    if settings.get('detect_groovy_files', True) and syntax and 'groovy' in syntax.scope.lower():
        return True

    # Check if it's a Jenkinsfile (with or without extension)
    if settings.get('detect_jenkinsfile', True):
        if 'Jenkinsfile' in base_name or base_name == 'Jenkinsfile':
            return True

    # Check additional file patterns
    additional_patterns = settings.get('additional_file_patterns', [])
    for pattern in additional_patterns:
        import fnmatch
        if fnmatch.fnmatch(file_name, pattern):
            return True

    return False

class JenkinsDocStatusBar(sublime_plugin.EventListener):
    """Show JenkinsDoc status in the status bar"""

    def on_activated(self, view):
        """Update status bar when a view is activated"""
        self._update_status(view)

    def on_new(self, view):
        """Update status bar for new files"""
        self._update_status(view)

    def on_load(self, view):
        """Update status bar when a file is loaded"""
        self._update_status(view)

    def on_clone(self, view):
        """Update status bar when a view is cloned"""
        self._update_status(view)

    def on_post_text_command(self, view, command_name, args):
        """Update status bar after text commands (like set syntax)"""
        if command_name == 'set_file_type':
            self._update_status(view)

    def on_post_save(self, view):
        """Update status bar after saving (in case filename changes)"""
        self._update_status(view)

    def _update_status(self, view):
        """Update the status bar based on file type"""
        if not settings or not settings.get('show_status_bar', True):
            view.erase_status('jenkins_doc')
            return

        if is_jenkins_file(view):
            # Check if data is loaded
            if jenkins_data and jenkins_data.get('instructions'):
                # Build status text from settings
                status_text = settings.get('status_bar_text', 'JenkinsDoc')
                if settings.get('show_instruction_count', False):
                    count = len(jenkins_data.get('instructions', []))
                    status_text = "{} ({} steps)".format(status_text, count)
                view.set_status('jenkins_doc', status_text)
            else:
                # Show error state if no data loaded
                status_text = settings.get('status_bar_text', 'JenkinsDoc')
                view.set_status('jenkins_doc', "{} (no data)".format(status_text))
        else:
            # Clear status for non-Jenkins files
            view.erase_status('jenkins_doc')

class JenkinsDocHoverCommand(sublime_plugin.EventListener):
    def __init__(self):
        self.css = """
            <style>
                body {
                    font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
                    padding: 12px 12px 16px 12px;
                    margin: 0;
                    line-height: 1.6;
                    background-color: #1e1e1e;
                    color: #d4d4d4;
                    min-width: 400px;
                }
                .container {
                    display: flex;
                    flex-direction: column;
                    position: relative;
                    padding-bottom: 36px;
                }
                .content-wrapper {
                    flex: 1;
                    margin-bottom: 16px;
                }
                h3 {
                    color: #4ec9b0;
                    margin: 0 0 16px 0;
                    padding-bottom: 8px;
                    border-bottom: 1px solid #404040;
                    font-size: 1.3em;
                    font-weight: 600;
                }
                h4 {
                    color: #9cdcfe;
                    margin: 20px 0 12px 0;
                    font-size: 1.1em;
                    font-weight: 500;
                }
                p {
                    margin: 12px 0;
                    color: #d4d4d4;
                    line-height: 1.6;
                }
                ul {
                    margin: 12px 0;
                    padding-left: 24px;
                }
                li {
                    margin: 8px 0;
                    color: #d4d4d4;
                    padding: 4px 0;
                }
                .param-name {
                    color: #9cdcfe;
                    font-weight: 600;
                    font-family: "Consolas", "Monaco", monospace;
                }
                .param-type {
                    color: #4ec9b0;
                    font-size: 0.9em;
                    margin-left: 8px;
                    padding: 2px 6px;
                    background-color: #252525;
                    border-radius: 3px;
                    font-family: "Consolas", "Monaco", monospace;
                }
                .param-optional {
                    color: #808080;
                    font-style: italic;
                    font-size: 0.9em;
                    margin-left: 8px;
                }
                .param-desc {
                    margin-top: 6px;
                    color: #cccccc;
                }
                .doc-link {
                    display: inline-block;
                    padding: 6px 12px;
                    background-color: #264f78;
                    border-radius: 4px;
                    color: #ffffff;
                    text-decoration: none;
                    transition: background-color 0.2s;
                    position: absolute;
                    bottom: 4px;
                    right: 0;
                    margin: 0;
                }
                .doc-link:hover {
                    background-color: #365f88;
                }
                .section-info {
                    background-color: #252525;
                    padding: 8px 12px;
                    border-radius: 4px;
                    margin: 12px 0;
                    border-left: 3px solid #4ec9b0;
                }
                .type-label {
                    display: inline-block;
                    padding: 2px 6px;
                    background-color: #252525;
                    border-radius: 3px;
                    color: #4ec9b0;
                    font-size: 0.9em;
                    margin-right: 8px;
                    font-family: "Consolas", "Monaco", monospace;
                }
            </style>
        """

    def on_hover(self, view, point, hover_zone):
        if hover_zone != sublime.HOVER_TEXT:
            return

        if not settings or not settings.get('show_hover_docs', True):
            return

        if not is_jenkins_file(view):
            return

        word_region = view.word(point)
        if not word_region:
            return

        word = view.substr(word_region)

        doc = self._find_documentation(word)
        if doc:
            wrapped_doc = "{0}<div class='container'>{1}</div>".format(self.css, doc)
            max_width = settings.get('hover_popup_max_width', 800)
            max_height = settings.get('hover_popup_max_height', 500)
            view.show_popup(wrapped_doc,
                          flags=sublime.HIDE_ON_MOUSE_MOVE_AWAY,
                          location=point,
                          max_width=max_width,
                          max_height=max_height)

    def _find_documentation(self, word):
        """Find documentation for the given word"""
        for instruction in jenkins_data['instructions']:
            if instruction['command'] == word:
                return self._format_instruction_doc(instruction)

        for env_var in jenkins_data['environmentVariables']:
            if env_var['name'] == word:
                return self._format_env_var_doc(env_var)

        for section in jenkins_data['sections']:
            if section['name'] == word:
                return self._format_section_doc(section)

        for directive in jenkins_data['directives']:
            if directive['name'] == word:
                return self._format_directive_doc(directive)

        return None

    def _format_instruction_doc(self, instruction):
        """Format instruction documentation as HTML"""
        html = """<div class="content-wrapper">
                    <h3>{0}</h3>
                    <div class="section-info">Pipeline Step</div>
                    <p>{1}</p>""".format(instruction['name'], instruction['description'])

        if instruction['parameters']:
            html += "<h4>Parameters</h4><ul>"
            for param in instruction['parameters']:
                optional = "(Optional)" if param.get('isOptional') else ""

                # Build parameter documentation with enum values
                param_doc = """
                    <li>
                        <div>
                            <span class="param-name">{0}</span>
                            <span class="param-type">{1}</span>
                            <span class="param-optional">{2}</span>
                        </div>""".format(param['name'], param['type'], optional)

                # Add enum values if present (matching VS Code implementation line 57)
                if param.get('values') and len(param['values']) > 0:
                    param_doc += "<div style='margin-left: 20px; margin-top: 8px;'><strong>Values:</strong><ul style='margin: 4px 0; padding-left: 20px;'>"
                    for value in param['values']:
                        param_doc += "<li style='color: #9cdcfe;'>{0}</li>".format(value)
                    param_doc += "</ul></div>"

                # Add parameter description
                param_doc += "<div class='param-desc'>{0}</div>".format(param['description'])
                param_doc += "</li>"

                html += param_doc
            html += "</ul>"

        html += "</div>"  # Close content-wrapper

        if instruction.get('url'):
            html += '<a href="{0}" class="doc-link">📘 View Documentation</a>'.format(instruction['url'])

        return html

    def _format_env_var_doc(self, env_var):
        """Format environment variable documentation as HTML"""
        return """
            <div class="content-wrapper">
                <h3>{0}</h3>
                <div class="section-info">Environment Variable</div>
                <p>{1}</p>
            </div>
        """.format(env_var['name'], env_var['description'])

    def _format_section_doc(self, section):
        """Format section documentation as HTML"""
        html = """<div class="content-wrapper">
                    <h3>{0}</h3>
                    <div class="section-info">Pipeline Section</div>
                    <p>{1}</p>""".format(section['name'], section['description'])

        if section.get('allowed'):
            html += """<div class="section-info">
                        <span class="type-label">Allowed</span>
                        {0}
                      </div>""".format(section.get('allowed', ''))

        html += "</div>"  # Close content-wrapper

        if section.get('url'):
            html += '<a href="{0}" class="doc-link">📘 View Documentation</a>'.format(section['url'])
        return html

    def _format_directive_doc(self, directive):
        """Format directive documentation as HTML"""
        html = """<div class="content-wrapper">
                    <h3>{0}</h3>
                    <div class="section-info">Pipeline Directive</div>
                    <p>{1}</p>""".format(directive['name'], directive['description'])

        if directive.get('allowed'):
            html += """<div class="section-info">
                        <span class="type-label">Allowed</span>
                        {0}
                      </div>""".format(directive.get('allowed', ''))

        html += "</div>"  # Close content-wrapper

        if directive.get('url'):
            html += '<a href="{0}" class="doc-link">📘 View Documentation</a>'.format(directive['url'])
        return html

class JenkinsCompletionsCommand(sublime_plugin.EventListener):
    """Provide autocompletions for Jenkins keywords"""

    def on_query_completions(self, view, prefix, locations):
        # Check if completions are enabled
        if not settings or not settings.get('enable_autocompletion', True):
            return None

        # Only activate for Groovy files and Jenkinsfiles
        if not is_jenkins_file(view):
            return None

        completions = []

        # Get current line up to cursor
        point = locations[0]
        line_region = view.line(point)
        line_start = line_region.begin()
        line_up_to_cursor = view.substr(sublime.Region(line_start, point))

        # Get previous line for multi-line context awareness
        previous_line = ""
        current_line_num = view.rowcol(point)[0]
        if current_line_num > 0:
            previous_line_region = view.line(view.text_point(current_line_num - 1, 0))
            previous_line = view.substr(previous_line_region)

        # Combine previous and current line for context-aware matching
        lines_prefix = previous_line + '\n' + line_up_to_cursor

        # Check if we're inside a function call for parameter completion
        param_completions = self._get_parameter_completions(line_up_to_cursor)
        if param_completions:
            return (param_completions, sublime.INHIBIT_WORD_COMPLETIONS)

        # Check if we're after 'env.' using regex pattern (more precise than string search)
        # Pattern matches "env." at the end of the line, optionally followed by partial word
        if re.search(r'(env)\.\w*$', line_up_to_cursor):
            # User already typed "env.", so only insert the variable name
            return (self._get_env_completions(include_prefix=False), sublime.INHIBIT_WORD_COMPLETIONS)

        # Check if we're inside a post block (using multi-line context)
        if re.search(r'post\s*\{\s*\w*$', lines_prefix):
            return (self._get_post_completions(), sublime.INHIBIT_WORD_COMPLETIONS)

        # Fallback to checking with full document context
        if self._is_inside_post_block(view, point):
            return (self._get_post_completions(), sublime.INHIBIT_WORD_COMPLETIONS)

        # Add all other completions (including env with "env." prefix)
        completions.extend(self._get_instruction_completions())
        completions.extend(self._get_section_completions())
        completions.extend(self._get_directive_completions())
        completions.extend(self._get_env_completions(include_prefix=True))

        # Limit completions if configured
        max_completions = settings.get('max_completions', 100) if settings else 100
        if len(completions) > max_completions:
            completions = completions[:max_completions]

        # Determine if we should inhibit word completions
        flags = sublime.INHIBIT_WORD_COMPLETIONS if settings and settings.get('inhibit_word_completions', True) else 0
        return (completions, flags)

    def _get_instruction_completions(self):
        """Get completions for Jenkins instructions"""
        completions = []
        for instruction in jenkins_data['instructions']:
            trigger = instruction['command']
            if instruction['parameters']:
                contents = "{0}(${{1}})".format(instruction['command'])
            else:
                contents = "{0}()".format(instruction['command'])

            completions.append(
                ["{0}\tJenkins Step".format(trigger), contents]
            )
        return completions

    def _get_env_completions(self, include_prefix=False):
        """Get completions for environment variables

        Args:
            include_prefix: If True, insert "env.NAME". If False, insert just "NAME".
                           False is used when user has already typed "env."
        """
        completions = []
        for var in jenkins_data['environmentVariables']:
            if include_prefix:
                # When not after "env.", insert full "env.NAME"
                trigger = "{0}\tEnvironment Variable".format(var['name'])
                contents = "env.{0}".format(var['name'])
            else:
                # When after "env.", insert just the variable name to avoid duplication
                trigger = "{0}\tEnvironment Variable".format(var['name'])
                contents = var['name']

            completions.append([trigger, contents])

        return completions

    def _get_section_completions(self):
        """Get completions for Jenkins sections"""
        completions = []
        for section in jenkins_data['sections']:
            # Check if section has inner instructions
            if section.get('innerInstructions'):
                # Add hint about available inner instructions
                inner_list = ", ".join(section['innerInstructions'][:3])
                if len(section['innerInstructions']) > 3:
                    inner_list += "..."
                trigger = "{0}\tJenkins Section ({1})".format(section['name'], inner_list)
                # Add a comment hint in the snippet
                contents = "{0} {{\n\t${{1:// {2}}}\n}}".format(
                    section['name'],
                    ", ".join(section['innerInstructions'])
                )
            else:
                trigger = "{0}\tJenkins Section".format(section['name'])
                contents = "{0} {{\n\t$0\n}}".format(section['name'])

            completions.append([trigger, contents])
        return completions

    def _get_directive_completions(self):
        """Get completions for Jenkins directives"""
        completions = []
        for directive in jenkins_data['directives']:
            # Check if directive has inner instructions
            if directive.get('innerInstructions'):
                # Add hint about available inner instructions
                inner_list = ", ".join(directive['innerInstructions'][:3])
                if len(directive['innerInstructions']) > 3:
                    inner_list += "..."
                trigger = "{0}\tJenkins Directive ({1})".format(directive['name'], inner_list)
                # Add a comment hint in the snippet
                contents = "{0} {{\n\t${{1:// {2}}}\n}}".format(
                    directive['name'],
                    ", ".join(directive['innerInstructions'])
                )
            else:
                trigger = "{0}\tJenkins Directive".format(directive['name'])
                contents = "{0} {{\n\t$0\n}}".format(directive['name'])

            completions.append([trigger, contents])
        return completions

    def _get_post_completions(self):
        """Get completions for post conditions"""
        # Extract post conditions from jenkins_data
        post_section = next((s for s in jenkins_data['sections']
                           if s['name'] == 'post'), None)

        if not post_section or not post_section.get('innerInstructions'):
            # Fallback to hardcoded values if data not found
            post_conditions = ['always', 'changed', 'fixed', 'regression', 'aborted',
                             'failure', 'success', 'unstable', 'unsuccessful', 'cleanup']
        else:
            post_conditions = post_section['innerInstructions']

        return [
            ["{0}\tPost Condition".format(condition),
             "{0} {{\n\t$0\n}}".format(condition)]
            for condition in post_conditions
        ]

    def _get_parameter_completions(self, line_up_to_cursor):
        """Get parameter completions when inside a function call"""
        # Match pattern like "functionName(" or "functionName(param1: 'value', "
        # Get the first word preceding a space or parenthesis, after the last opening brace
        match = re.search(r'\{?\s*(\w+)\s*[( ](?!.*[\{(])', line_up_to_cursor)
        if not match:
            return []

        function_name = match.group(1)

        # Find the instruction by command name
        instruction = next((i for i in jenkins_data['instructions']
                          if i['command'] == function_name), None)

        if not instruction or not instruction.get('parameters'):
            return []

        # Build parameter completions
        completions = []
        for param in instruction['parameters']:
            optional_label = "(Optional)" if param.get('isOptional') else ""
            param_type = param.get('type', 'Unknown')

            # Build the description
            desc_parts = []
            if param.get('values'):
                desc_parts.append("Values: " + ", ".join(param['values']))
            if param.get('description'):
                desc_parts.append(param['description'])
            description = " - ".join(desc_parts) if desc_parts else ""

            # Build the insertion text based on type
            if param_type == 'String':
                insert_text = "{0}: '${{1}}'".format(param['name'])
            elif param_type == 'boolean':
                insert_text = "{0}: ${{1:true}}".format(param['name'])
            elif param_type == 'Enum' and param.get('values'):
                # For enum, just provide the parameter name and let user type
                # Sublime doesn't support choice snippets like VS Code
                insert_text = "{0}: '${{1}}'".format(param['name'])
            else:
                insert_text = "{0}: ".format(param['name'])

            # Format: [trigger\tDescription, contents]
            trigger = "{0}\t{1} {2}".format(param['name'], param_type, optional_label)
            completions.append([trigger, insert_text])

        return completions

    def _is_inside_post_block(self, view, point):
        """Check if cursor is inside a post{} block"""
        # Search backwards for 'post {'
        content = view.substr(sublime.Region(0, point))
        post_matches = list(re.finditer(r'\bpost\s*{', content))
        if not post_matches:
            return False

        # Check if we're inside the closest post block
        last_post = post_matches[-1]
        post_start = last_post.start()

        # Count braces to find matching end
        brace_count = 1
        pos = last_post.end()
        while pos < point and brace_count > 0:
            char = content[pos]
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
            pos += 1

        return brace_count > 0

class JenkinsGoToDefinitionCommand(sublime_plugin.EventListener):
    """Provide go-to-definition functionality for Groovy functions"""

    def on_hover(self, view, point, hover_zone):
        """Show definition link on hover"""
        if hover_zone != sublime.HOVER_TEXT:
            return

        if not settings or not settings.get('enable_goto_definition', True):
            return

        if not is_jenkins_file(view):
            return

        # Check if Ctrl/Cmd is pressed (for goto definition hint)
        # We'll provide the definition link in the popup
        word_region = view.word(point)
        if not word_region:
            return

        word = view.substr(word_region)

        # Expand to capture object.method pattern
        extended_region = view.expand_by_class(
            point,
            sublime.CLASS_WORD_START | sublime.CLASS_WORD_END,
            "._"
        )
        extended_word = view.substr(extended_region)

        # Only show for word.word pattern (like fileName.functionName)
        if '.' in extended_word:
            parts = extended_word.split('.')
            if len(parts) == 2:
                file_name, function_name = parts
                # Check if we should show popup
                if settings and settings.get('show_goto_popup', True):
                    # Show a hint that definition can be navigated
                    link_html = '<a href="goto:{0}:{1}">Go to definition of {2}</a>'.format(
                        file_name, function_name, extended_word
                    )
                    view.show_popup(
                        link_html,
                        flags=sublime.HIDE_ON_MOUSE_MOVE_AWAY,
                        location=point,
                        on_navigate=lambda href: self._handle_goto(view, href)
                    )

    def _handle_goto(self, view, href):
        """Handle goto definition navigation"""
        if not href.startswith('goto:'):
            return

        # Parse the href (format: "goto:fileName:functionName")
        parts = href[5:].split(':')
        if len(parts) == 2:
            file_name, function_name = parts
            self._goto_definition(view, file_name, function_name)
        else:
            # Single word goto
            self._goto_definition(view, parts[0], None)

    def _goto_definition(self, view, file_or_function, function_name=None):
        """Navigate to the definition of a function or file"""
        window = view.window()
        if not window:
            return

        if function_name:
            # Pattern: fileName.functionName
            # Search for fileName.groovy and look for functionName in it
            self._find_function_in_files(window, file_or_function, function_name)
        else:
            # Single word: check current file first, then look for file
            if self._find_function_in_current_file(view, file_or_function):
                return
            # Look for a file with this name
            self._find_and_open_file(window, file_or_function)

    def _find_function_in_current_file(self, view, function_name):
        """Search for function definition in the current file"""
        content = view.substr(sublime.Region(0, view.size()))

        # Regex to match Groovy function declarations
        # Matches: def functionName(...) { or void functionName(...) {
        pattern = r'\b(?:def|void|String|int|boolean|Object|[\w<>]+)\s+{0}\s*\([^{{}}]*?\)\s*\{{'.format(
            re.escape(function_name)
        )

        match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
        if match:
            # Calculate line number
            line_num = content[:match.start()].count('\n')
            point = view.text_point(line_num, 0)

            # Move cursor and center view
            view.sel().clear()
            view.sel().add(sublime.Region(point))
            view.show_at_center(point)
            return True

        return False

    def _find_function_in_files(self, window, file_name, function_name):
        """Search for function definition across .groovy files"""
        # Get all .groovy files in the project
        folders = window.folders()
        if not folders:
            sublime.status_message("No project folder open")
            return

        # Search for the file
        for folder in folders:
            groovy_files = []
            for root, dirs, files in os.walk(folder):
                for file in files:
                    if file.endswith('.groovy') or file == file_name + '.groovy':
                        groovy_files.append(os.path.join(root, file))

            # Search in each groovy file
            for file_path in groovy_files:
                if self._find_and_open_function_in_file(window, file_path, function_name):
                    return

        sublime.status_message("Definition not found: {0} in {1}.groovy".format(
            function_name, file_name
        ))

    def _find_and_open_file(self, window, file_name):
        """Find and open a .groovy file by name"""
        folders = window.folders()
        if not folders:
            sublime.status_message("No project folder open")
            return

        for folder in folders:
            for root, dirs, files in os.walk(folder):
                for file in files:
                    if file == file_name + '.groovy' or file == file_name:
                        file_path = os.path.join(root, file)
                        window.open_file(file_path)
                        return

        sublime.status_message("File not found: {0}.groovy".format(file_name))

    def _find_and_open_function_in_file(self, window, file_path, function_name):
        """Open file and navigate to function definition"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Search for function definition
            pattern = r'\b(?:def|void|String|int|boolean|Object|[\w<>]+)\s+{0}\s*\([^{{}}]*?\)\s*\{{'.format(
                re.escape(function_name)
            )

            match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
            if match:
                line_num = content[:match.start()].count('\n')
                # Open file at the specific line
                window.open_file(
                    "{0}:{1}:0".format(file_path, line_num + 1),
                    sublime.ENCODED_POSITION
                )
                return True
        except Exception as e:
            print("Error reading file {0}: {1}".format(file_path, str(e)))

        return False


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
""".format(version=__version__)

        sublime.message_dialog(message)


class JenkinsDocReloadCommand(sublime_plugin.WindowCommand):
    """Reload Jenkins Documentation plugin settings and data"""

    def run(self):
        """Reload settings and data"""
        global jenkins_data, settings

        # Reload settings
        settings = sublime.load_settings('JenkinsDoc.sublime-settings')

        # Reload data
        jenkins_data = load_jenkins_data()

        # Show status
        if jenkins_data:
            plugin_count = len(jenkins_data.get('plugins', []))
            instruction_count = len(jenkins_data.get('instructions', []))
            sublime.status_message("JenkinsDoc: Reloaded {} plugins with {} instructions".format(
                plugin_count, instruction_count
            ))
            if settings.get('show_console_messages', True):
                print("JenkinsDoc: Reloaded {} plugins with {} instructions".format(
                    plugin_count, instruction_count
                ))
        else:
            sublime.status_message("JenkinsDoc: Failed to reload data")
            if settings.get('show_console_messages', True):
                print("JenkinsDoc: Failed to reload data")
