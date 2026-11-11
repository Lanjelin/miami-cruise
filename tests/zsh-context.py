#!/usr/bin/env python3
"""Dependency-free context/status regressions: Python stdlib, Zsh and existing Git.
Build first with python3 -I build.py zsh; then python3 tests/zsh-context.py.
Uses disposable repositories only; no user rc or Git config changes.
"""
from pathlib import Path
import os
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
ENV = {k: v for k, v in os.environ.items() if not k.startswith(('SSH_', 'GIT_', 'MIAMI_CRUISE_'))}
ENV.update(GIT_CONFIG_GLOBAL='/dev/null', GIT_CONFIG_NOSYSTEM='1')


def git(repo, *args, ok=True):
    result = subprocess.run(['git', '-C', str(repo), *args], env=ENV, text=True, capture_output=True)
    if ok:
        result.check_returncode()
    else:
        assert result.returncode != 0, result.stdout
    return result.stdout.strip()


def probe(variant, repo, script):
    theme = ROOT / f'dist/zsh/miami-cruise-{variant}.zsh-theme'
    result = subprocess.run(['zsh', '-fc', f'source {str(theme)!r}\n{script}'],
                            cwd=repo, env=ENV, text=True, capture_output=True)
    assert result.returncode == 0, (script, result.stdout, result.stderr)
    return result.stdout


def states(repo, expected):
    for variant in ('dark', 'light'):
        output = probe(variant, repo, 'MIAMI_CRUISE_SHOW_GIT_OPERATION=1; miami_cruise_git_status')
        assert expected in output, (expected, output)
        assert expected not in probe(variant, repo, 'miami_cruise_git_status')


