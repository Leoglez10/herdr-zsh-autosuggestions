"""Exercise the real ZLE/plugin through a PTY using synthetic history only."""
import errno
import os
from pathlib import Path
import pty
import select
import subprocess
import tempfile
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / ".state"
STATE.mkdir(exist_ok=True)


class SuggestionsTest(unittest.TestCase):
    def setUp(self):
        self.assertTrue((ROOT / ".cache/zsh-autosuggestions.zsh").is_file(),
                        "Official pinned plugin is not downloaded yet")
        self.tmp = tempfile.TemporaryDirectory(dir=STATE)
        self.addCleanup(self.tmp.cleanup)
        self.home = Path(self.tmp.name)
        self.snapshot = self.home / "snapshot"
        self.master, slave = pty.openpty()
        env = dict(HOME=str(self.home), ZDOTDIR=str(self.home),
                   PATH="/usr/bin:/bin:/usr/sbin:/sbin", TERM="xterm-256color",
                   HERDR_PROBE_STATE=str(self.snapshot))
        self.proc = subprocess.Popen(
            ["/bin/zsh", "-df"], stdin=slave, stdout=slave, stderr=slave,
            cwd=self.home, env=env, start_new_session=True)
        os.close(slave)
        self.addCleanup(self.close_shell)
        self.output = b""
        self.send(('source "' + str(ROOT / "sandbox.zsh") + '"\n').encode())
        self.wait_for(b"herdr-trial> ")

    def close_shell(self):
        self.proc.terminate()
        try:
            self.proc.wait(timeout=2)
        except subprocess.TimeoutExpired:
            self.proc.kill()
            self.proc.wait(timeout=2)
        os.close(self.master)

    def send(self, value):
        os.write(self.master, value)

    def drain(self, duration=0.15):
        end = time.monotonic() + duration
        while time.monotonic() < end:
            ready, _, _ = select.select([self.master], [], [], max(0, end-time.monotonic()))
            if ready:
                try:
                    self.output += os.read(self.master, 65536)
                except OSError as exc:
                    if exc.errno != errno.EIO:
                        raise
                    break

    def wait_for(self, text):
        end = time.monotonic() + 3
        while text not in self.output and time.monotonic() < end:
            self.drain(0.05)
        self.assertIn(text, self.output)

    def state(self):
        self.snapshot.unlink(missing_ok=True)
        self.send(b"\x18\x07")
        end = time.monotonic() + 2
        while not self.snapshot.exists() and time.monotonic() < end:
            self.drain(0.02)
        self.assertTrue(self.snapshot.exists(), "ZLE snapshot did not complete")
        return self.snapshot.read_text().splitlines()

    def type_and_suggest(self, prefix):
        self.send(prefix)
        self.drain(0.2)
        return self.state()

    def test_faint_history_suggestion_and_update(self):
        buffer, ghost, cursor = self.type_and_suggest(b"printf")
        self.assertEqual(buffer, "printf")
        self.assertIn("herdr-sample-two", ghost)
        self.assertEqual(cursor, "6")
        self.assertTrue(b"38;5;8m" in self.output or b"[90m" in self.output,
                        "Missing muted ANSI foreground")
        buffer, ghost, _ = self.type_and_suggest(b" 'herdr-sample-o")
        self.assertIn("one", buffer + ghost)
        self.assertNotIn("two", ghost)

    def test_accept_never_executes_until_enter(self):
        self.type_and_suggest(b"touch")
        self.send(b"\x1b[C")
        self.drain()
        buffer, ghost, cursor = self.state()
        self.assertEqual(buffer, "touch herdr-executed")
        self.assertEqual(ghost, "")
        self.assertEqual(int(cursor), len(buffer))
        marker = self.home / "herdr-executed"
        self.assertFalse(marker.exists(), "Accept executed the command")
        self.send(b"\n")
        self.drain()
        self.assertTrue(marker.exists(), "Explicit Enter did not execute synthetic command")

    def test_unmatched_input_and_explicit_dismiss(self):
        self.type_and_suggest(b"printf")
        self.send(b"\x18\x04")
        self.drain()
        self.assertEqual(self.state()[:2], ["printf", ""])
        self.send(b"\x01\x0b")
        self.drain()
        self.assertEqual(self.type_and_suggest(b"unmatched-herdr-xyz")[:2],
                         ["unmatched-herdr-xyz", ""])
        self.assertFalse((self.home / "herdr-executed").exists())

    def test_cursor_edit_and_tab_preserve_normal_behavior(self):
        self.type_and_suggest(b"touch")
        self.send(b"\x1b[D")
        self.drain()
        self.assertEqual(self.state()[2], "4")
        self.send(b"\x7f")
        self.drain()
        self.assertEqual(self.state()[0], "touh")
        self.send(b"\x01\x0b")
        self.drain()
        (self.home / "unique-herdr-file").touch()
        self.send(b"cat unique-herdr-f\t")
        self.drain()
        self.assertEqual(self.state()[0], "cat unique-herdr-file ")
        self.assertFalse((self.home / "herdr-executed").exists())

    def test_typing_remains_responsive_without_network(self):
        self.send(b"x" * 100)
        buffer, ghost, cursor = self.state()
        self.assertEqual(buffer, "x" * 100)
        self.assertEqual(ghost, "")
        self.assertEqual(cursor, "100")
        self.assertFalse((self.home / "herdr-executed").exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
