"""Native plugin preview fixtures, captured through isolated tmux servers."""
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import tempfile
import time

from _terminal import ansi_html

ROOT = Path(__file__).resolve().parents[1]


def render(app, output):
    airline = app == 'airline'
    key = 'AIRLINE' if airline else 'ZSH_AUTOSUGGESTIONS'
    dependency = Path(os.environ.get(key, '/nonexistent')).resolve()
    expected = dependency / ('plugin/airline.vim' if airline else 'zsh-autosuggestions.zsh')
    if not expected.is_file():
        raise SystemExit(f'Set {key} to an existing upstream plugin checkout. No plugin is installed by this script.')
    palettes = json.loads((ROOT / 'dist/tokens/tokens.json').read_text())
    sections = []
    with tempfile.TemporaryDirectory(prefix='miami-plugin-preview-') as scratch:
        base = Path(scratch)
        for variant, p in palettes.items():
            home = base / variant
            home.mkdir()
            env = {k: v for k, v in os.environ.items() if not k.startswith(('TMUX', 'ZSH', 'VIM', 'GIT_'))}
            env.update(HOME=str(home), SHELL='/bin/sh', TERM='tmux-256color', COLORTERM='truecolor',
                       LC_ALL='C.UTF-8', ZDOTDIR=str(home), XDG_CONFIG_HOME=str(home / '.config'),
                       XDG_CACHE_HOME=str(home / '.cache'))
            socket = home / 'tmux.sock'

            def tm(*args, check=True):
                return subprocess.run(['tmux', '-S', str(socket), *args], env=env, cwd=home,
                                      capture_output=True, text=True, check=check).stdout

            def screen():
                return tm('capture-pane', '-p', '-e', '-t', 'preview:0.0')

            def wait(needle):
                end = time.monotonic() + 10
                last = ''
                while time.monotonic() < end:
                    last = screen()
                    if needle in re.sub(r'\x1b\[[0-9;]*m', '', last):
                        time.sleep(.2)
                        return screen()
                    time.sleep(.08)
                raise RuntimeError(f'{app}/{variant}: waiting for {needle!r}: {last}')

            try:
                if airline:
                    sample = home / 'cruise.py'
                    sample.write_text('# Miami Cruise / native vim-airline\n\ndef night_drive(destination):\n    playlist = ["Ocean Drive", "Neon Skyline"]\n    return f"Cruising to {destination}"\n\nnight_drive("Miami Beach")\n')
                    init = home / 'preview.vim'
                    init.write_text(f'''set nocompatible
set rtp^={dependency}
set rtp+={ROOT}/dist/airline
set rtp+={ROOT}/dist/vim
set termguicolors background={variant}
syntax on
colorscheme miami-cruise
let g:airline_theme = 'miami_cruise'
let g:airline_powerline_fonts = 0
let g:airline_left_sep = ''
let g:airline_right_sep = ''
let g:airline_skip_empty_sections = 1
let g:airline_symbols_ascii = 1
let g:airline_extensions = []
set laststatus=2 noshowmode noruler noshowcmd nonumber
runtime plugin/airline.vim
''')
                    command = shlex.join(['vim', '-N', '-u', str(init), '-n', '-i', 'NONE', str(sample)])
                else:
                    init = home / '.zshrc'
                    init.write_text(f'''HOST=cruise
HISTFILE=/dev/null
MIAMI_CRUISE_ASCII=1
source {shlex.quote(str(ROOT / f'dist/zsh/miami-cruise-{variant}.zsh-theme'))}
source {shlex.quote(str(ROOT / "previews/identity.zsh"))}
source {shlex.quote(str(expected))}
source {shlex.quote(str(ROOT / f'dist/zsh_autosuggestions/miami-cruise-{variant}.zsh'))}
print -s -- 'git status --short'
print -s -- 'python3 -m http.server 8000'
print -s -- 'cd projects/miami-cruise'
''')
                    # Global zshenv on some hosts redirects ZDOTDIR here.
                    (home / '.config/zsh').mkdir(parents=True)
                    (home / '.config/zsh/.zshrc').symlink_to(init)
                    command = 'zsh -i'
                tm('-f', '/dev/null', 'new-session', '-d', '-s', 'preview', '-x', '94', '-y', '13', command)
                tm('set-option', '-g', 'status', 'off')
                captures = []
                if airline:
                    captures.append(('Normal', wait('NORMAL')))
                    for mode, keys in [('Insert', ['i']), ('Visual', ['Escape', 'v', 'l', 'l']), ('Replace', ['Escape', 'R'])]:
                        tm('send-keys', '-t', 'preview:0.0', *keys)
                        shot = wait(mode.upper())
                        captures.append((mode, '\n'.join(shot.splitlines()[-2:-1])))
                else:
                    time.sleep(.8)
                    for prefix, completion in [('git st', 'git status --short'), ('python3 -m', 'python3 -m http.server 8000'), ('cd proj', 'cd projects/miami-cruise')]:
                        tm('send-keys', '-t', 'preview:0.0', 'C-u')
                        tm('send-keys', '-l', '-t', 'preview:0.0', prefix)
                        shot = wait(completion)
                        assert 'miami@cruise' in re.sub(r'\x1b\[[0-9;]*m', '', shot), 'Preview identity drifted'
                        rgb = ';'.join(str(int(p['muted'][i:i+2], 16)) for i in (1, 3, 5))
                        assert '38;2;' + rgb in shot, 'Suggestion did not use the generated RGB style'
                        captures.append((prefix, '\n'.join(shot.rstrip().splitlines()[-3:])))
                content = ''.join(f'<pre>{ansi_html(shot.rstrip(), p)}</pre>' for _, shot in captures)
                name = 'vim-airline' if airline else 'zsh-autosuggestions'
                sections.append(f'<section style="background:{p["bg"]};color:{p["text"]}"><header style="color:{p["accent"]}">Miami Cruise · {name} · {variant}</header>{content}</section>')
            finally:
                tm('kill-server', check=False)
    css = "body{margin:0;padding:14px;display:grid;gap:14px;background:transparent}section{border-radius:8px;overflow:hidden;padding:16px 20px}header{font:600 15px system-ui;margin-bottom:14px}pre{font:15px/19px 'DejaVu Sans Mono',monospace;white-space:pre;margin:0 0 14px}pre:last-child{margin-bottom:0}"
    output.write_text('<!doctype html><meta charset="utf-8"><style>' + css + '</style>' + ''.join(sections))
    print(f'Captured native {app}: dark/light plugin output in disposable tmux sessions.')