with tempfile.TemporaryDirectory(prefix='miami-zsh-context-') as scratch:
    base = Path(scratch)
    repo = base / 'repo'
    repo.mkdir()
    git(repo, 'init', '-b', 'main')
    git(repo, 'config', 'user.name', 'Fixture')
    git(repo, 'config', 'user.email', 'fixture@example.invalid')
    file = repo / 'file'
    file.write_text('base\n')
    git(repo, 'add', 'file')
    git(repo, 'commit', '-m', 'base')
    initial = git(repo, 'rev-parse', 'HEAD')
    git(repo, 'checkout', '-b', 'topic')
    file.write_text('topic\n')
    git(repo, 'commit', '-am', 'topic')
    git(repo, 'checkout', 'main')
    file.write_text('main\n')
    git(repo, 'commit', '-am', 'main')
    git(repo, 'merge', 'topic', ok=False)
    states(repo, 'merge')
    git(repo, 'merge', '--abort')
    git(repo, 'cherry-pick', 'topic', ok=False)
    states(repo, 'cherry-pick')
    git(repo, 'cherry-pick', '--abort')
    git(repo, 'revert', 'topic', ok=False)
    states(repo, 'revert')
    git(repo, 'revert', '--abort')
    git(repo, 'rebase', 'topic', ok=False)
    states(repo, 'rebase 1/1')
    git(repo, 'rebase', '--abort')
    git(repo, '-c', 'rebase.backend=apply', 'rebase', 'topic', ok=False)
    states(repo, 'rebase 1/1')
    git(repo, 'rebase', '--abort')
    patch = base / 'topic.patch'
    patch.write_text(git(repo, 'format-patch', '-1', 'topic', '--stdout') + '\n')
    git(repo, 'am', str(patch), ok=False)
    states(repo, 'am 1/1')
    git(repo, 'am', '--abort')
    git(repo, 'bisect', 'start')
    git(repo, 'bisect', 'bad')
    git(repo, 'bisect', 'good', initial)
    states(repo, 'bisect')
    git(repo, 'bisect', 'reset')
    linked = base / 'linked'
    git(repo, 'worktree', 'add', '-b', 'linked', str(linked))
    git(linked, 'merge', 'topic', ok=False)
    states(linked, 'merge')
    git(linked, 'merge', '--abort')
    print('PASS real merge/rebase/cherry-pick/revert/bisect states and linked worktrees')
    readonly = base / 'readonly'
    readonly.mkdir(mode=0o555)
    for variant in ('dark', 'light'):
        probe(variant, repo, r'''
# A ZLE hangup notification can arrive with the complete record still buffered.
_miami_cruise_git_pwd=$PWD
exec {_miami_cruise_git_fd}< <(print -rn -- "buffered-result"$'\0')
miami_cruise_git_ready $_miami_cruise_git_fd hup
[[ $_miami_cruise_git_cache == buffered-result && -z ${_miami_cruise_git_fd:-} ]] || exit 20
false | true
miami_cruise_precmd
[[ -z $_miami_cruise_error ]] || exit 1
MIAMI_CRUISE_SHOW_PIPELINE_STATUS=1
false | true
miami_cruise_precmd
[[ $_miami_cruise_error == *'[1|0]'* ]] || exit 2
true | true
miami_cruise_precmd
[[ -z $_miami_cruise_error ]] || exit 3
setopt pipefail
false | true
miami_cruise_precmd
[[ $_miami_cruise_error == *'[1|0]'* && -o pipefail ]] || exit 4
MIAMI_CRUISE_SHOW_RETURN_CODE=0
false | true
miami_cruise_precmd
[[ -z $_miami_cruise_error && -o pipefail ]] || exit 5
MIAMI_CRUISE_SHOW_RETURN_CODE=1
MIAMI_CRUISE_SIGNAL_NAMES=1
command zsh -fc 'kill -TERM $$'
miami_cruise_precmd
[[ $_miami_cruise_error == *SIGTERM* ]] || exit 6
MIAMI_CRUISE_SHOW_PIPELINE_STATUS=0
false | true
miami_cruise_precmd
[[ $_miami_cruise_error == *'1 ↵'* ]] || exit 7
''')
        probe(variant, repo, r'''
[[ -n $(miami_cruise_context) ]] || exit 1
MIAMI_CRUISE_SMART_CONTEXT=1
if (( UID != 0 )); then
  [[ -z $(miami_cruise_context) ]] || exit 2
fi
SSH_CONNECTION=test
[[ -n $(miami_cruise_context) ]] || exit 3
unset SSH_CONNECTION
SHLVL=1
miami_cruise_precmd
[[ -z $_miami_cruise_shell_level ]] || exit 4
MIAMI_CRUISE_SHOW_SHELL_LEVEL=1
miami_cruise_precmd
[[ -z $_miami_cruise_shell_level ]] || exit 5
SHLVL=2
miami_cruise_precmd
[[ $_miami_cruise_shell_level == *sh:2* ]] || exit 6
YAZI_LEVEL=3
miami_cruise_precmd
[[ $_miami_cruise_shell_level == *yazi:3* && $_miami_cruise_shell_level != *sh:* ]] || exit 7
MIAMI_CRUISE_SHOW_SHELL_LEVEL=0
miami_cruise_precmd
[[ -z $_miami_cruise_shell_level ]] || exit 8
''')
        probe(variant, readonly, r'''
MIAMI_CRUISE_SHOW_READ_ONLY=1
miami_cruise_precmd
if [[ ! -w $PWD ]]; then
  [[ $_miami_cruise_read_only == *''* && $_miami_cruise_right_prompt != *''* ]] || exit 1
else
  [[ -z $_miami_cruise_read_only ]] || exit 2
fi
MIAMI_CRUISE_SHOW_READ_ONLY=0
miami_cruise_precmd
[[ -z $_miami_cruise_read_only ]] || exit 3
''')
        theme = ROOT / f'dist/zsh/miami-cruise-{variant}.zsh-theme'
        # Exercise theme-owned glyphs without rewriting user text.
        output = probe(variant, repo, f'''
MIAMI_CRUISE_ASCII=1
source {str(theme)!r}
function ruby_prompt_info() {{ print -nr -- "${{ZSH_THEME_RUBY_PROMPT_PREFIX}}ruby${{ZSH_THEME_RUBY_PROMPT_SUFFIX}}"; }}
print -P -- "$PROMPT"
MIAMI_CRUISE_SHOW_RETURN_CODE=1
false
miami_cruise_precmd
print -P -- "$RPROMPT"
''')
        assert all(ord(c) < 128 for c in output), output
        assert 'git:main' in output and '<ruby>' in output and '1 exit' in output, output
        print(f'PASS {variant}: pipeline/signal flags, context, permissions, shell depth and ASCII')
