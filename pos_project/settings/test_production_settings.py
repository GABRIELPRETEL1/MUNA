import os
import subprocess
import sys
import unittest
from pathlib import Path


SETTINGS_FILE = Path(__file__).resolve().parents[1] / 'pos_project' / 'settings' / 'production.py'


class ProductionSettingsTests(unittest.TestCase):
    def load_settings(self, secret_key, allowed_hosts):
        env = os.environ.copy()
        env.pop('DJANGO_SETTINGS_MODULE', None)
        env.pop('DJANGO_SECRET_KEY', None)
        env.pop('ALLOWED_HOSTS', None)
        if secret_key is not None:
            env['DJANGO_SECRET_KEY'] = secret_key
        if allowed_hosts is not None:
            env['ALLOWED_HOSTS'] = allowed_hosts
        script = (
            'import importlib.util; '
            f"spec = importlib.util.spec_from_file_location('production_settings', {str(SETTINGS_FILE)!r}); "
            'module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)'
        )
        return subprocess.run(
            [sys.executable, '-c', script],
            env=env,
            capture_output=True,
            text=True,
        )

    def test_missing_secret_key_fails_clearly(self):
        result = self.load_settings(None, 'example.com')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('DJANGO_SECRET_KEY must be set', result.stderr)

    def test_wildcard_host_fails_clearly(self):
        result = self.load_settings('production-secret', '*')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("ALLOWED_HOSTS must not contain '*'", result.stderr)

    def test_valid_production_configuration_loads(self):
        result = self.load_settings('production-secret', 'example.com, www.example.com')
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == '__main__':
    unittest.main()
