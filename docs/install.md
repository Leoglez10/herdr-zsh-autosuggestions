# Install and remove the integration

From a clean clone, run `python3 bin/fetch-plugin` before installation. It downloads the pinned public script and license over HTTPS and verifies both SHA-256 hashes from `dependency.json`; it does not edit startup files. Existing verified artifacts are reused. If verification fails, check the network and cache before retrying. Do not edit the cache concurrently with the download.

Explicitly select the zsh startup file you want to change. For a standard HOME-based setup:

```sh
python3 bin/manage install --rc "$HOME/.zshrc"
python3 bin/manage status --rc "$HOME/.zshrc"
python3 bin/manage uninstall --rc "$HOME/.zshrc"
python3 bin/manage --help
```

If `ZDOTDIR` changes where zsh reads `.zshrc`, use that file instead. Inspect your setup before choosing; the manager never automatically selects one. Install verifies the cached script before editing. The owned block sources `integration.zsh` by absolute path: **do not move or remove the project while installed**. Uninstall first, then reinstall at the new location. Start a new Herdr shell after installation, updates or removal; existing shells keep what they already loaded.

The manager preserves existing bytes, inode and permissions, appends a marked block, and removes only that exact block, preserving later edits. Install and uninstall are idempotent. It refuses symlinks, nonregular files and ambiguous or modified markers; resolve these manually. It makes no backups and prints no configuration content. An absent rc file is created in an existing directory; uninstall retains that file empty. Avoid concurrent edits. System zsh startup files and other plugins are outside its control.

The integration activates in interactive shells with both `HC_TERMINAL_ID` and `HC_TERMINAL_SOCKET`; it leaves an already-loaded plugin unchanged. It tries local history first, then a conservative local pathname fallback limited to one simple command and one literal pathname; options, multiple arguments, expansions, shell operators and backslashes inside double quotes get no path suggestion. It doesn't bind keys or execute a suggestion when accepted. The script and license live under `.cache/`; trial state lives under `.state/`. Existing shell history is not uploaded by this integration. Only the bootstrap makes public HTTPS downloads.
