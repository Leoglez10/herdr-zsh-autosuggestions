# Herdr zsh autosuggestions

A local zsh integration for Herdr users: see a faint continuation from shell history, or a local pathname when history has no match. Accepting a suggestion fills the command line; it does not run it. This is for people who want suggestions without changing the Herdr app.

## Install

Tested environment: macOS, zsh 5.9 and Python 3. Git is needed to clone. From a location you intend to keep:

```sh
git clone https://github.com/Leoglez10/herdr-zsh-autosuggestions.git
cd herdr-zsh-autosuggestions
python3 bin/fetch-plugin
# Optional: try the isolated history demo first
/bin/bash bin/trial
python3 bin/manage install --rc "$HOME/.zshrc"
```

The final command explicitly modifies the selected startup file. If zsh uses `ZDOTDIR`, choose its actual `.zshrc` instead of `$HOME/.zshrc`; inspect your setup first. No startup file is silently edited by the download or trial. Open a new Herdr shell after installing or updating. The managed block uses an **absolute path**: do not move or remove the project while installed; uninstall first, then reinstall from the new location. See [installation details](docs/install.md).

## Use

Type the beginning of a command. History is tried first; if it has no suggestion, a simple local path can be suggested, for example `cd app-ex` for a directory `app-example/`, or `ls "my fi` for a file `my file`. These examples are illustrative; matching files must exist. Right Arrow normally accepts a suggestion at the end of the buffer, but your zsh bindings control this. Enter executes the completed line; Tab retains its normal behavior.

Path fallback deliberately understands only a subset of shell syntax: one simple command and one literal pathname. It never invokes completion functions, external programs, file contents or network services; the pinned plugin itself uses a short-lived local subshell for its asynchronous fetch, as upstream does by default. In practice:

- Supported: unquoted paths, backslash-escaped spaces, single or double quotes around a pathname, and literal glob characters such as `[`.
- Not suggested: options or multiple arguments, `~` expansion, parameter, command or arithmetic expansion, shell operators, and any backslash inside double quotes (declined rather than guessed).
- `cd` offers directories only; other commands offer files and directories.
- When several paths match, the first in sorted order is offered. Without a suffix, no suggestion is shown.

Remote-mounted filesystems can make filesystem lookups slow or unavailable. [Trial instructions](docs/trial.md) describe the isolated demo.

## Status and removal

Use the same startup file selected during installation:

```sh
python3 bin/manage status --rc "$HOME/.zshrc"
python3 bin/manage uninstall --rc "$HOME/.zshrc"
```

Uninstall removes the owned block, not an already loaded plugin from an existing shell; start a new shell. Existing loaded plugins are left unchanged. The integration activates only when both `HC_TERMINAL_ID` and `HC_TERMINAL_SOCKET` are present in an interactive shell; it does not depend on `TERM_PROGRAM`.

## Troubleshooting

- **No suggestion:** check for matching history or a local path supported by the parser.
- **Not active:** check the selected rc file with `status`, verify both Herdr markers, and open a new Herdr shell.
- **Hard to see:** suggestions use muted `fg=8`; check your terminal palette and contrast.
- **Project moved:** restore it to its original location, uninstall there, then move and reinstall it.
- **Download fails:** check connectivity and retry `python3 bin/fetch-plugin`; it verifies both pinned SHA-256 hashes before writing.

## Data and development

The bootstrap downloads only the pinned public plugin and its license over HTTPS into `.cache/`. It does not upload terminal input or shell history. Normal suggestions use existing local shell history and filesystem paths; trial data is temporary under `.state/`. Startup changes are limited to the explicitly selected rc file. See [installation details](docs/install.md) before editing it.

After bootstrapping, run the focused tests with:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests
```

`integration.zsh` contains the Herdr loader and fallback; `bin/manage` manages the startup block, `bin/fetch-plugin` verifies the upstream dependency, and `tests/` exercises behavior. Contributions are welcome: open an issue or pull request at the [project repository](https://github.com/Leoglez10/herdr-zsh-autosuggestions) with a reproducible example and test. For support, use its issue tracker without posting private history or configuration.

## License

Project code is under the [MIT License](LICENSE). The upstream plugin has its own [MIT license](licenses/zsh-autosuggestions.LICENSE); see [NOTICE](NOTICE).
