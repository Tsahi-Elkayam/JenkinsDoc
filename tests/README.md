# Tests

Test suite for the JenkinsDoc plugin. Currently at 110 tests, all passing.

Tests cover:
- File detection (Jenkinsfile, .groovy files)
- Autocompletion
- Hover docs
- Go-to-definition
- Status bar
- Commands and settings

## Test Structure

```
tests/
├── helpers/              # Shared test utilities
│   ├── __init__.py      # Package exports
│   └── mocks.py         # Mock objects for Sublime Text API
├── unit/                # Unit tests (68 tests)
│   ├── test_commands.py    # Command classes
│   ├── test_listeners.py   # Listener classes
│   └── test_utils.py       # Utility functions
├── integration/         # Integration tests (17 tests)
│   ├── test_completions.py      # Completion workflows
│   ├── test_file_detection.py   # File detection logic
│   └── test_hover.py            # Hover documentation
├── validation/          # Validation tests (19 tests)
│   ├── test_commands_registry.py  # Command registration
│   ├── test_documentation.py      # Code documentation
│   ├── test_menu_items.py         # Menu configuration
│   └── test_schema.py             # Settings schema
├── quality/             # Code quality tests (6 tests)
│   ├── test_formatting.py  # Code formatting (black, isort)
│   ├── test_linting.py     # Linting (flake8)
│   └── test_security.py    # Security scanning (bandit)
└── run_tests.py         # Test runner script
```

## Running Tests

Run everything:
```bash
python tests/run_tests.py
```

Run by category:
```bash
python tests/run_tests.py unit
python tests/run_tests.py integration
python tests/run_tests.py validation
python tests/run_tests.py quality       # needs black, isort, flake8, bandit
```

Run single file:
```bash
python tests/unit/test_utils.py
```

Run specific test:
```bash
python -m unittest tests.unit.test_utils.TestIsJenkinsFile.test_jenkinsfile_by_name
```

## What's Tested

**Unit (68 tests)** - test_commands.py, test_listeners.py, test_utils.py
- Commands (diagnostics, reload, etc)
- Listeners (status bar, hover, completions, go-to-def)
- Utils (file detection, data loading)

**Integration (17 tests)** - test_completions.py, test_file_detection.py, test_hover.py
- Completion workflows
- File pattern detection
- Hover doc lookups

**Validation (19 tests)** - test_commands_registry.py, test_documentation.py, test_menu_items.py, test_schema.py
- Command registry checks
- Docstring presence
- Menu/settings validation

**Quality (6 tests)** - test_formatting.py, test_linting.py, test_security.py
- Code formatting (black, isort)
- Linting (flake8)
- Security (bandit, hardcoded secrets)

Note: Quality tests need extra tools installed or they'll just skip.

## Known Issues

Sometimes tests fail when run all together but pass individually. This is a mock state issue. Make sure you're calling `reset_mock()` in setUp if you notice this.

Quality tests need optional tools. Install with:
```bash
pip install black isort flake8 bandit
```

## Debugging

Add `-v` for verbose output:
```bash
python tests/run_tests.py -v
```

Or just throw in print statements - they'll show up in the test output.
