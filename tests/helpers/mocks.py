"""
Shared test utilities and mocks for JenkinsDoc tests
"""

from unittest.mock import Mock


# Create proper base classes that can be inherited from
class MockEventListener:
    """Mock EventListener base class"""
    pass


class MockTextCommand:
    """Mock TextCommand base class"""
    def __init__(self, view):
        self.view = view


class MockWindowCommand:
    """Mock WindowCommand base class"""
    def __init__(self, window):
        self.window = window


class MockApplicationCommand:
    """Mock ApplicationCommand base class"""
    pass


# Create global mock instances that will be shared across all tests
sublime_mock = Mock()

# Setup sublime constants
sublime_mock.HOVER_TEXT = 1
sublime_mock.HIDE_ON_MOUSE_MOVE_AWAY = 1
sublime_mock.INHIBIT_WORD_COMPLETIONS = 1
sublime_mock.CLASS_WORD_START = 1
sublime_mock.CLASS_WORD_END = 2
sublime_mock.ENCODED_POSITION = 1
sublime_mock.Region = Mock

# Create sublime_plugin mock with base classes
sublime_plugin_mock = Mock()
sublime_plugin_mock.EventListener = MockEventListener
sublime_plugin_mock.TextCommand = MockTextCommand
sublime_plugin_mock.WindowCommand = MockWindowCommand
sublime_plugin_mock.ApplicationCommand = MockApplicationCommand


def setup_sublime_mocks():
    """
    Get the shared Sublime Text mocks for testing.
    Returns tuple of (sublime_mock, sublime_plugin_mock)

    Note: Returns the same instances every time to ensure
    test isolation while maintaining shared mock state.
    """
    return sublime_mock, sublime_plugin_mock
