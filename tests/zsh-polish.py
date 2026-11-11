#!/usr/bin/env python3
"""Real ZLE timestamp/transient/path-lock checks; disposable tmux servers only.
Run python3 -I build.py zsh, then python3 tests/zsh-polish.py.
Requires only the existing test tools: Python stdlib, Zsh and tmux.
"""
from pathlib import Path
import os
import re
import subprocess
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
CLOCK = re.compile(r'\d{2}:\d{2}:\d{2}\s*$')


def check(base, variant, single, transient, ascii_mode):
    home = base / f'{variant}-{single}-{transient}-{ascii_mode}'
    home.mkdir()
    locked = home / 'readonly'
    locked.mkdir(mode=0o555)
    other = home / 'other'
    other.mkdir()
    (home / '.config/zsh').mkdir(parents=True)
    (home / '.config/zsh/.zshrc').symlink_to(home / '.zshrc')
    theme = ROOT / f'dist/zsh/miami-cruise-{variant}.zsh-theme'
    (home / '.zshrc').write_text(f'''
MIAMI_CRUISE_SINGLE_LINE={single}
MIAMI_CRUISE_TRANSIENT_PROMPT={transient}
MIAMI_CRUISE_ASCII={ascii_mode}
MIAMI_CRUISE_SHOW_TIMESTAMP=1
MIAMI_CRUISE_SHOW_READ_ONLY=1
MIAMI_CRUISE_SHOW_GIT=0
MIAMI_CRUISE_SHOW_VI_MODE=1
MIAMI_CRUISE_SHOW_SHELL_LEVEL=1
YAZI_LEVEL=2
bindkey -v
source {str(theme)!r}
''')
    env = {k: v for k, v in os.environ.items() if not k.startswith(('MIAMI_CRUISE_', 'TMUX'))}
    env.update(HOME=str(home), ZDOTDIR=str(home), TERM='tmux-256color', TZ='UTC')
    sock = str(home / 'tmux.sock')

    def tmux(*args):
        return subprocess.run(['tmux', '-S', sock, *args], check=True, env=env,
                              text=True, capture_output=True).stdout

    def screen():
        return tmux('capture-pane', '-p', '-t', 'test')

    def lastline(value):
        return ([line for line in value.splitlines() if line.strip()] or [''])[-1]

    def wait(predicate, label):
        deadline = time.monotonic() + 4
        while time.monotonic() < deadline:
            value = screen()
            if predicate(value):
                return value
            time.sleep(.025)
        raise AssertionError(f'{variant}/{single}/{transient}/{ascii_mode}: {label}\n{screen()}')

    def command(value):
        tmux('send-keys', '-t', 'test', '-l', value)
        tmux('send-keys', '-t', 'test', 'Enter')
        time.sleep(.06)
        return wait(lambda s: ('[INS]' if ascii_mode else '➤') in lastline(s), value)

    def submitted(marker, full, folder):
        lines = screen().splitlines()
        idx = next(i for i, line in enumerate(lines) if f'echo {marker}' in line)
        line = lines[idx]
        has_context = (f'~/{folder}' in line if single else
                       line.lstrip().startswith('+-' if ascii_mode else '╰─') and
                       f'~/{folder}' in lines[idx-1])
        assert has_context == full, (marker, full, '\n'.join(lines[max(0, idx-1):idx+1]))
        assert CLOCK.search(line), ('submission timestamp missing/not rightmost', line)
        return CLOCK.search(line).group().strip()

    try:
        tmux('-f', '/dev/null', 'new-session', '-d', '-s', 'test', '-x', '150', '-y', '40',
             '-c', str(locked), 'zsh', '-i')
        tmux('set-option', '-g', 'status', 'off')
        tmux('set-option', '-g', 'scroll-on-clear', 'off')
        value = wait(lambda s: ('[INS]' if ascii_mode else '➤') in lastline(s) and CLOCK.search(lastline(s)), 'startup timestamp')
        lock = '[RO]' if ascii_mode else ''
        assert lock + ' ~/readonly' in value, value
        assert lock not in lastline(value).split('➤' if not ascii_mode else '>')[-1], value
        initial_time = CLOCK.search(lastline(value)).group().strip()
        tmux('send-keys', '-t', 'test', '-l', 'echo FIRST_VISIT')
        if transient == 'same-dir' and not ascii_mode:
            # Idle editing must not freeze the submitted timestamp at prompt creation.
            time.sleep(1.1)
        tmux('send-keys', '-t', 'test', 'Enter')
        time.sleep(.06)
        wait(lambda s: ('[INS]' if ascii_mode else '➤') in lastline(s), 'after first command')
        stamp = submitted('FIRST_VISIT', transient != '1', 'readonly')
        if transient == 'same-dir' and not ascii_mode:
            assert stamp != initial_time, (stamp, initial_time)
        command('echo REPEATED')
        submitted('REPEATED', transient == '0', 'readonly')
        command('false')
        assert re.search(r'1 (?:exit|↵) \d{2}:\d{2}:\d{2}\s*$', lastline(screen())), screen()
        command(f'cd {other}')
        if transient == 'same-dir':
            tmux('send-keys', '-t', 'test', '-l', 'cancelled')
            tmux('send-keys', '-t', 'test', 'C-c')
            tmux('send-keys', '-t', 'test', 'Enter')
            time.sleep(.06)
        command('echo OTHER_FIRST')
        submitted('OTHER_FIRST', transient != '1', 'other')
        assert lock not in lastline(screen()), screen()
        command('echo OTHER_REPEAT')
        submitted('OTHER_REPEAT', transient == '0', 'other')
        command(f'cd {locked}')
        command('echo RETURN_FIRST')
        submitted('RETURN_FIRST', transient != '1', 'readonly')
        # Clock is far right after shell-level/mode/status, and can be disabled.
        command('MIAMI_CRUISE_SHOW_TIMESTAMP=0; true')
        assert CLOCK.search(lastline(screen())) is None, screen()
        if ascii_mode:
            assert all(ord(c) < 128 for c in screen()), screen()
        assert 'command not found' not in screen(), screen()
        print(f'PASS {variant} single={single} transient={transient} ascii={ascii_mode}', flush=True)
    finally:
        tmux('kill-server')


with tempfile.TemporaryDirectory(prefix='miami-zsh-polish-') as scratch:
    for variant in ('dark', 'light'):
        for single in (0, 1):
            for transient in ('0', '1', 'same-dir'):
                for ascii_mode in (0, 1):
                    check(Path(scratch), variant, single, transient, ascii_mode)
