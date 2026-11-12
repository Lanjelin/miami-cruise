# Native Zsh facilities: no worker plugin, daemon or temporary files required.
zmodload zsh/datetime
zmodload zsh/parameter

# Re-sourcing must release any old descriptor before replacing its callbacks.
if (( ${+functions[miami_cruise_git_close]} )); then
  miami_cruise_git_close
fi
typeset -g _miami_cruise_git_cache='' _miami_cruise_git_pwd=''
typeset -g _miami_cruise_duration='' _miami_cruise_mode=''
typeset -g _miami_cruise_timestamp='' _miami_cruise_right_prompt=''
typeset -g _miami_cruise_last_submitted_pwd=''
typeset -g _miami_cruise_read_only='' _miami_cruise_shell_level=''
typeset -g _miami_cruise_started='' _miami_cruise_jobs='' _miami_cruise_error=''


# Selected at load time, like the layout flags. ASCII changes theme-owned glyphs,
# never user-provided branch names, paths or environment names.
typeset -gA _miami_cruise_symbols=(
  arrow '➤' first '╭─' last '╰─' branch '' ahead '⇡' behind '⇣'
  conflict '×' failure '↵' running '⚙' suspended 'Ⅱ' ruby_open '‹' ruby_close '›' lock ''
  python ' ' duration '󱎫 ' shell ' ' yazi ' '
)
if [[ ${MIAMI_CRUISE_ASCII:-0} == 1 ]]; then
  _miami_cruise_symbols=(
    arrow '>' first '+-' last '+-' branch 'git:' ahead '^' behind 'v'
    conflict 'x' failure 'exit' running 'jobs:' suspended 'stopped:' ruby_open '<' ruby_close '>' lock '[RO]'
    python '' duration '' shell '' yazi ''
  )
fi

typeset -g _miami_cruise_arrow=${_miami_cruise_symbols[arrow]}

# Static between redraws: show local prompt time while editing, then stamp the
# actual submission time in line-finish so scrollback does not show an idle clock.
function miami_cruise_timestamp_update() {
  _miami_cruise_timestamp=''
  if [[ ${MIAMI_CRUISE_SHOW_TIMESTAMP:-0} == 1 ]]; then
    local clock_text
    strftime -s clock_text '%H:%M:%S' $EPOCHSECONDS
    _miami_cruise_timestamp="%F{@time@}${clock_text}%f"
  fi
  return 0
}

# Joining nonempty segments keeps spacing consistent, with time always last.
function miami_cruise_right_prompt_update() {
  local part
  local -a segments=()
  for part in "$(miami_cruise_venv)" "$_miami_cruise_shell_level" "$_miami_cruise_mode" \
      "$_miami_cruise_jobs" "$_miami_cruise_duration" \
      "$_miami_cruise_error" "$_miami_cruise_timestamp"; do
    [[ -n $part ]] && segments+=("${part% }")
  done
  _miami_cruise_right_prompt="${(j: :)segments}"
  return 0
}

