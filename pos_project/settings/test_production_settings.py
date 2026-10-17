import json
import os
import subprocess
import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


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
            'import json; from pos_project.settings import production as settings; '
            'print(json.dumps({name: getattr(settings, name) for name in '
            "('SECRET_KEY', 'ALLOWED_HOSTS', 'DEBUG', "
            "'SESSION_COOKIE_SECURE', 'CSRF_COOKIE_SECURE')}))"
        )
        return subprocess.run(
            [sys.executable, '-c', script],
            cwd=PROJECT_ROOT,
            env=env,
            capture_output=True,
            text=True,
        )

    def test_missing_secret_key_fails_clearly(self):
        result = self.load_settings(None, 'example.com')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('ValueError: DJANGO_SECRET_KEY must be set', result.stderr)

    def test_wildcard_host_fails_clearly(self):
        result = self.load_settings('production-secret', '*')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("ValueError: ALLOWED_HOSTS must not contain '*'", result.stderr)

    def test_valid_production_configuration_loads(self):
        result = self.load_settings('production-secret', 'example.com, www.example.com')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), {
            'SECRET_KEY': 'production-secret',
            'ALLOWED_HOSTS': ['example.com', 'www.example.com'],
            'DEBUG': False,
            'SESSION_COOKIE_SECURE': True,
            'CSRF_COOKIE_SECURE': True,
        })


if __name__ == '__main__':
    unittest.main()
