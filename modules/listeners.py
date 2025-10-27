"""
Event listeners for the JenkinsDoc plugin.
Handles autocompletion, hover documentation, status bar, and go-to-definition.
"""

import html
import os
import re

import sublime
import sublime_plugin

from .utils import get_jenkins_data, get_settings, is_jenkins_file


class JenkinsDocStatusBar(sublime_plugin.EventListener):
    """Show JenkinsDoc status in the status bar"""

    def __init__(self):
        self._last_update = {}  # view_id -> timestamp
        self._throttle_ms = 500  # Minimum time between updates in milliseconds

    def _should_update(self, view):
        """Check if enough time has passed since last update for this view"""
        import time

        view_id = view.id()
        now = time.time()

        if view_id in self._last_update:
            time_since_last = (now - self._last_update[view_id]) * 1000  # Convert to ms
            if time_since_last < self._throttle_ms:
                return False

        self._last_update[view_id] = now
        return True

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
        if command_name == "set_file_type":
            self._update_status(view)

    def on_post_save(self, view):
        """Update status bar after saving (in case filename changes)"""
        self._update_status(view)

    def _update_status(self, view):
        """Update the status bar based on file type"""
        # Throttle updates to avoid excessive work
        if not self._should_update(view):
            return

        settings = get_settings()
        if not settings or not settings.get("show_status_bar", True):
            view.erase_status("jenkins_doc")
            return

        if is_jenkins_file(view, settings):
            # Check if data is loaded
            jenkins_data = get_jenkins_data()
            if jenkins_data and jenkins_data.get("instructions"):
                # Build status text from settings
                status_text = settings.get("status_bar_text", "JenkinsDoc")
                if settings.get("show_instruction_count", False):
                    count = len(jenkins_data.get("instructions", []))
                    status_text = "{} ({} steps)".format(status_text, count)
                view.set_status("jenkins_doc", status_text)
            else:
                # Show error state if no data loaded
                status_text = settings.get("status_bar_text", "JenkinsDoc")
                view.set_status("jenkins_doc", "{} (no data)".format(status_text))
        else:
            # Clear status for non-Jenkins files
            view.erase_status("jenkins_doc")


