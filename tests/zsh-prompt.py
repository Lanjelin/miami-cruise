#!/usr/bin/env python3
"""Real ZLE regression checks in disposable tmux servers; no user rc changes.
Run after: python3 -I build.py zsh
Requires Zsh 5.9+, Git and tmux. Uses only Python's standard library.
"""
from pathlib import Path
import os
import subprocess
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]


def run(*args, **kwargs):
    return subprocess.run(args, check=True, text=True, capture_output=True, **kwargs).stdout


def check(variant, single, transient, base):
    home = base / f'{variant}-{single}-{transient}'
    home.mkdir()
    repo = home / 'repo'
    repo.mkdir()
    run('git', 'init', '-b', 'cruise', str(repo))
    (repo / 'untracked').write_text('test')
    slow = home / 'slow'
    slow.mkdir()
    run('git', 'init', '-b', 'old-branch', str(slow))
    shim = home / 'bin'
    shim.mkdir()
    real_git = run('which', 'git').strip()
    # Delay only status in this fixture, not the shell or directory segment.
    (shim / 'git').write_text(f'#!/bin/sh\ncase "$PWD:$1" in */slow:status) sleep 1.5;; esac\nexec {real_git} "$@"\n')
    (shim / 'git').chmod(0o755)
    theme = ROOT / f'dist/zsh/miami-cruise-{variant}.zsh-theme'
    (home / '.config/zsh').mkdir(parents=True)
    (home / '.config/zsh/.zshrc').symlink_to(home / '.zshrc')
    (home / '.zshrc').write_text(f'''
PATH={str(shim)!r}:$PATH
MIAMI_CRUISE_SINGLE_LINE={single}
MIAMI_CRUISE_TRANSIENT_PROMPT={transient}
MIAMI_CRUISE_SHOW_VI_MODE=1
MIAMI_CRUISE_DURATION_THRESHOLD=0.1
function existing_preexec() {{ :; }}
function existing_precmd() {{ :; }}
preexec_functions=(existing_preexec)
function existing_post_precmd() {{ print -r -- called > {str(home / 'post-hook')!r}; }}
precmd_functions=(existing_precmd)
function existing_keymap() {{ print -r -- $KEYMAP > {str(home / 'keymap-hook')!r}; }}
zle -N zle-keymap-select existing_keymap
bindkey -v
source {str(theme)!r}
source {str(theme)!r}
precmd_functions+=(existing_post_precmd)
''')
    env = dict(os.environ, HOME=str(home), ZDOTDIR=str(home), TERM='tmux-256color',
               GIT_CONFIG_GLOBAL='/dev/null', GIT_CONFIG_NOSYSTEM='1')
    socket = str(home / 'tmux.sock')

    def tmux(*args):
        return run('tmux', '-S', socket, *args, env=env)

    def screen(history=False):
        return tmux('capture-pane', '-p', '-t', 'test', *(('-S', '-') if history else ()))

    def current(value):
        return '\n'.join([line for line in value.splitlines() if line.strip()][-(1 if single else 2):])

    def lastline(value):
        return ([line for line in value.splitlines() if line.strip()] or [''])[-1]

    def wait(predicate, label, timeout=5):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            value = screen()
            if predicate(value):
                return value
            time.sleep(.025)
        raise AssertionError(f'{variant}/{single}/{transient}: {label}\n{screen()}')

    def command(value):
        tmux('send-keys', '-t', 'test', '-l', value)
        tmux('send-keys', '-t', 'test', 'Enter')
        time.sleep(.08)

    try:
        tmux('-f', '/dev/null', 'new-session', '-d', '-s', 'test', '-x', '150', '-y', '35', '-c', str(home), 'zsh', '-i')
        tmux('set-option', '-g', 'status', 'off')
        tmux('set-option', '-g', 'scroll-on-clear', 'off')
        wait(lambda s: '➤' in lastline(s), 'standalone startup')
        command(f'cd {repo}')
        wait(lambda s: 'cruise ?1' in s, 'async real Git')
        command('sleep 0.2')
        wait(lambda s: '󱎫 0.2s' in s, 'duration')
        command('true')
        wait(lambda s: '0.2s' not in lastline(s), 'duration resets')
        command('VIRTUAL_ENV=/tmp/python-env')
        wait(lambda s: ' (python-env)' in lastline(s), 'native venv')
        command('VIRTUAL_ENV_PROMPT=nbno')
        wait(lambda s: ' (nbno)' in lastline(s), 'venv display name')
        command('unset VIRTUAL_ENV; CONDA_DEFAULT_ENV=conda-env')
        wait(lambda s: ' (conda-env)' in lastline(s), 'conda fallback')
        command('unset CONDA_DEFAULT_ENV VIRTUAL_ENV_PROMPT; sleep 30 &')
        wait(lambda s: '⚙1' in lastline(s), 'background job')
        command('kill -STOP %1; sleep 0.1')
        wait(lambda s: 'Ⅱ1' in lastline(s), 'suspended job')
        command('kill -CONT %1; kill %1')
        wait(lambda s: 'Ⅱ1' not in lastline(s), 'job removal')
        assert '[INS]' not in lastline(screen()), 'Unicode mode must not add labels'
        tmux('send-keys', '-t', 'test', '-l', 'abcdef')
        tmux('send-keys', '-t', 'test', 'Escape')
        wait(lambda s: '❮' in lastline(s), 'vi normal')
        tmux('send-keys', '-t', 'test', '-l', 'v')
        wait(lambda s: 'V' in lastline(s), 'vi visual')
        tmux('send-keys', '-t', 'test', 'Escape')
        tmux('send-keys', '-t', 'test', '-l', 'R')
        wait(lambda s: '▶' in lastline(s), 'vi replace')
        tmux('send-keys', '-t', 'test', 'C-c')
        wait(lambda s: '➤' in lastline(s), 'vi reset on new line')
        command(f'cd {slow}')
        tmux('send-keys', '-t', 'test', '-l', 'echo responsive')
        wait(lambda s: '➤  echo responsive' in s, 'typing during delayed Git', timeout=.7)
        wait(lambda s: 'old-branch' in current(s) and 'echo responsive' in lastline(s),
             'async repaint preserves buffer')
        tmux('send-keys', '-t', 'test', 'C-c')
        command(f'cd {home}; cd {slow}; cd {home}')
        time.sleep(1.7)
        assert 'old-branch' not in current(screen()), 'stale async result after cd'
        command(f'cd {repo}')
        wait(lambda s: 'cruise ?1' in s, 'new-directory result')
        (home / 'post-hook').unlink(missing_ok=True)
        command('false')
        wait(lambda s: '1 ↵' in lastline(s), 'failure status survives async redraw')
        assert (home / 'post-hook').exists(), 'nonzero exit stopped later precmd hook'
        assert (home / 'keymap-hook').exists(), 'existing keymap widget not called'
        command('MIAMI_CRUISE_SHOW_RETURN_CODE=0; false')
        wait(lambda s: '➤' in lastline(s) and '↵' not in lastline(s), 'hidden return code')
        command('MIAMI_CRUISE_SHOW_RETURN_CODE=1; false')
        wait(lambda s: '1 ↵' in lastline(s), 'return code re-enabled')
        command('true')
        wait(lambda s: '➤' in lastline(s) and '↵' not in lastline(s), 'success unmarked')
        command('MIAMI_CRUISE_SHOW_PIPELINE_STATUS=1; false | true')
        wait(lambda s: '[1|0] ↵' in lastline(s), 'pipeline failure with existing hooks')
        command('MIAMI_CRUISE_SIGNAL_NAMES=1; (exit 130)')
        wait(lambda s: 'SIGINT ↵' in lastline(s), 'signal name')
        command('MIAMI_CRUISE_SHOW_RETURN_CODE=0; false | true')
        wait(lambda s: '↵' not in lastline(s), 'master return-code toggle hides pipeline')
        command('MIAMI_CRUISE_SHOW_RETURN_CODE=1; MIAMI_CRUISE_SHOW_PIPELINE_STATUS=0; MIAMI_CRUISE_SIGNAL_NAMES=0')
        # Re-source while async work is pending; verify each hook appears once.
        command(f'source {theme}; source {theme}')
        command("print -r -- $precmd_functions $preexec_functions > hooks; zstyle -L 'zle-*' widgets >> hooks")
        hooks = (repo / 'hooks').read_text()
        for name in ('miami_cruise_precmd', 'miami_cruise_preexec', 'miami_cruise_mode_update'):
            assert hooks.count(name) == (3 if name.endswith('mode_update') else 1), hooks
        assert 'existing_precmd' in hooks and 'existing_preexec' in hooks and 'existing_keymap' in hooks
        command('MIAMI_CRUISE_SHOW_GIT=0; MIAMI_CRUISE_SHOW_DURATION=0; MIAMI_CRUISE_SHOW_JOBS=0; MIAMI_CRUISE_SHOW_VIRTUALENV=0; MIAMI_CRUISE_SHOW_VI_MODE=0; VIRTUAL_ENV=/tmp/hidden; sleep 0.2')
        wait(lambda s: lastline(s).rstrip().endswith('➤'), 'disabled segments')
        tail = current(screen())
        assert not any(x in tail for x in ('', '[INS]', '(hidden)', '0.2s')), tail
        command('MIAMI_CRUISE_SHOW_GIT=1; MIAMI_CRUISE_ASYNC_GIT=0')
        wait(lambda s: 'cruise' in s, 'sync Git fallback')
        # Fresh screen allows exact transient-vs-persistent context assertions.
        command('clear')
        command('echo LAYOUT_MARKER')
        value = screen()
        before = value.split('echo LAYOUT_MARKER')[0]
        if transient:
            assert '╭─' not in before and 'cruise' not in before, value
        elif single:
            assert '╭─' not in before and 'cruise' in before, value
        else:
            assert '╭─' in before and 'cruise' in before, value
        assert not any(x in screen(True) for x in ('command not found', 'bad math', 'bad file descriptor', 'No handler')), screen(True)
        command(f'MIAMI_CRUISE_ASCII=1; MIAMI_CRUISE_SHOW_VI_MODE=1; source {theme}')
        wait(lambda s: 'git:cruise' in current(s) and '>' in lastline(s), 'ASCII layout and Git')
        tmux('send-keys', '-t', 'test', '-l', 'abcdef')
        tmux('send-keys', '-t', 'test', 'Escape')
        wait(lambda s: '[NOR]' in lastline(s) and '>' in lastline(s), 'ASCII normal label')
        tmux('send-keys', '-t', 'test', '-l', 'v')
        wait(lambda s: '[VIS]' in lastline(s), 'ASCII visual label')
        tmux('send-keys', '-t', 'test', 'Escape')
        tmux('send-keys', '-t', 'test', '-l', 'R')
        wait(lambda s: '[REP]' in lastline(s), 'ASCII replace label')
        tmux('send-keys', '-t', 'test', 'C-c')
        wait(lambda s: '[INS]' in lastline(s), 'ASCII insert label')
        command('clear')  # Exclude the deliberately cancelled edit from scrollback assertions.
        command('false')
        wait(lambda s: '1 exit' in lastline(s), 'ASCII failure symbol')
        command('echo ASCII_MARKER')
        before_ascii = screen().split('echo ASCII_MARKER')[0].split('MIAMI_CRUISE_ASCII=1')[-1]
        if transient:
            assert 'git:cruise' not in before_ascii, before_ascii
        print(f'PASS {variant} single={single} transient={transient}', flush=True)
    finally:
        tmux('kill-server')


