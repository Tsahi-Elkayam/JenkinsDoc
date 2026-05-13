"""
Utility functions for the JenkinsDoc plugin.
Handles data loading, file detection, and completion generation.
"""

import fnmatch
import json
import os

import sublime

from .log import LOG

# Module-level variables for jenkins data and settings
_jenkins_data = None
_settings = None
_priority_snippets = None


def get_jenkins_data():
    """Get the cached jenkins data"""
    return _jenkins_data


def set_jenkins_data(data):
    """Set the jenkins data cache"""
    global _jenkins_data
    _jenkins_data = data


def get_settings():
    """Get the cached settings"""
    return _settings


def set_settings(settings):
    """Set the settings cache"""
    global _settings
    _settings = settings


def get_priority_snippets():
    """Return cached priority snippets mapping {command: snippet}."""
    return _priority_snippets or {}


def _data_dir():
    return os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "data")


def _load_json(filename, fallback):
    path = os.path.join(_data_dir(), filename)
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        LOG.error("failed to load %s - %s", filename, e)
        return fallback


def load_jenkins_data(settings):
    """Load Jenkins documentation data from JSON file"""
    global _priority_snippets
    data_file = settings.get("data_file", "jenkins_data.json") if settings else "jenkins_data.json"
    snippets_file = (
        settings.get("priority_snippets_file", "priority_snippets.json") if settings else "priority_snippets.json"
    )

    _priority_snippets = _load_json(snippets_file, {})

    return _load_json(
        data_file,
        {"plugins": [], "instructions": [], "sections": [], "directives": [], "environmentVariables": []},
    )


def is_jenkins_file(view, settings):
    """Check if the current file is a Groovy or Jenkinsfile"""
    if not settings or not settings.get("enabled", True):
        return False

    syntax = view.syntax()
    file_name = view.file_name() or ""
    base_name = os.path.basename(file_name)

    # Check if it's a Groovy file by syntax
    if settings.get("detect_groovy_files", True) and syntax and "groovy" in syntax.scope.lower():
        return True

    # Check if it's a Jenkinsfile (with or without extension)
    if settings.get("detect_jenkinsfile", True):
        if "Jenkinsfile" in base_name or base_name == "Jenkinsfile":
            return True

    # Check additional file patterns
    additional_patterns = settings.get("additional_file_patterns", [])
    for pattern in additional_patterns:
        # Try matching against both full path and basename
        if fnmatch.fnmatch(file_name, pattern) or fnmatch.fnmatch(base_name, pattern):
            return True

    return False
