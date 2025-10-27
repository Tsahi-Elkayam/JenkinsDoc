"""
Code quality tests - Security
Runs bandit security checks
"""

import sys
import os
import unittest
import subprocess

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))


class TestSecurity(unittest.TestCase):
    """Run security checks as tests"""

    @classmethod
    def setUpClass(cls):
        """Get plugin directory"""
        cls.plugin_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

    def test_bandit_security_scan(self):
        """Test for security issues with bandit"""
        try:
            result = subprocess.run(
                ['bandit', '-r', '.',
                 '--exclude', './venv,./ENV,./env,./tests,./.git',
                 '-f', 'screen'],
                cwd=self.plugin_dir,
                capture_output=True,
                text=True,
                timeout=60
            )

            # Bandit returns non-zero if issues found
            if result.returncode != 0:
                print(f"\nSecurity issues found:\n{result.stdout}")

            # Check for high severity issues
            if 'Severity: High' in result.stdout or 'Severity: Medium' in result.stdout:
                self.fail(f"Security issues found:\n{result.stdout}")

        except FileNotFoundError:
            self.skipTest("bandit not installed")
        except subprocess.TimeoutExpired:
            self.skipTest("bandit timed out")

    def test_no_hardcoded_secrets(self):
        """Test that there are no obvious hardcoded secrets"""
        dangerous_patterns = [
            'password =',
            'api_key =',
            'secret =',
            'token ='
        ]

        plugin_files = []
        for root, dirs, files in os.walk(self.plugin_dir):
            # Skip test and venv directories
            dirs[:] = [d for d in dirs if d not in ['venv', 'ENV', 'env', '.git', '__pycache__', 'tests']]

            for file in files:
                if file.endswith('.py'):
                    plugin_files.append(os.path.join(root, file))

        issues = []
        for filepath in plugin_files:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read().lower()
                for pattern in dangerous_patterns:
                    if pattern in content:
                        # Check if it's in a comment
                        lines = content.split('\n')
                        for i, line in enumerate(lines, 1):
                            if pattern in line and not line.strip().startswith('#'):
                                issues.append(f"{filepath}:{i} - Potential secret: {pattern}")

        if issues:
            self.fail(f"Potential hardcoded secrets found:\n" + "\n".join(issues))


if __name__ == '__main__':
    unittest.main()