with tempfile.TemporaryDirectory(prefix='miami-zsh-tests-') as scratch:
    for variant in ('dark', 'light'):
        for single in (0, 1):
            for transient in (0, 1):
                check(variant, single, transient, Path(scratch))

# Deterministic threshold checks; do not wait three real seconds per case.
for variant in ('dark', 'light'):
    theme = ROOT / f'dist/zsh/miami-cruise-{variant}.zsh-theme'
    script = f'''
source {str(theme)!r}
_miami_cruise_started=$(( EPOCHREALTIME - 2 ))
miami_cruise_precmd
[[ -z $_miami_cruise_duration ]] || exit 1
_miami_cruise_started=$(( EPOCHREALTIME - 4 ))
miami_cruise_precmd
[[ $_miami_cruise_duration == *4.0s* ]] || exit 2
MIAMI_CRUISE_DURATION_THRESHOLD=invalid
_miami_cruise_started=$(( EPOCHREALTIME - 2 ))
miami_cruise_precmd
[[ -z $_miami_cruise_duration ]] || exit 3
MIAMI_CRUISE_DURATION_THRESHOLD=0
_miami_cruise_started=$(( EPOCHREALTIME - 0.5 ))
miami_cruise_precmd
[[ $_miami_cruise_duration == *0.5s* ]] || exit 4
'''
    run('zsh', '-fc', script)
print('PASS default/custom/invalid duration thresholds', flush=True)
