#!/usr/bin/env python3
"""
Simple test runner for JenkinsDoc tests

Usage:
    python run_tests.py              # Run all tests
    python run_tests.py unit         # Run only unit tests
    python run_tests.py integration  # Run only integration tests
    python run_tests.py validation   # Run only validation tests
    python run_tests.py quality      # Run only quality tests
"""

import sys
import os
import unittest

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))


def run_tests(category=None):
    """Run tests for specified category or all tests"""
    tests_dir = os.path.dirname(os.path.realpath(__file__))

    # Determine which tests to run
    if category:
        if category not in ['unit', 'integration', 'validation', 'quality']:
            print(f"Error: Unknown category '{category}'")
            print("Valid categories: unit, integration, validation, quality")
            return False

        test_path = os.path.join(tests_dir, category)
        if not os.path.exists(test_path):
            print(f"Error: No tests found in {category}/")
            return False

        print(f"\nRunning {category.upper()} tests...\n")
        print("=" * 70)
    else:
        test_path = tests_dir
        print("\nRunning ALL tests...\n")
        print("=" * 70)

    # Discover and load tests
    loader = unittest.TestLoader()
    suite = loader.discover(test_path, pattern='test_*.py')

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Tests run:  {result.testsRun}")
    print(f"Passed:     {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failed:     {len(result.failures)}")
    print(f"Errors:     {len(result.errors)}")
    print(f"Skipped:    {len(result.skipped)}")

    if result.wasSuccessful():
        print("\n[PASS] All tests passed!")
    else:
        print("\n[FAIL] Some tests failed")

    print("=" * 70)

    return result.wasSuccessful()


def main():
    category = sys.argv[1] if len(sys.argv) > 1 else None

    # Show help
    if category in ['-h', '--help', 'help']:
        print(__doc__)
        return 0

    # Run tests
    success = run_tests(category)

    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
