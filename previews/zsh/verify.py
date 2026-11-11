"""Exercise layout/transient flags in real, isolated Oh My Zsh + tmux sessions.

Run with ZSH pointing to an Oh My Zsh checkout: python3 -I previews/zsh/verify.py
"""
import os
from pathlib import Path
import subprocess
import tempfile
import time

ROOT = Path(__file__).resolve().parents[2]
OMZ = Path(os.environ.get('ZSH', Path.home() / '.local/share/oh-my-zsh'))
assert (OMZ / 'oh-my-zsh.sh').is_file(), 'Set ZSH to an Oh My Zsh checkout'

with tempfile.TemporaryDirectory(prefix='miami-prompt-check-') as scratch:
    base = Path(scratch)
    for variant in ('dark', 'light'):
        for single in (0, 1):
            for transient in (0, 1):
                folder = base / f'{variant}-{single}-{transient}'
                folder.mkdir()
                context = folder / 'context-path'
                context.mkdir()
                theme = ROOT / f'dist/zsh/miami-cruise-{variant}.zsh-theme'
                zdot = folder / '.config/zsh'
                zdot.mkdir(parents=True)
                (zdot / '.zshrc').write_text(
                    f'ZSH={str(OMZ)!r}\nplugins=()\nZSH_THEME=""\n'
                    'DISABLE_AUTO_UPDATE=true\nZSH_DISABLE_COMPFIX=true\n'
                    'source "$ZSH/oh-my-zsh.sh"\n'
                    f'MIAMI_CRUISE_SINGLE_LINE={single}\nMIAMI_CRUISE_TRANSIENT_PROMPT={transient}\n'
                    # Re-sourcing must not duplicate hook registration.
                    f'source {str(theme)!r}\nsource {str(theme)!r}\n'
                    'bindkey -e\n')
                env = {k: v for k, v in os.environ.items() if not k.startswith(('ZSH', 'TMUX', 'MIAMI_CRUISE_'))}
                env.update(HOME=str(folder), ZDOTDIR=str(zdot), TERM='tmux-256color')
                socket = str(folder / 'socket')

                def tmux(*args, check=True):
                    return subprocess.run(['tmux', '-S', socket, *args], env=env,
                                          check=check, text=True, capture_output=True).stdout

                def wait(predicate):
                    deadline = time.monotonic() + 8
                    while time.monotonic() < deadline:
                        time.sleep(.1)
                        screen = tmux('capture-pane', '-p', '-S', '-', '-t', 'test')
                        if predicate(screen):
                            return screen
                        time.sleep(.05)
                    raise AssertionError((variant, single, transient, screen))

                def send(text):
                    tmux('send-keys', '-t', 'test', '-l', text)
                    tmux('send-keys', '-t', 'test', 'Enter')

                try:
                    tmux('-f', '/dev/null', 'new-session', '-d', '-s', 'test', '-x', '160', '-y', '40',
                         '-c', str(context), 'zsh', '-i')
                    tmux('set-option', '-g', 'status', 'off')
                    # Otherwise a full-screen ZLE redraw is archived as history by tmux.
                    tmux('set-window-option', '-g', 'scroll-on-clear', 'off')
                    initial = wait(lambda s: 'context-path' in s and '➤' in s)
                    assert ('╭─' in initial) == (not single)
                    send("print -r -- OUTPUT_ONE")
                    screen = wait(lambda s: '\nOUTPUT_ONE\n' in s and s.count('➤') >= 2)
                    assert screen.count('context-path') == (1 if transient else 2), screen
                    assert '➤  print -r -- OUTPUT_ONE' in screen, screen
                    send('false')
                    screen = wait(lambda s: '1 ↵' in s and s.count('➤') >= 3)
                    assert screen.count('context-path') == (1 if transient else 3), screen
                    # Wrapped input retains the entire command after shrinking.
                    send("print -r -- " + 'x' * 190 + ' WRAP_END')
                    wait(lambda s: '\n' + 'x' * 160 in s and 'WRAP_END' in s and s.count('➤') >= 4)
                    # Cancellation must restore full context on the next edit.
                    tmux('send-keys', '-t', 'test', '-l', 'unsubmitted')
                    tmux('send-keys', '-t', 'test', 'C-c')
                    wait(lambda s: s.count('➤') >= 5 and 'context-path' in s)
                    # A real multiline buffer must still execute intact.
                    tmux('send-keys', '-t', 'test', '-l', "print -r -- 'MULTI_START")
                    tmux('send-keys', '-t', 'test', 'C-v', 'C-j')
                    tmux('send-keys', '-t', 'test', '-l', "MULTI_END'")
                    tmux('send-keys', '-t', 'test', 'Enter')
                    wait(lambda s: '\nMULTI_START\nMULTI_END\n' in s and s.count('➤') >= 6)
                    print(f'Verified {variant}: single_line={single}, transient={transient}')
                finally:
                    tmux('kill-server', check=False)