function miami_cruise_status_label() {
  local code=$1 signal_index=$(( $1 - 127 ))
  # Shell statuses conventionally encode signals as 128 + signal number.
  # An explicit `exit 130` is indistinguishable from SIGINT here.
  if [[ ${MIAMI_CRUISE_SIGNAL_NAMES:-0} == 1 ]] &&
      (( code > 128 && signal_index <= ${#signals} )) && [[ -n $signals[$signal_index] ]]; then
    print -nr -- "SIG${signals[$signal_index]}"
  else
    print -nr -- "$code"
  fi
}

function miami_cruise_context() {
  if [[ ${MIAMI_CRUISE_SMART_CONTEXT:-0} != 1 || $UID == 0 ||
        -n $SSH_CONNECTION || -n $SSH_CLIENT || -n $SSH2_CLIENT || -n $SSH_TTY ]]; then
    print -nr -- "$_miami_cruise_user_host "
  elif [[ ${MIAMI_CRUISE_SINGLE_LINE:-0} != 1 ]]; then
    # Keep the path (or read-only marker) clear of the two-line decoration.
    print -nr -- ' '
  fi
  return 0
}

function miami_cruise_git_state() {
  [[ ${MIAMI_CRUISE_SHOW_GIT_OPERATION:-0} == 1 ]] || return 0
  local git_dir state='' step='' total=''
  git_dir=$(command git rev-parse --absolute-git-dir 2>/dev/null) || return 0
  if [[ -d $git_dir/rebase-merge ]]; then
    state=rebase
    [[ -r $git_dir/rebase-merge/msgnum ]] && step=$(< "$git_dir/rebase-merge/msgnum")
    [[ -r $git_dir/rebase-merge/end ]] && total=$(< "$git_dir/rebase-merge/end")
  elif [[ -d $git_dir/rebase-apply ]]; then
    state=rebase
    [[ -f $git_dir/rebase-apply/applying ]] && state=am
    [[ -r $git_dir/rebase-apply/next ]] && step=$(< "$git_dir/rebase-apply/next")
    [[ -r $git_dir/rebase-apply/last ]] && total=$(< "$git_dir/rebase-apply/last")
  elif [[ -f $git_dir/CHERRY_PICK_HEAD ]]; then
    state=cherry-pick
  elif [[ -f $git_dir/REVERT_HEAD ]]; then
    state=revert
  elif [[ -f $git_dir/MERGE_HEAD ]]; then
    state=merge
  elif [[ -f $git_dir/BISECT_LOG ]]; then
    state=bisect
  fi
  [[ -n $state ]] || return 0
  [[ $step == <-> && $total == <-> ]] && state+=" $step/$total"
  print -nr -- " %F{@conflict@}${state}%f"
}

function miami_cruise_git_close() {
  if [[ -n ${_miami_cruise_git_fd:-} ]]; then
    zle -F $_miami_cruise_git_fd 2>/dev/null
    exec {_miami_cruise_git_fd}<&-
    unset _miami_cruise_git_fd
  fi
  return 0
}

function miami_cruise_git_ready() {
  emulate -L zsh
  local result='' fd=$1
  [[ $fd == ${_miami_cruise_git_fd:-} ]] || return 0
  # Worker writes one NUL-delimited record, including an empty non-repo result.
  # A pipe may report hangup with its final record still buffered.
  if [[ -z $2 || $2 == hup ]] && IFS= read -r -d '' -u $fd result; then
    [[ $_miami_cruise_git_pwd == $PWD ]] && _miami_cruise_git_cache=$result
  fi
  miami_cruise_git_close
  if zle; then
    zle .reset-prompt
    zle -R
  fi
  return 0
}

function miami_cruise_git_start() {
  [[ ${MIAMI_CRUISE_SHOW_GIT:-1} == 1 && ${MIAMI_CRUISE_ASYNC_GIT:-1} == 1 ]] || {
    miami_cruise_git_close
    _miami_cruise_git_cache=''
    return 0
  }
  if [[ $_miami_cruise_git_pwd != $PWD ]]; then
    miami_cruise_git_close
    _miami_cruise_git_cache=''
  fi
  _miami_cruise_git_pwd=$PWD
  # Don't launch another worker while the current directory's request is pending.
  [[ -n ${_miami_cruise_git_fd:-} ]] && return 0
  exec {_miami_cruise_git_fd}< <(
    local result=$(miami_cruise_git_status)
    print -rn -- "$result"$'\0'
  )
  zle -F $_miami_cruise_git_fd miami_cruise_git_ready
  return 0
}

function miami_cruise_chpwd() {
  miami_cruise_git_close
  _miami_cruise_git_cache=''
  _miami_cruise_git_pwd=''
  return 0
}

function miami_cruise_git_prompt() {
  [[ ${MIAMI_CRUISE_SHOW_GIT:-1} == 1 ]] || return 0
  if [[ ${MIAMI_CRUISE_ASYNC_GIT:-1} == 1 && -o interactive ]]; then
    [[ $_miami_cruise_git_pwd == $PWD ]] && print -nr -- "$_miami_cruise_git_cache"
  else
    miami_cruise_git_status
  fi
}

function miami_cruise_venv() {
  [[ ${MIAMI_CRUISE_SHOW_VIRTUALENV:-1} == 1 ]] || return 0
  local env_name=''
  if [[ -n $VIRTUAL_ENV ]]; then
    env_name=${VIRTUAL_ENV_PROMPT:-${VIRTUAL_ENV:t}}
  else
    env_name=${CONDA_DEFAULT_ENV:t}
  fi
  [[ -n $env_name ]] || return 0
  print -nr -- "%F{@venv@}${_miami_cruise_symbols[python]}(${env_name//\%/%%})%f "
}

function miami_cruise_ruby() {
  (( ${+functions[ruby_prompt_info]} )) && ruby_prompt_info
  return 0
}

function miami_cruise_inline_segments() {
  local segment
  segment=$(miami_cruise_ruby)
  [[ -n $segment ]] && print -nr -- " $segment"
  segment=$(miami_cruise_git_prompt)
  [[ -n $segment ]] && print -nr -- " $segment"
  return 0
}

function miami_cruise_preexec() {
  _miami_cruise_started=$EPOCHREALTIME
  _miami_cruise_last_submitted_pwd=$PWD
  # An in-flight snapshot predating this command must not repaint its result.
  miami_cruise_git_close
  return 0
}

function miami_cruise_precmd() {
  local last_status=$? last_pipeline="${(j: :)pipestatus}"
  local -a pipeline_codes=( ${=last_pipeline} )
  local code label=''
  local -i pipeline_failed=0
  for code in $pipeline_codes; do
    (( code )) && pipeline_failed=1
  done
  _miami_cruise_error=''
  if [[ ${MIAMI_CRUISE_SHOW_RETURN_CODE:-1} == 1 ]]; then
    if [[ ${MIAMI_CRUISE_SHOW_PIPELINE_STATUS:-0} == 1 ]] &&
        (( ${#pipeline_codes} > 1 && pipeline_failed )); then
      for code in $pipeline_codes; do
        [[ -n $label ]] && label+='|'
        label+=$(miami_cruise_status_label $code)
      done
      label="[$label]"
    elif (( last_status )); then
      label=$(miami_cruise_status_label $last_status)
    fi
    [[ -n $label ]] && _miami_cruise_error="%F{@error@}${label} ${_miami_cruise_symbols[failure]}%f"
  fi
  _miami_cruise_read_only=''
  if [[ ${MIAMI_CRUISE_SHOW_READ_ONLY:-1} == 1 && ! -w $PWD ]]; then
    _miami_cruise_read_only="%F{@error@}${_miami_cruise_symbols[lock]}%f "
  fi
  _miami_cruise_shell_level=''
  if [[ ${MIAMI_CRUISE_SHOW_SHELL_LEVEL:-0} == 1 ]]; then
    if [[ ${YAZI_LEVEL:-0} == <-> ]] && (( ${YAZI_LEVEL:-0} > 0 )); then
      _miami_cruise_shell_level="%F{@jobs@}${_miami_cruise_symbols[yazi]}yazi:${YAZI_LEVEL}%f "
    elif (( SHLVL > 1 )); then
      _miami_cruise_shell_level="%F{@jobs@}${_miami_cruise_symbols[shell]}sh:${SHLVL}%f "
    fi
  fi
  local threshold=${MIAMI_CRUISE_DURATION_THRESHOLD:-3} job_state
  local -F elapsed
  _miami_cruise_duration=''
  if [[ -n $_miami_cruise_started && ${MIAMI_CRUISE_SHOW_DURATION:-1} == 1 ]]; then
    [[ $threshold == <-> || $threshold == <->.<-> ]] || threshold=3
    elapsed=$(( EPOCHREALTIME - _miami_cruise_started ))
    if (( elapsed >= threshold )); then
      printf -v _miami_cruise_duration '%%F{@duration@}%s%.1fs%%f ' "${_miami_cruise_symbols[duration]}" $elapsed
    fi
  fi
  _miami_cruise_started=''
  _miami_cruise_jobs=''
  if [[ ${MIAMI_CRUISE_SHOW_JOBS:-1} == 1 ]]; then
    local -i running=0 suspended=0
    for job_state in "${(@v)jobstates}"; do
      case $job_state in
        running:*) (( running++ )) ;;
        suspended:*) (( suspended++ )) ;;
      esac
    done
    (( running )) && _miami_cruise_jobs="%F{@jobs@}${_miami_cruise_symbols[running]}${running}%f "
    (( suspended )) && _miami_cruise_jobs+="%F{@jobs@}${_miami_cruise_symbols[suspended]}${suspended}%f "
  fi
  miami_cruise_timestamp_update
  miami_cruise_right_prompt_update
  [[ -o interactive ]] && miami_cruise_git_start
  # Status is rendered from the snapshot; never stop other precmd hooks.
  return 0
}

# line-pre-redraw also catches visual selection and overwrite transitions that
# don't change keymaps. Never replace accept-line or any user's vi widgets.
function miami_cruise_mode_update() {
  local mode='' arrow=${_miami_cruise_symbols[arrow]}
  if [[ ${MIAMI_CRUISE_SHOW_VI_MODE:-0} == 1 ]]; then
    if (( ${REGION_ACTIVE:-0} )); then
      mode=VIS
    elif [[ $ZLE_STATE == *overwrite* ]]; then
      mode=REP
    elif [[ $KEYMAP == vicmd ]]; then
      mode=NOR
    else
      mode=INS
    fi
    if [[ ${MIAMI_CRUISE_ASCII:-0} == 1 ]]; then
      mode="%F{@mode@}[${mode}]%f "
    else
      case $mode in
        NOR) arrow='❮' ;;
        VIS) arrow='V' ;;
        REP) arrow='▶' ;;
      esac
      mode=''
    fi
  fi
  if [[ $_miami_cruise_mode != $mode || $_miami_cruise_arrow != $arrow ]]; then
    _miami_cruise_arrow=$arrow
    _miami_cruise_mode=$mode
    miami_cruise_right_prompt_update
    zle .reset-prompt
  fi
  return 0
}

autoload -Uz add-zsh-hook
add-zsh-hook preexec miami_cruise_preexec
add-zsh-hook precmd miami_cruise_precmd
if [[ -o interactive ]]; then
  add-zsh-hook chpwd miami_cruise_chpwd
  add-zsh-hook zshexit miami_cruise_git_close
  autoload -Uz add-zle-hook-widget
  add-zle-hook-widget line-init miami_cruise_mode_update
  add-zle-hook-widget keymap-select miami_cruise_mode_update
  add-zle-hook-widget line-pre-redraw miami_cruise_mode_update
fi