class JenkinsDocHoverCommand(sublime_plugin.EventListener):
    """Show documentation on hover for Jenkins Pipeline keywords"""

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
        """Show documentation on hover"""
        if hover_zone != sublime.HOVER_TEXT:
            return

        settings = get_settings()
        if not settings or not settings.get("show_hover_docs", True):
            return

        if not is_jenkins_file(view, settings):
            return

        word_region = view.word(point)
        if not word_region:
            return

        word = view.substr(word_region)
        jenkins_data = get_jenkins_data()

        doc = self._find_documentation(word, jenkins_data)
        if doc:
            wrapped_doc = "{0}<div class='container'>{1}</div>".format(self.css, doc)
            max_width = settings.get("hover_popup_max_width", 800)
            max_height = settings.get("hover_popup_max_height", 500)
            view.show_popup(
                wrapped_doc,
                flags=sublime.HIDE_ON_MOUSE_MOVE_AWAY,
                location=point,
                max_width=max_width,
                max_height=max_height,
            )

    def _find_documentation(self, word, jenkins_data):
        """Find documentation for the given word using O(1) lookup"""
        if not jenkins_data:
            return None

        # Use lookup indices if available (O(1)), fallback to O(n) search if not
        if "_lookup" in jenkins_data:
            lookup = jenkins_data["_lookup"]

            if word in lookup["instructions"]:
                return self._format_instruction_doc(lookup["instructions"][word])
            if word in lookup["environmentVariables"]:
                return self._format_env_var_doc(lookup["environmentVariables"][word])
            if word in lookup["sections"]:
                return self._format_section_doc(lookup["sections"][word])
            if word in lookup["directives"]:
                return self._format_directive_doc(lookup["directives"][word])
        else:
            # Fallback to linear search if indices not built
            for instruction in jenkins_data.get("instructions", []):
                if instruction["command"] == word:
                    return self._format_instruction_doc(instruction)

            for env_var in jenkins_data.get("environmentVariables", []):
                if env_var["name"] == word:
                    return self._format_env_var_doc(env_var)

            for section in jenkins_data.get("sections", []):
                if section["name"] == word:
                    return self._format_section_doc(section)

            for directive in jenkins_data.get("directives", []):
                if directive["name"] == word:
                    return self._format_directive_doc(directive)

        return None

    def _format_instruction_doc(self, instruction):
        """Format instruction documentation as HTML"""
        safe_name = html.escape(instruction["name"])
        safe_description = html.escape(instruction["description"])
        html_output = """<div class="content-wrapper">
                    <h3>{0}</h3>
                    <div class="section-info">Pipeline Step</div>
                    <p>{1}</p></div>""".format(
            safe_name, safe_description
        )

        if instruction["parameters"]:
            html_output += "<h4>Parameters</h4><ul>"
            for param in instruction["parameters"]:
                optional = "(Optional)" if param.get("isOptional") else ""
                safe_param_name = html.escape(param["name"])
                safe_param_type = html.escape(param["type"])
                safe_optional = html.escape(optional)

                # Build parameter documentation with enum values
                param_doc = """
                    <li>
                        <div>
                            <span class="param-name">{0}</span>
                            <span class="param-type">{1}</span>
                            <span class="param-optional">{2}</span>
                        </div>""".format(
                    safe_param_name, safe_param_type, safe_optional
                )

                # Add enum values if present (matching VS Code implementation line 57)
                if param.get("values") and len(param["values"]) > 0:
                    param_doc += "<div style='margin-left: 20px; margin-top: 8px;'><strong>Values:</strong><ul style='margin: 4px 0; padding-left: 20px;'>"
                    for value in param["values"]:
                        safe_value = html.escape(value)
                        param_doc += "<li style='color: #9cdcfe;'>{0}</li>".format(safe_value)
                    param_doc += "</ul></div>"

                # Add parameter description
                safe_param_desc = html.escape(param["description"])
                param_doc += "<div class='param-desc'>{0}</div>".format(safe_param_desc)
                param_doc += "</li>"

                html_output += param_doc
            html_output += "</ul>"

        html_output += "</div>"  # Close content-wrapper

        if instruction.get("url"):
            safe_url = html.escape(instruction["url"])
            html_output += '<a href="{0}" class="doc-link">View Documentation</a>'.format(safe_url)

        return html_output

    def _format_env_var_doc(self, env_var):
        """Format environment variable documentation as HTML"""
        safe_name = html.escape(env_var["name"])
        safe_description = html.escape(env_var["description"])
        return """
            <div class="content-wrapper">
                <h3>{0}</h3>
                <div class="section-info">Environment Variable</div>
                <p>{1}</p>
            </div>
        """.format(
            safe_name, safe_description
        )

    def _format_section_doc(self, section):
        """Format section documentation as HTML"""
        safe_name = html.escape(section["name"])
        safe_description = html.escape(section["description"])
        html_output = """<div class="content-wrapper">
                    <h3>{0}</h3>
                    <div class="section-info">Pipeline Section</div>
                    <p>{1}</p></div>""".format(
            safe_name, safe_description
        )

        if section.get("allowed"):
            safe_allowed = html.escape(section.get("allowed", ""))
            html_output += """<div class="section-info">
                        <span class="type-label">Allowed</span>
                        {0}
                      </div>""".format(
                safe_allowed
            )

        html_output += "</div>"  # Close content-wrapper

        if section.get("url"):
            safe_url = html.escape(section["url"])
            html_output += '<a href="{0}" class="doc-link">View Documentation</a>'.format(safe_url)
        return html_output

    def _format_directive_doc(self, directive):
        """Format directive documentation as HTML"""
        safe_name = html.escape(directive["name"])
        safe_description = html.escape(directive["description"])
        html_output = """<div class="content-wrapper">
                    <h3>{0}</h3>
                    <div class="section-info">Pipeline Directive</div>
                    <p>{1}</p></div>""".format(
            safe_name, safe_description
        )

        if directive.get("allowed"):
            safe_allowed = html.escape(directive.get("allowed", ""))
            html_output += """<div class="section-info">
                        <span class="type-label">Allowed</span>
                        {0}
                      </div>""".format(
                safe_allowed
            )

        html_output += "</div>"  # Close content-wrapper

        if directive.get("url"):
            safe_url = html.escape(directive["url"])
            html_output += '<a href="{0}" class="doc-link">View Documentation</a>'.format(safe_url)
        return html_output


