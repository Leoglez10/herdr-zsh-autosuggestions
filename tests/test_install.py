"""Installer and loader tests using only synthetic, project-local fixtures."""
import os
from pathlib import Path
import shutil
import stat
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / '.state'
STATE.mkdir(exist_ok=True)


class InstallTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='install-tests.', dir=STATE)
        self.addCleanup(self.tmp.cleanup)
        self.home = Path(self.tmp.name)
        self.project = self.home / 'project'
        for directory in ('bin', '.cache'):
            (self.project / directory).mkdir(parents=True, exist_ok=True)
        for name in ('bin/manage', 'integration.zsh', 'dependency.json',
                     '.cache/zsh-autosuggestions.zsh'):
            source = ROOT / name
            if source.exists():
                shutil.copyfile(source, self.project / name)
        self.rc = self.home / '.zshrc'
        self.env = {'HOME': str(self.home), 'ZDOTDIR': str(self.home),
                    'PATH': '/usr/bin:/bin:/usr/sbin:/sbin', 'TERM': 'xterm'}

    def manage(self, action, rc=None):
        return subprocess.run(['python3', str(self.project / 'bin/manage'), action,
                               '--rc', str(rc or self.rc)], env=self.env,
                              capture_output=True, text=True, timeout=5)

    def test_install_uninstall_idempotent_preserves_bytes_inode_mode_and_edits(self):
        original = b'# synthetic original without final newline'
        self.rc.write_bytes(original)
        self.rc.chmod(0o640)
        inode = self.rc.stat().st_ino
        self.assertEqual(self.manage('install').returncode, 0)
        installed = self.rc.read_bytes()
        self.assertTrue(installed.startswith(original + b'\n'))
        self.assertEqual(self.manage('install').returncode, 0)
        self.assertEqual(self.rc.read_bytes(), installed)
        self.assertEqual(self.manage('status').returncode, 0)
        with self.rc.open('ab') as f:
            f.write(b'# later synthetic edit\n')
        self.assertEqual(self.manage('uninstall').returncode, 0)
        self.assertEqual(self.rc.read_bytes(), original + b'\n# later synthetic edit\n')
        self.assertEqual(self.manage('uninstall').returncode, 0)
        self.assertEqual(self.rc.stat().st_ino, inode)
        self.assertEqual(stat.S_IMODE(self.rc.stat().st_mode), 0o640)

    def test_uninstall_preserves_later_executable_line_boundary(self):
        original = b'# original'
        later = b'export HERDR_LINE_BOUNDARY=kept\n'
        self.rc.write_bytes(original)
        self.rc.chmod(0o640)
        inode = self.rc.stat().st_ino
        self.assertEqual(self.manage('install').returncode, 0)
        with self.rc.open('ab') as f:
            f.write(later)
        script = 'source "$1"; print -r -- "$HERDR_LINE_BOUNDARY"'

        def check_shell():
            result = subprocess.run(['/bin/zsh', '-df', '-c', script, 'zsh', str(self.rc)],
                                    env=self.env, capture_output=True, text=True, timeout=5)
            self.assertEqual((result.returncode, result.stdout, result.stderr), (0, 'kept\n', ''))

        check_shell()
        self.assertEqual(self.manage('uninstall').returncode, 0)
        check_shell()
        self.assertEqual(self.rc.read_bytes(), original + b'\n' + later)
        self.assertEqual(self.rc.stat().st_ino, inode)
        self.assertEqual(stat.S_IMODE(self.rc.stat().st_mode), 0o640)
        self.assertEqual(self.manage('uninstall').returncode, 0)
        self.assertEqual(self.rc.read_bytes(), original + b'\n' + later)

    def test_uninstall_restores_original_without_final_newline(self):
        original = b'# original'
        self.rc.write_bytes(original)
        self.assertEqual(self.manage('install').returncode, 0)
        self.assertEqual(self.manage('uninstall').returncode, 0)
        self.assertEqual(self.rc.read_bytes(), original)

    def test_missing_rc_is_retained_empty_and_missing_parent_rejected(self):
        self.assertEqual(self.manage('install').returncode, 0)
        self.assertEqual(self.manage('uninstall').returncode, 0)
        self.assertEqual(self.rc.read_bytes(), b'')
        missing = self.home / 'missing' / '.zshrc'
        self.assertNotEqual(self.manage('install', missing).returncode, 0)
        self.assertFalse(missing.parent.exists())

    def test_modified_duplicate_and_malformed_blocks_are_never_changed(self):
        self.rc.write_bytes(b'synthetic\n')
        self.assertEqual(self.manage('install').returncode, 0)
        valid = self.rc.read_bytes()
        block = valid[len(b'synthetic\n'):]
        for data in (valid.replace(b'source ', b'source  '), valid + block,
                     valid.replace(b'# <<< herdr-autosuggestions <<<', b'# damaged end')):
            for action in ('install', 'uninstall', 'status'):
                with self.subTest(action=action, data=data):
                    self.rc.write_bytes(data)
                    self.assertNotEqual(self.manage(action).returncode, 0)
                    self.assertEqual(self.rc.read_bytes(), data)

    def test_symlink_and_bad_checksum_leave_data_unchanged(self):
        target = self.home / 'target'
        target.write_bytes(b'synthetic target')
        self.rc.symlink_to(target)
        for action in ('install', 'uninstall', 'status'):
            self.assertNotEqual(self.manage(action).returncode, 0)
            self.assertEqual(target.read_bytes(), b'synthetic target')
            self.assertTrue(self.rc.is_symlink())
        self.rc.unlink()
        self.rc.write_bytes(b'synthetic rc')
        plugin = self.project / '.cache/zsh-autosuggestions.zsh'
        plugin.write_bytes(b'tampered synthetic artifact')
        self.assertNotEqual(self.manage('install').returncode, 0)
        self.assertEqual(self.rc.read_bytes(), b'synthetic rc')
        self.assertEqual(plugin.read_bytes(), b'tampered synthetic artifact')

    def test_nonregular_file_rejected_without_blocking(self):
        os.mkfifo(self.rc)
        for action in ('install', 'uninstall', 'status'):
            self.assertNotEqual(self.manage(action).returncode, 0)
            self.assertTrue(stat.S_ISFIFO(self.rc.lstat().st_mode))

    def test_uninstall_preserves_edits_before_block(self):
        self.rc.write_bytes(b'initial\n')
        self.assertEqual(self.manage('install').returncode, 0)
        self.rc.write_bytes(b'edited before\n' + self.rc.read_bytes())
        self.assertEqual(self.manage('uninstall').returncode, 0)
        self.assertEqual(self.rc.read_bytes(), b'edited before\ninitial\n')

    def shell(self, interactive, markers, script):
        env = dict(self.env, **markers)
        return subprocess.run(['/bin/zsh', '-dfi' if interactive else '-df', '-c', script],
                              env=env, capture_output=True, text=True, timeout=5)

    def test_loader_guards_settings_and_existing_plugin(self):
        source = 'source ' + str(self.project / 'integration.zsh') + '; '
        query = '(( $+functions[_zsh_autosuggest_start] )) && print loaded || print absent'
        core = {'HC_TERMINAL_ID': 'synthetic-id', 'HC_TERMINAL_SOCKET': 'synthetic-socket'}
        for interactive, markers, expected in (
            (True, core, 'loaded'), (False, core, 'absent'),
            (True, {'TERM_PROGRAM': 'ghostty'}, 'absent'),
            (True, {'HC_TERMINAL_ID': 'synthetic-id'}, 'absent'),
            (True, {'HC_TERMINAL_SOCKET': 'synthetic-socket'}, 'absent')):
            result = self.shell(interactive, markers, source + query)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout.strip(), expected)
        result = self.shell(True, core, "before=$(bindkey '^I'); " + source +
                            "print -r -- ${(j:,:)ZSH_AUTOSUGGEST_STRATEGY}:$ZSH_AUTOSUGGEST_HIGHLIGHT_STYLE:${#ZSH_AUTOSUGGEST_EXECUTE_WIDGETS}; "
                            "[[ $(bindkey '^I') == $before ]] && print binding-preserved")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('history,herdr_path:fg=8:0\nbinding-preserved', result.stdout)
        result = self.shell(True, core, "_zsh_autosuggest_start() { :; }; ZSH_AUTOSUGGEST_HIGHLIGHT_STYLE=existing; " + source +
                            "print -r -- $ZSH_AUTOSUGGEST_HIGHLIGHT_STYLE")
        self.assertEqual(result.stdout.strip(), 'existing')


if __name__ == '__main__':
    unittest.main()
