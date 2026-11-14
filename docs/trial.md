# Isolated history suggestion trial

Run `python3 bin/fetch-plugin` first, then start a **new** Herdr terminal and run:

```sh
/bin/bash /absolute/path/to/bin/trial
```

Or from the project directory run `/bin/bash bin/trial`. The trial demonstrates history suggestions and the conservative local pathname fallback (one simple command and one literal pathname; no options, multiple arguments or expansions). The trial does not install the integration or modify Herdr. `--help` prints usage without starting a shell.

The launcher starts interactive `/bin/zsh -d -i` with a fresh HOME, ZDOTDIR and working directory under `.state/`. It sources a generated `.zshrc` and `sandbox.zsh`, not your normal user zsh configuration or history. Zsh may still read the system `/etc/zshenv`. Only TERM and, if explicitly set, the diagnostic `HERDR_PROBE_STATE` are forwarded from the original environment; PATH is fixed.

Type `printf` and look for a faint continuation. Type more to change it; use Right Arrow at the end of the input to accept. Acceptance fills the input; Enter executes it. Ctrl-X Ctrl-D dismisses the suggestion; Ctrl-C clears the input. Check editing and Tab as well. The sample `touch herdr-executed` creates a file only if you press Enter.

Type `exit` or Ctrl-D on an empty line to end the trial. Its temporary directory and any files you create there are removed on normal exit; do not store anything there that you want to keep. Abrupt termination may leave it behind. The trial does not capture global keys or upload history.
