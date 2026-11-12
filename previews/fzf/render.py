"""Exercise real fzf in an isolated tmux server; capture its screen, not a mockup.

FZF=/path/to/fzf BAT=/path/to/bat sh previews/fzf/render.sh
Only disposable files/config/cache and this app's preview are written.
"""
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import time

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / 'previews')]
from _terminal import ansi_html


def capture(output):
    fzf = shutil.which(os.environ.get('FZF', 'fzf'))
    bat = shutil.which(os.environ.get('BAT', 'bat')) or shutil.which('batcat')
    if not fzf or not bat or not shutil.which('tmux'):
        raise SystemExit('Preview needs fzf, bat and tmux; set FZF and BAT if needed.')
    tokens = json.loads((ROOT / 'dist/tokens/tokens.json').read_text())
    with tempfile.TemporaryDirectory(prefix='miami-fzf-') as tmp:
        base = Path(tmp)
        env = {k: v for k, v in os.environ.items()
               if not k.startswith(('FZF_', 'BAT_', 'TMUX')) and k != 'NO_COLOR'}
        env.update(SHELL='/bin/sh', TERM='tmux-256color', COLORTERM='truecolor', LC_ALL='C.UTF-8',
                   XDG_CONFIG_HOME=str(base / 'config'), XDG_CACHE_HOME=str(base / 'cache'),
                   BAT_CONFIG_DIR=str(base / 'bat'))
        config = base / 'bat/themes'
        config.mkdir(parents=True)
        for path in (ROOT / 'dist/bat').glob('*.tmTheme'):
            shutil.copyfile(path, config / path.name)
        subprocess.run([bat, 'cache', '--build'], env=env, capture_output=True, check=True)
        names = ['cruise.py', 'cruise-night.py', 'cruise light.py', 'cruise-dawn.py', 'palette.json', 'README.md', 'theme.yml']
        sample = (ROOT / 'previews/bat/sample.py').read_text()
        for name in names:
            (base / name).write_text(sample if name.endswith('.py') else '# Miami Cruise\n')
        (base / 'files').write_text('\n'.join(names) + '\n')
        existing_opts = base / 'existing.opts'
        existing_opts.write_text('--border\n--bind=ctrl-y:change-prompt:KEPT-BINDING\n')
        socket = base / 'tmux.sock'

        def run(args, **kwargs):
            return subprocess.run(args, env=env, cwd=base, capture_output=True,
                                  text=True, **kwargs)

        def tmux(*args, check=True):
            return run(['tmux', '-S', str(socket), *args], check=check).stdout

        def screen():
            return tmux('capture-pane', '-p', '-e', '-N', '-t', 'preview:0.0')

        def plain(s):
            return re.sub(r'\x1b\[[0-9;]*m', '', s)

        def wait(predicate, label):
            deadline = time.monotonic() + 10
            last = ''
            while time.monotonic() < deadline:
                last = screen()
                if predicate(last):
                    return last
                time.sleep(.08)
            raise RuntimeError(f'Timed out: {label}\n{plain(last)}')

        def key(*values):
            tmux('send-keys', '-t', 'preview:0.0', *values)

        def text(value):
            tmux('send-keys', '-t', 'preview:0.0', '-l', '--', value)

        def start(command):
            tmux('-f', os.devnull, 'new-session', '-d', '-s', 'preview', '-x', '112', '-y', '28', command)
            tmux('set-option', '-g', 'status', 'off')
            tmux('resize-window', '-t', 'preview:0', '-x', '112', '-y', '28')

        def rgb(value):
            return ';'.join(str(int(value[i:i+2], 16)) for i in (1, 3, 5))

        sections = []
        try:
            for variant, p in tokens.items():
                theme = ROOT / f'dist/fzf/miami-cruise-{variant}.opts'
                bat_theme = f'miami-cruise-{variant}'
                preview = shlex.join([bat, '--color=always', '--paging=never', '--style=numbers',
                                      '--theme=' + bat_theme, '--']) + ' {}'
                args = [fzf, '--sync', '--layout=reverse', '--border', '--multi', '--no-sort',
                        '--preview', preview, '--preview-window=right:60%',
                        '--preview-label= bat syntax ', '--prompt=Find > ']
                defaults = '--header="Tab: select | Enter: accept | Esc: cancel"'
                command = ('env ' + shlex.quote('FZF_DEFAULT_OPTS_FILE=' + str(theme)) + ' ' +
                           shlex.quote('FZF_DEFAULT_OPTS=' + defaults) + ' ' + shlex.join(args) +
                           ' < files > result; printf "%s" "$?" > exit-code; exec sleep 30')
                start(command)
                wait(lambda s: '7/7' in plain(s) and 'Miami' in plain(s), 'native option file + bat preview')
                text('cru')
                wait(lambda s: '4/7' in plain(s), 'search')
                key('Tab', 'Tab')
                shot = wait(lambda s: '4/7 (2)' in plain(s), 'multi-selection')
                # The selected filename contains a space: {} must remain safely quoted by fzf.
                shot = wait(lambda s: 'Miami' in plain(s) and '38;2;' + rgb(p['success']) in s,
                            'matching bat syntax on file with spaces')
                for prefix, token in [('38;2;', 'accent'), ('48;2;', 'hover'), ('38;2;', 'text')]:
                    assert prefix + rgb(p[token]) in shot, (variant, token)
                assert '\x1b[4' in shot or ';4;' in shot or ';4m' in shot, 'Underlined current matches missing'
                sections.append(f'<section style="background:{p["bg"]};color:{p["text"]}">'
                                f'<header style="color:{p["accent"]}">Miami Cruise · fzf · {variant} · optional bat preview</header>'
                                f'<pre>{ansi_html(shot, p)}</pre></section>')
                key('C-u')
                text('zzzz-no-match')
                wait(lambda s: '0/7' in plain(s), 'no matches')
                key('C-u')
                text('cru')
                wait(lambda s: '4/7' in plain(s), 'restored search')
                key('Enter')
                deadline = time.monotonic() + 10
                while not (base / 'exit-code').exists() and time.monotonic() < deadline:
                    time.sleep(.08)
                assert (base / 'exit-code').read_text() == '0'
                assert (base / 'result').read_text().splitlines() == names[:2], 'Accepted selection differs'
                tmux('kill-server')
                # Verify the documented append method in both installed shells, without bat.
                for shell in ('bash', 'zsh'):
                    if not shutil.which(shell):
                        continue
                    code = ('export FZF_DEFAULT_OPTS="${FZF_DEFAULT_OPTS-} $(cat ' + shlex.quote(str(theme)) + ')"\n' +
                            shlex.quote(fzf) + ' --sync < files > result; printf "%s" "$?" > cancelled; exec sleep 30')
                    command = ('env ' + shlex.quote('FZF_DEFAULT_OPTS_FILE=' + str(existing_opts)) + ' ' +
                               shlex.quote('FZF_DEFAULT_OPTS=--header=KEEP-EXISTING --layout=reverse') +
                               ' ' + shlex.join([shell, '-c', code]))
                    start(command)
                    wait(lambda s: 'KEEP-EXISTING' in plain(s) and '38;2;' + rgb(p['accent']) in s,
                         shell + ' append method, no preview dependency')
                    key('C-y')
                    wait(lambda s: 'KEPT-BINDING' in plain(s), 'binding retained from existing options file')
                    key('Escape')
                    deadline = time.monotonic() + 10
                    while not (base / 'cancelled').exists() and time.monotonic() < deadline:
                        time.sleep(.08)
                    assert (base / 'cancelled').read_text() == '130'
                    (base / 'cancelled').unlink()
                    tmux('kill-server')
                (base / 'exit-code').unlink()
            css = '''body{margin:0;padding:14px;display:grid;gap:14px;background:transparent}
section{border-radius:8px;overflow:hidden;padding:16px 20px}
header{font:600 15px system-ui;margin-bottom:12px}
pre{font:15px/1.25 'DejaVu Sans Mono',monospace;margin:0;white-space:pre}'''
            output.write_text('<!doctype html><meta charset="utf-8"><style>' + css + '</style>' + ''.join(sections))
        finally:
            tmux('kill-server', check=False)
    print('Verified fzf: both variants, native file, Bash/Zsh append, search, selection, accept/cancel, no matches and bat preview.', file=sys.stderr)


if __name__ == '__main__':
    capture(Path(sys.argv[1]))
