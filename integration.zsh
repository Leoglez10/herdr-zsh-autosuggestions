# Local Herdr Core shells only; leave an already-loaded plugin untouched.
if [[ -o interactive && -n ${HC_TERMINAL_ID:-} && -n ${HC_TERMINAL_SOCKET:-} ]] && (( ! $+functions[_zsh_autosuggest_start] )); then
  # Only a simple command and one literal pathname are understood. Operators,
  # expansions, substitutions, options and multiple arguments are not parsed.
  # Quotes may enclose the pathname; backslashes inside double quotes are unsupported.
  # No completion functions, processes, file contents, or network services are used.
  _zsh_autosuggest_strategy_herdr_path() {
    emulate -L zsh
    setopt extendedglob
    local input=$1 command raw literal='' quote='' char suffix candidate pattern
    local -a matches
    integer i=1 escaped=0 closed=0
    [[ $input == (#b)([A-Za-z0-9_./-]##)' '([\ -~]##) ]] || return
    command=$match[1] raw=$match[2]
    [[ $raw != -* ]] || return
    while (( i <= ${#raw} )); do
      char=$raw[i]
      # Reject shell syntax rather than attempt to interpret it, even in quotes.
      case $char in
        ('$'|'`'|';'|'|'|'&'|'<'|'>'|'('|')'|'{'|'}'|'!'|'~') return ;;
      esac
      if (( escaped )); then
        literal+=$char
        escaped=0
      elif [[ $char == '\' && $quote != "'" ]]; then
        [[ -z $quote ]] || return
        escaped=1
      elif [[ -n $quote && $char == $quote ]]; then
        quote=''
        closed=1
      elif [[ -z $quote && ( $char == "'" || $char == '"' ) ]]; then
        (( i == 1 && ! closed )) || return
        quote=$char
      elif [[ $char == ' ' && -z $quote ]]; then
        return
      else
        (( ! closed )) || return
        literal+=$char
      fi
      (( i++ ))
    done
    (( ! escaped )) && [[ -n $literal ]] || return
    # (b) quotes glob metacharacters before the only wildcard is appended.
    pattern=${(b)literal}'*'
    if [[ $command == cd ]]; then
      matches=( ${~pattern}(N-/) )
    else
      matches=( ${~pattern}(N) )
    fi
    (( ${#matches} )) || return
    matches=( ${(o)matches} )
    candidate=$matches[1]
    [[ -d $candidate && $candidate != */ ]] && candidate+=/
    suffix=${candidate:${#literal}}
    [[ -n $suffix || -n $quote ]] || return
    if [[ -n $quote ]]; then
      # Avoid producing shell syntax inside an open quote for unusual filenames.
      [[ $suffix != *[!A-Za-z0-9_./\ \-]* ]] || return
      suggestion=$input$suffix$quote
    else
      suggestion=$input${(q)suffix}
    fi
  }
  ZSH_AUTOSUGGEST_STRATEGY=(history herdr_path)
  ZSH_AUTOSUGGEST_HIGHLIGHT_STYLE='fg=8'
  ZSH_AUTOSUGGEST_EXECUTE_WIDGETS=()
  source "${${(%):-%N}:A:h}/.cache/zsh-autosuggestions.zsh"
fi