class JenkinsCompletions(sublime_plugin.EventListener):
    """Provide autocompletions for Jenkins keywords"""

    def on_query_completions(self, view, prefix, locations):
        settings = get_settings()
        jenkins_data = get_jenkins_data()

        # Always log when called in debug mode
        if settings and settings.get("debug_mode", False):
            print("=== JenkinsDoc: on_query_completions called ===")
            print("  Prefix: '{}'".format(prefix))
            print("  File: {}".format(view.file_name()))

        try:
            # Check if it's a Jenkins file
            if not is_jenkins_file(view, settings):
                if settings and settings.get("debug_mode", False):
                    print("  Not a Jenkins file - returning None")
                return None

            if settings and settings.get("debug_mode", False):
                print("  Is Jenkins file - building completions")

            # Start with ALL completions
            completions = []

            # Priority/common completions that should always appear first
            priority_commands = {
                "echo": "echo '${1:message}'",
                "sh": "sh '${1:script}'",
                "git": "git url: '${1:url}'",
                "checkout": "checkout scm",
                "stage": "stage('${1:name}') {\n\t${0}\n}",
                "steps": "steps {\n\t${0}\n}",
                "pipeline": "pipeline {\n\t${0}\n}",
                "agent": "agent ${1:any}",
                "node": "node('${1:label}') {\n\t${0}\n}",
                "script": "script {\n\t${0}\n}",
                "bat": "bat '${1:script}'",
                "powershell": "powershell '${1:script}'",
                "pwd": "pwd()",
                "dir": "dir('${1:path}') {\n\t${0}\n}",
                "deleteDir": "deleteDir()",
                "error": "error '${1:message}'",
                "unstable": "unstable '${1:message}'",
                "retry": "retry(${1:3}) {\n\t${0}\n}",
                "timeout": "timeout(time: ${1:1}, unit: '${2:HOURS}') {\n\t${0}\n}",
                "waitUntil": "waitUntil {\n\t${0}\n}",
                "sleep": "sleep ${1:60}",
                "input": "input '${1:Proceed?}'",
                "parallel": "parallel {\n\t${0}\n}",
                "when": "when {\n\t${0}\n}",
                "post": "post {\n\t${0}\n}",
            }

            # Track which commands have been added to avoid duplicates
            added_commands = set()

            # Add priority completions first (these will appear at top)
            for cmd, snippet in priority_commands.items():
                # Only add if it matches the prefix (if there is one)
                if not prefix or cmd.lower().startswith(prefix.lower()):
                    completions.append(["{}\tJenkins".format(cmd), snippet])
                    added_commands.add(cmd.lower())

            # Try to add full completions if data is loaded
            if jenkins_data and jenkins_data.get("instructions"):
                if settings and settings.get("debug_mode", False):
                    print("  Adding {} instructions from jenkins_data".format(len(jenkins_data["instructions"])))

                # Get current context
                point = locations[0]
                line_region = view.line(point)
                line_start = line_region.begin()
                line_up_to_cursor = view.substr(sublime.Region(line_start, point))

                # Check for special contexts
                if re.search(r"env\.\w*$", line_up_to_cursor):
                    # Environment variable completions
                    env_completions = self._get_env_completions(jenkins_data, include_prefix=False)
                    if env_completions:
                        if settings and settings.get("debug_mode", False):
                            print("  Returning {} env completions".format(len(env_completions)))
                        return (env_completions, sublime.INHIBIT_WORD_COMPLETIONS)

                # Add full instruction completions (filtered by prefix)
                # But limit them for very short prefixes to avoid overwhelming
                instruction_completions = self._get_instruction_completions(
                    jenkins_data, settings, prefix, added_commands
                )
                if instruction_completions:
                    # For single character prefixes, limit to avoid too many results
                    if len(prefix) == 1:
                        # Only add first 50 instruction completions for single char
                        completions.extend(instruction_completions[:50])
                    else:
                        # Add all matching completions for longer prefixes
                        completions.extend(instruction_completions)

                # Add sections and directives (only if they match prefix)
                section_completions = []
                for section in jenkins_data.get("sections", []):
                    if not prefix or section["name"].lower().startswith(prefix.lower()):
                        section_completions.append(
                            ["{}\tJenkins Section".format(section["name"]), "{} {{\n\t$0\n}}".format(section["name"])]
                        )
                completions.extend(section_completions)

                directive_completions = []
                for directive in jenkins_data.get("directives", []):
                    if not prefix or directive["name"].lower().startswith(prefix.lower()):
                        directive_completions.append(
                            [
                                "{}\tJenkins Directive".format(directive["name"]),
                                "{} {{\n\t$0\n}}".format(directive["name"]),
                            ]
                        )
                completions.extend(directive_completions)

            # Debug output
            if settings and settings.get("debug_mode", False):
                print("  Total completions: {}".format(len(completions)))
                if len(completions) > 0:
                    print("  First 3 completions:")
                    for c in completions[:3]:
                        print("    - {}".format(c[0]))

            # Return completions
            if completions:
                return (completions, sublime.INHIBIT_WORD_COMPLETIONS)
            else:
                if settings and settings.get("debug_mode", False):
                    print("  No completions - returning None")
                return None

        except Exception as e:
            print("JenkinsDoc ERROR in on_query_completions: {}".format(str(e)))
            import traceback

            traceback.print_exc()
            # Return basic completions on error
            return (
                [
                    ["echo\tJenkins", "echo '${1:message}'"],
                    ["sh\tJenkins", "sh '${1:script}'"],
                    ["pipeline\tJenkins", "pipeline {\n\t${0}\n}"],
                ],
                sublime.INHIBIT_WORD_COMPLETIONS,
            )

    def _get_instruction_completions(self, jenkins_data, settings, prefix="", added_commands=None):
        """Get completions for Jenkins instructions

        Args:
            jenkins_data: The Jenkins data dictionary
            settings: Plugin settings
            prefix: Prefix filter for completions
            added_commands: Set of command names already added (to avoid duplicates)
        """
        completions = []
        if added_commands is None:
            added_commands = set()

        if not jenkins_data or not jenkins_data.get("instructions"):
            if settings and settings.get("debug_mode", False):
                print("JenkinsDoc: No instructions data available")
            return completions

        # Filter by prefix if provided
        for instruction in jenkins_data["instructions"]:
            command = instruction["command"]

            # Skip if already added (e.g., as priority command)
            if command.lower() in added_commands:
                continue

            # Skip if doesn't match prefix
            if prefix and not command.lower().startswith(prefix.lower()):
                continue

            if instruction.get("parameters"):
                contents = "{0}(${{1}})".format(command)
            else:
                contents = "{0}()".format(command)

            completions.append(["{0}\tJenkins Step".format(command), contents])
            added_commands.add(command.lower())

        if settings and settings.get("debug_mode", False):
            print("JenkinsDoc: Created {} instruction completions (filtered by '{}')".format(len(completions), prefix))
        return completions

    def _get_env_completions(self, jenkins_data, include_prefix=False):
        """Get completions for environment variables

        Args:
            include_prefix: If True, insert "env.NAME". If False, insert just "NAME".
                           False is used when user has already typed "env."
        """
        completions = []
        if not jenkins_data:
            return completions
        for var in jenkins_data.get("environmentVariables", []):
            if include_prefix:
                # When not after "env.", insert full "env.NAME"
                trigger = "{0}\tEnvironment Variable".format(var["name"])
                contents = "env.{0}".format(var["name"])
            else:
                # When after "env.", insert just the variable name to avoid duplication
                trigger = "{0}\tEnvironment Variable".format(var["name"])
                contents = var["name"]

            completions.append([trigger, contents])

        return completions

    def _get_section_completions(self, jenkins_data):
        """Get completions for Jenkins sections

        TODO: This method is currently unused but tested. Consider integrating
        into on_query_completions for context-aware section suggestions.
        """
        completions = []
        if not jenkins_data:
            return completions
        for section in jenkins_data.get("sections", []):
            # Check if section has inner instructions
            if section.get("innerInstructions"):
                # Add hint about available inner instructions
                inner_list = ", ".join(section["innerInstructions"][:3])
                if len(section["innerInstructions"]) > 3:
                    inner_list += "..."
                trigger = "{0}\tJenkins Section ({1})".format(section["name"], inner_list)
                # Add a comment hint in the snippet
                contents = "{0} {{\n\t${{1:// {1}}}\n}}".format(
                    section["name"], ", ".join(section["innerInstructions"])
                )
            else:
                trigger = "{0}\tJenkins Section".format(section["name"])
                contents = "{0} {{\n\t$0\n}}".format(section["name"])

            completions.append([trigger, contents])
        return completions

    def _get_directive_completions(self, jenkins_data):
        """Get completions for Jenkins directives

        TODO: This method is currently unused but tested. Consider integrating
        into on_query_completions for context-aware directive suggestions.
        """
        completions = []
        if not jenkins_data:
            return completions
        for directive in jenkins_data.get("directives", []):
            # Check if directive has inner instructions
            if directive.get("innerInstructions"):
                # Add hint about available inner instructions
                inner_list = ", ".join(directive["innerInstructions"][:3])
                if len(directive["innerInstructions"]) > 3:
                    inner_list += "..."
                trigger = "{0}\tJenkins Directive ({1})".format(directive["name"], inner_list)
                # Add a comment hint in the snippet
                contents = "{0} {{\n\t${{1:// {1}}}\n}}".format(
                    directive["name"], ", ".join(directive["innerInstructions"])
                )
            else:
                trigger = "{0}\tJenkins Directive".format(directive["name"])
                contents = "{0} {{\n\t$0\n}}".format(directive["name"])

            completions.append([trigger, contents])
        return completions

    def _get_post_completions(self, jenkins_data):
        """Get completions for post conditions

        TODO: This method is currently unused but tested. Consider integrating
        into on_query_completions when inside post{} blocks.
        """
        # Extract post conditions from jenkins_data
        if not jenkins_data:
            return []
        post_section = next((s for s in jenkins_data.get("sections", []) if s["name"] == "post"), None)

        if not post_section or not post_section.get("innerInstructions"):
            # Fallback to hardcoded values if data not found
            post_conditions = [
                "always",
                "changed",
                "fixed",
                "regression",
                "aborted",
                "failure",
                "success",
                "unstable",
                "unsuccessful",
                "cleanup",
            ]
        else:
            post_conditions = post_section["innerInstructions"]

        return [
            ["{0}\tPost Condition".format(condition), "{0} {{\n\t$0\n}}".format(condition)]
            for condition in post_conditions
        ]

    def _get_parameter_completions(self, jenkins_data, line_up_to_cursor):
        """Get parameter completions when inside a function call

        TODO: This method is currently unused but tested. Consider integrating
        into on_query_completions to provide parameter hints inside function calls.
        """
        # Match pattern like "functionName(" or "functionName(param1: 'value', "
        # Get the first word preceding a space or parenthesis, after the last opening brace
        match = re.search(r"{{?\s*(\w+)\s*[( ](?!.*[\{{(])", line_up_to_cursor)
        if not match:
            return []

        function_name = match.group(1)

        # Find the instruction by command name
        if not jenkins_data:
            return []
        instruction = next((i for i in jenkins_data.get("instructions", []) if i["command"] == function_name), None)

        if not instruction or not instruction.get("parameters"):
            return []

        # Build parameter completions
        completions = []
        for param in instruction["parameters"]:
            optional_label = "(Optional)" if param.get("isOptional") else ""
            param_type = param.get("type", "Unknown")

            # Build the description
            desc_parts = []
            if param.get("values"):
                desc_parts.append("Values: " + ", ".join(param["values"]))
            if param.get("description"):
                desc_parts.append(param["description"])
            description = " - ".join(desc_parts) if desc_parts else ""

            # Build the insertion text based on type
            if param_type == "String":
                insert_text = "{0}: '${{1}}'".format(param["name"])
            elif param_type == "boolean":
                insert_text = "{0}: ${{1:true}}".format(param["name"])
            elif param_type == "Enum" and param.get("values"):
                # For enum, just provide the parameter name and let user type
                # Sublime doesn't support choice snippets like VS Code
                insert_text = "{0}: '${{1}}'".format(param["name"])
            else:
                insert_text = "{0}: ".format(param["name"])

            # Format: [trigger\tDescription, contents]
            trigger = "{0}\t{1} {2}".format(param["name"], param_type, optional_label)
            completions.append([trigger, insert_text])

        return completions

    def _is_inside_post_block(self, view, point):
        """Check if cursor is inside a post{} block

        TODO: This method is currently unused but tested. Consider using with
        _get_post_completions to provide context-aware suggestions in post blocks.
        """
        # Search backwards for 'post {'
        content = view.substr(sublime.Region(0, point))
        post_matches = list(re.finditer(r"\bpost\s*\{", content))
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
            if char == "{":
                brace_count += 1
            elif char == "}":
                brace_count -= 1
            pos += 1

        return brace_count > 0


