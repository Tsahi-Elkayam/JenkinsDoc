"""
Code quality tests - Linting
Runs flake8 and pylint as tests
"""

import os
import subprocess
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))


class TestLinting(unittest.TestCase):
    """Run linting tools as tests"""

    @classmethod
    def setUpClass(cls):
        """Get plugin directory"""
        cls.plugin_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

    def test_flake8_critical_errors(self):
        """Test for critical Python syntax errors with flake8"""
        try:
            result = subprocess.run(
                [
                    "flake8",
                    ".",
                    "--count",
                    "--select=E9,F63,F7,F82",
                    "--show-source",
                    "--statistics",
                    "--exclude=venv,ENV,env,__pycache__,.git",
                ],
                cwd=self.plugin_dir,
                capture_output=True,
                text=True,
                timeout=30,
            )

            # Should have no critical errors
            self.assertEqual(result.returncode, 0, f"Critical flake8 errors found:\n{result.stdout}\n{result.stderr}")

        except FileNotFoundError:
            self.skipTest("flake8 not installed")
        except subprocess.TimeoutExpired:
            self.fail("flake8 timed out")

    def test_flake8_style_warnings(self):
        """Test for style issues with flake8 (non-blocking)"""
        try:
            result = subprocess.run(
                [
                    "flake8",
                    ".",
                    "--count",
                    "--max-complexity=15",
                    "--max-line-length=120",
                    "--statistics",
                    "--exclude=venv,ENV,env,__pycache__,.git",
                ],
                cwd=self.plugin_dir,
                capture_output=True,
                text=True,
                timeout=30,
            )

            # This is informational - we just print warnings
            if result.returncode != 0:
                print(f"\nStyle warnings from flake8:\n{result.stdout}")

        except FileNotFoundError:
            self.skipTest("flake8 not installed")
        except subprocess.TimeoutExpired:
            self.skipTest("flake8 timed out")


if __name__ == "__main__":
    unittest.main()
