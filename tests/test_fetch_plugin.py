import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent.parent
WRAPPER = r'''
import io, os, runpy, sys, urllib.request
class Opener:
    def open(self, url, timeout):
        with open(os.environ['CALLS'], 'a') as f: f.write(url + '\n')
        name = url.rsplit('/', 1)[-1]
        if os.environ.get('FAIL') == name: raise OSError('private response body')
        data = open(os.path.join(os.environ['FIXTURES'], name), 'rb').read()
        if os.environ.get('BAD') == name: data += b'bad'
        return io.BytesIO(data)
urllib.request.build_opener = lambda *a: Opener()
sys.argv = [sys.argv[1]] + sys.argv[2:]
runpy.run_path(sys.argv[0], run_name='__main__')
'''

class FetchCLI(unittest.TestCase):
    def setUp(self):
        (ROOT / '.state').mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(prefix='bootstrap-tests.', dir=ROOT / '.state')
        self.root = Path(self.temp.name)
        (self.root / 'bin').mkdir()
        shutil.copy(ROOT / 'dependency.json', self.root)
        if (ROOT / 'bin/fetch-plugin').exists():
            shutil.copy(ROOT / 'bin/fetch-plugin', self.root / 'bin')
        self.calls = self.root / 'calls'
        self.env = dict(os.environ, FIXTURES=str(ROOT / '.cache'), CALLS=str(self.calls))

    def tearDown(self):
        self.temp.cleanup()

    def run_cli(self, *args, **env):
        return subprocess.run([sys.executable, '-c', WRAPPER, str(self.root / 'bin/fetch-plugin'), *args], env=dict(self.env, **env), capture_output=True, text=True, timeout=10)

    def test_help_never_downloads(self):
        p = self.run_cli('--help')
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIn('usage:', p.stdout)
        self.assertFalse(self.calls.exists())

    def test_download_and_idempotence(self):
        p = self.run_cli()
        self.assertEqual(p.returncode, 0, p.stderr)
        meta = json.loads((self.root / 'dependency.json').read_text())
        urls = self.calls.read_text().splitlines()
        self.assertEqual(urls, [f"https://raw.githubusercontent.com/zsh-users/zsh-autosuggestions/{meta['revision']}/{name}" for name in ('zsh-autosuggestions.zsh', 'LICENSE')])
        for name in ('zsh-autosuggestions.zsh', 'LICENSE'):
            self.assertEqual((self.root / '.cache' / name).read_bytes(), (ROOT / '.cache' / name).read_bytes())
        self.assertEqual(self.run_cli().returncode, 0)
        self.assertEqual(self.calls.read_text().splitlines(), urls)

    def test_failures_leave_existing_bytes(self):
        cache = self.root / '.cache'
        cache.mkdir()
        for name in ('zsh-autosuggestions.zsh', 'LICENSE'):
            (cache / name).write_bytes(b'old')
        for env in ({'BAD': 'LICENSE'}, {'FAIL': 'LICENSE'}):
            p = self.run_cli(**env)
            self.assertNotEqual(p.returncode, 0)
            self.assertEqual(p.stdout, '')
            self.assertIn('fetch-plugin:', p.stderr)
            self.assertNotIn('private response body', p.stderr)
            for name in ('zsh-autosuggestions.zsh', 'LICENSE'):
                self.assertEqual((cache / name).read_bytes(), b'old')

    def test_symlink_refused(self):
        cache = self.root / '.cache'
        cache.mkdir()
        target = self.root / 'target'
        target.write_bytes(b'unchanged')
        (cache / 'LICENSE').symlink_to(target)
        p = self.run_cli()
        self.assertNotEqual(p.returncode, 0)
        self.assertIn('fetch-plugin:', p.stderr)
        self.assertEqual(target.read_bytes(), b'unchanged')
        self.assertFalse(self.calls.exists())

if __name__ == '__main__':
    unittest.main()