class JenkinsGoToDefinitionCommand(sublime_plugin.EventListener):
    """Provide go-to-definition functionality for Groovy functions"""

    def __init__(self):
        self._file_cache = {}  # folder_path -> list of groovy files
        self._cache_time = {}  # folder_path -> timestamp
        self._cache_ttl = 60  # Cache TTL in seconds

    def _get_groovy_files(self, folder):
        """Get cached list of groovy files or rebuild cache"""
        import time

        now = time.time()

        # Check if cache is still valid
        if folder in self._cache_time:
            if now - self._cache_time[folder] < self._cache_ttl:
                return self._file_cache[folder]

        # Rebuild cache
        groovy_files = []
        for root, dirs, files in os.walk(folder):
            # Skip common non-code directories for performance
            dirs[:] = [d for d in dirs if d not in {".git", "node_modules", "__pycache__", ".venv", "venv"}]

            for file in files:
                if file.endswith(".groovy"):
                    groovy_files.append(os.path.join(root, file))

        self._file_cache[folder] = groovy_files
        self._cache_time[folder] = now

        return groovy_files

    def on_hover(self, view, point, hover_zone):
        """Show definition link on hover"""
        if hover_zone != sublime.HOVER_TEXT:
            return

        settings = get_settings()
        if not settings or not settings.get("enable_goto_definition", True):
            return

        if not is_jenkins_file(view, settings):
            return

        # Check if Ctrl/Cmd is pressed (for goto definition hint)
        # Provide the definition link in the popup
        word_region = view.word(point)
        if not word_region:
            return

        word = view.substr(word_region)

        # Expand to capture object.method pattern
        extended_region = view.expand_by_class(point, sublime.CLASS_WORD_START | sublime.CLASS_WORD_END, "._")
        extended_word = view.substr(extended_region)

        # Only show for word.word pattern (like fileName.functionName)
        if "." in extended_word:
            parts = extended_word.split(".")
            if len(parts) == 2:
                file_name, function_name = parts
                # Check if we should show popup
                if settings and settings.get("show_goto_popup", True):
                    # Show a hint that definition can be navigated
                    link_html = '<a href="goto:{0}:{1}">Go to definition of {2}</a>'.format(
                        file_name, function_name, extended_word
                    )
                    view.show_popup(
                        link_html,
                        flags=sublime.HIDE_ON_MOUSE_MOVE_AWAY,
                        location=point,
                        on_navigate=lambda href: self._handle_goto(view, href),
                    )

    def _handle_goto(self, view, href):
        """Handle goto definition navigation"""
        if not href.startswith("goto:"):
            return

        # Parse the href (format: "goto:fileName:functionName")
        parts = href[5:].split(":")
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
        pattern = r"\b(?:def|void|String|int|boolean|Object|[\w<>]+)\s+{0}\s*\([^{{}}]*?\)\s*\{{".format(
            re.escape(function_name)
        )

        match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
        if match:
            # Calculate line number
            line_num = content[: match.start()].count("\n")
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
            # Use cached file list instead of os.walk()
            groovy_files = self._get_groovy_files(folder)

            # Search in each groovy file
            for file_path in groovy_files:
                if file_name in os.path.basename(file_path):
                    if self._find_and_open_function_in_file(window, file_path, function_name):
                        return

        sublime.status_message("Definition not found: {0} in {1}.groovy".format(function_name, file_name))

    def _find_and_open_file(self, window, file_name):
        """Find and open a .groovy file by name"""
        folders = window.folders()
        if not folders:
            sublime.status_message("No project folder open")
            return

        for folder in folders:
            # Use cached file list instead of os.walk()
            groovy_files = self._get_groovy_files(folder)

            for file_path in groovy_files:
                base_name = os.path.basename(file_path)
                if base_name == file_name + ".groovy" or base_name == file_name:
                    window.open_file(file_path)
                    return

        sublime.status_message("File not found: {0}.groovy".format(file_name))

    def _find_and_open_function_in_file(self, window, file_path, function_name):
        """Open file and navigate to function definition"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Search for function definition
            pattern = r"\b(?:def|void|String|int|boolean|Object|[\w<>]+)\s+{0}\s*\([^{{}}]*?\)\s*\{{".format(
                re.escape(function_name)
            )

            match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
            if match:
                line_num = content[: match.start()].count("\n")
                # Open file at the specific line
                window.open_file("{0}:{1}:0".format(file_path, line_num + 1), sublime.ENCODED_POSITION)
                return True
        except Exception as e:
            print("Error reading file {0}: {1}".format(file_path, str(e)))

        return False
