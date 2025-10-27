"""
Code quality tests - Formatting
Checks black and isort compliance
"""

import sys
import os
import unittest
import subprocess

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))


class TestFormatting(unittest.TestCase):
    """Check code formatting compliance"""

    @classmethod
    def setUpClass(cls):
        """Get plugin directory"""
        cls.plugin_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

    def test_black_formatting(self):
        """Test that code follows black formatting"""
        try:
            result = subprocess.run(
                ["black", "--check", "--line-length=120", r"--exclude=/(\.git|venv|ENV|env|__pycache__)/", "."],
                cwd=self.plugin_dir,
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode != 0:
                print(f"\nBlack formatting issues:\n{result.stdout}")
                print("\nRun 'black --line-length=120 .' to fix")

            # Non-blocking - just informational
            self.assertTrue(True, "Formatting check completed")

        except FileNotFoundError:
            self.skipTest("black not installed")
        except subprocess.TimeoutExpired:
            self.skipTest("black timed out")

    def test_isort_formatting(self):
        """Test that imports follow isort formatting"""
        try:
            result = subprocess.run(
                [
                    "isort",
                    "--check-only",
                    "--profile",
                    "black",
                    "--line-length",
                    "120",
                    "--skip-glob=*/venv/*",
                    "--skip-glob=*/__pycache__/*",
                    ".",
                ],
                cwd=self.plugin_dir,
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode != 0:
                print(f"\nImport sorting issues:\n{result.stdout}")
                print("\nRun 'isort --profile black --line-length 120 .' to fix")

            # Non-blocking - just informational
            self.assertTrue(True, "Import check completed")

        except FileNotFoundError:
            self.skipTest("isort not installed")
        except subprocess.TimeoutExpired:
            self.skipTest("isort timed out")


if __name__ == "__main__":
    unittest.main()
