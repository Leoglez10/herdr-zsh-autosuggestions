"""PTY coverage for the bounded local pathname fallback; fixtures are synthetic."""
from test_suggestions import SuggestionsTest


class PathTest(SuggestionsTest):
    def test_paths(self):
        (self.home / 'app-example').mkdir()
        (self.home / 'app-example-worktrees').mkdir()
        prefix = b'cd app-ex'
        self.assertEqual(self.type_and_suggest(prefix)[:2],
                         ['cd app-ex', 'ample/'])
        self.send(b'\x1b[C')
        self.drain()
        self.assertEqual(self.state()[:2], ['cd app-example/', ''])
        self.assertEqual(self.proc.poll(), None)

    def test_history_first(self):
        (self.home / 'herdr-executed-path').touch()
        self.assertIn('herdr-executed', ''.join(self.type_and_suggest(b'touch herdr-ex')))
        self.assertEqual(self.state()[1], 'ecuted')

    def test_cd_dirs_only_and_file_argument(self):
        (self.home / 'choice-a').touch()
        (self.home / 'choice-b').mkdir()
        self.assertEqual(self.type_and_suggest(b'cd choice-')[:2], ['cd choice-', 'b/'])
        self.send(b'\x01\x0b')
        self.drain()
        self.assertEqual(self.type_and_suggest(b'cat choice-a')[:2], ['cat choice-a', ''])
        self.send(b'\x01\x0b')
        self.drain()
        self.assertEqual(self.type_and_suggest(b'cat choice-')[:2], ['cat choice-', 'a'])

    def test_no_match(self):
        self.assertEqual(self.type_and_suggest(b'cat missing-xyz')[:2], ['cat missing-xyz', ''])

    def test_spaces_and_literal_glob(self):
        (self.home / 'space name').touch()
        for typed, expected in [(b'cat space\\ n', 'ame'), (b"cat 'space n", "ame'"),
                                (b'cat "space n', 'ame"')]:
            with self.subTest(typed=typed):
                self.send(b'\x01\x0b')
                self.drain()
                buffer, ghost, _ = self.type_and_suggest(typed)
                self.assertEqual(buffer + ghost, typed.decode() + expected)
                self.send(b'\x1b[C')
                self.drain()
                self.assertEqual(self.state()[0], typed.decode() + expected)
        (self.home / 'literal[abc').touch()
        self.send(b'\x01\x0b')
        self.drain()
        self.assertEqual(self.type_and_suggest(b'cat literal[')[:2], ['cat literal[', 'abc'])

    def test_double_quoted_backslash_is_not_misinterpreted(self):
        (self.home / 'slashname').touch()
        (self.home / 'slash name').touch()
        for typed in (b'cat "slash\\n', b'cat "slash\\ n'):
            with self.subTest(typed=typed):
                self.send(b'\x01\x0b')
                self.drain()
                self.assertEqual(self.type_and_suggest(typed)[:2], [typed.decode(), ''])

    def test_reject_shell_syntax_without_execution_or_changes(self):
        marker = self.home / 'sentinel'
        fixture = self.home / 'fixture'
        fixture.write_text('untouched')
        for typed in (b'cat $(touch sentinel)', b'cat `touch sentinel`',
                      b'cat fixture;touch sentinel', b'cat fixture>sentinel',
                      b'cat $HOME/fixture'):
            with self.subTest(typed=typed):
                self.send(b'\x01\x0b')
                self.drain()
                self.assertEqual(self.type_and_suggest(typed)[:2], [typed.decode(), ''])
                self.send(b'\x1b[C')
                self.drain()
                self.assertEqual(self.state()[0], typed.decode())
                self.assertFalse(marker.exists())
                self.assertEqual(fixture.read_text(), 'untouched')


if __name__ == '__main__':
    import unittest
    unittest.main(verbosity=2)
