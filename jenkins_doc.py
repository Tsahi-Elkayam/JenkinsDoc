import sublime
import sublime_plugin
import json
import os
import re

def plugin_loaded():
    """Load plugin data when Sublime starts"""
    global jenkins_data
    jenkins_data = load_jenkins_data()

def load_jenkins_data():
    """Load Jenkins documentation data from JSON file"""
    plugin_path = os.path.dirname(os.path.realpath(__file__))
    data_path = os.path.join(plugin_path, 'jenkins_data.json')

    with open(data_path, 'r', encoding='utf-8') as f:
        return json.load(f)

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

        syntax = view.syntax()
        if not syntax or 'groovy' not in syntax.scope.lower():
            return

        word_region = view.word(point)
        if not word_region:
            return

        word = view.substr(word_region)

        doc = self._find_documentation(word)
        if doc:
            wrapped_doc = "{0}<div class='container'>{1}</div>".format(self.css, doc)
            view.show_popup(wrapped_doc,
                          flags=sublime.HIDE_ON_MOUSE_MOVE_AWAY,
                          location=point,
                          max_width=800,
                          max_height=500)

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
                html += """
                    <li>
                        <div>
                            <span class="param-name">{0}</span>
                            <span class="param-type">{1}</span>
                            <span class="param-optional">{2}</span>
                        </div>
                        <div class="param-desc">{3}</div>
                    </li>
                """.format(param['name'], param['type'], optional, param['description'])
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
        # Only activate for Groovy files and Jenkinsfiles
        syntax = view.syntax()
        if not syntax or 'groovy' not in syntax.scope.lower():
            return None

        completions = []

        # Get current line up to cursor
        point = locations[0]
        line_region = view.line(point)
        line_start = line_region.begin()
        line_up_to_cursor = view.substr(sublime.Region(line_start, point))

        # Check if we're after 'env.'
        if 'env.' in line_up_to_cursor:
            return (self._get_env_completions(), sublime.INHIBIT_WORD_COMPLETIONS)

        # Check if we're inside a post block
        if self._is_inside_post_block(view, point):
            return (self._get_post_completions(), sublime.INHIBIT_WORD_COMPLETIONS)

        # Add all other completions
        completions.extend(self._get_instruction_completions())
        completions.extend(self._get_section_completions())
        completions.extend(self._get_directive_completions())

        return (completions, sublime.INHIBIT_WORD_COMPLETIONS)

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

    def _get_env_completions(self):
        """Get completions for environment variables"""
        return [
            ["{0}\tEnvironment Variable".format(var['name']), var['name']]
            for var in jenkins_data['environmentVariables']
        ]

    def _get_section_completions(self):
        """Get completions for Jenkins sections"""
        return [
            ["{0}\tJenkins Section".format(section['name']),
             "{0} {{\n\t$0\n}}".format(section['name'])]
            for section in jenkins_data['sections']
        ]

    def _get_directive_completions(self):
        """Get completions for Jenkins directives"""
        return [
            ["{0}\tJenkins Directive".format(directive['name']),
             "{0} {{\n\t$0\n}}".format(directive['name'])]
            for directive in jenkins_data['directives']
        ]

    def _get_post_completions(self):
        """Get completions for post conditions"""
        post_conditions = ['always', 'changed', 'fixed', 'regression', 'aborted',
                         'failure', 'success', 'unstable', 'unsuccessful', 'cleanup']

        return [
            ["{0}\tPost Condition".format(condition),
             "{0} {{\n\t$0\n}}".format(condition)]
            for condition in post_conditions
        ]

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
