# Isolated trial only: start with /bin/zsh -df, then source this file.
setopt no_beep
unset HISTFILE
HISTSIZE=50
SAVEHIST=0
fc -p /dev/null 50 0
PS1='herdr-trial> '
bindkey -e
# Synthetic markers only for this isolated trial; retain the caller's values.
() {
  local HC_TERMINAL_ID=synthetic-trial HC_TERMINAL_SOCKET=synthetic-trial
  source "$1/integration.zsh"
} "${${(%):-%N}:A:h}" || return
bindkey '^[[C' forward-char
bindkey '^X^D' autosuggest-clear
print -rs -- "printf 'herdr-sample-one\\n'"
print -rs -- "printf 'herdr-sample-two\\n'"
print -s -- 'touch herdr-executed'
if [[ -n ${HERDR_PROBE_STATE:-} ]]; then
  _herdr_probe_snapshot() {
    printf '%s\n' "$BUFFER" "$POSTDISPLAY" "$CURSOR" > "$HERDR_PROBE_STATE"
  }
  zle -N _herdr_probe_snapshot
  bindkey '^X^G' _herdr_probe_snapshot
fi
print -r -- 'Isolated local history + local paths suggestions; no AI. Right arrow accepts; Ctrl-X Ctrl-D dismisses; Ctrl-C clears; exit returns.'
