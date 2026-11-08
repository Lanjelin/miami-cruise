"""Capture real btop in isolated config/tmux with only a disposable demo process listed.

BTOP=/path/to/btop sh previews/btop/render.sh
System metrics are live. No personal process list or command lines are captured.
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
    btop = shutil.which(os.environ.get('BTOP', 'btop'))
    if not btop or not shutil.which('tmux'):
        raise SystemExit('Preview needs btop 1.4.8 and tmux; set BTOP if needed.')
    palettes = json.loads((ROOT / 'dist/tokens/tokens.json').read_text())
    with tempfile.TemporaryDirectory(prefix='miami-btop-') as tmp:
        base = Path(tmp)
        env = {k: v for k, v in os.environ.items() if not k.startswith('TMUX') and k != 'NO_COLOR'}
        env.update(TERM='tmux-256color', COLORTERM='truecolor', LC_ALL='C.UTF-8',
                   XDG_CONFIG_HOME=str(base / 'config'), XDG_STATE_HOME=str(base / 'state'))
        themes = base / 'config/btop/themes'
        themes.mkdir(parents=True)
        for path in (ROOT / 'dist/btop').glob('*.theme'):
            shutil.copyfile(path, themes / path.name)
        # Only this process is shown. It consumes a small, bounded amount of one CPU core.
        demo = base / 'mc-dashboard.py'
        demo.write_text('import ctypes,time\nctypes.CDLL(None).prctl(15,b"mc-dashboard",0,0,0)\n'
                        'memory=bytearray(24*1024*1024)\nwhile True:\n'
                        ' end=time.monotonic()+.015\n while time.monotonic()<end: pass\n time.sleep(.085)\n')
        worker = subprocess.Popen([sys.executable, str(demo)], env=env, cwd=base)
        socket = base / 'tmux.sock'

        def run(args, check=True):
            return subprocess.run(args, env=env, cwd=base, capture_output=True, text=True, check=check)

        def tmux(*args, check=True):
            return run(['tmux', '-S', str(socket), *args], check).stdout

        def screen():
            return tmux('capture-pane', '-p', '-e', '-N', '-t', 'preview:0.0')

        def plain(s):
            return re.sub(r'\x1b\[[0-9;]*m', '', s)

        def wait(predicate, label):
            deadline = time.monotonic() + 12
            last = ''
            while time.monotonic() < deadline:
                last = screen()
                if predicate(last):
                    return last
                time.sleep(.1)
            raise RuntimeError(f'Timed out: {label}\n{plain(last)}')

        def key(*values):
            tmux('send-keys', '-t', 'preview:0.0', *values)

        def rgb(value):
            return ';'.join(str(int(value[i:i+2], 16)) for i in (1, 3, 5))

        def start(variant, lowcolor=False):
            conf = base / 'config/btop/btop.conf'
            conf.write_text(f'color_theme = "miami-cruise-{variant}.theme"\n'
                            'truecolor = true\ntheme_background = true\n'
                            'update_ms = 200\nshown_boxes = "cpu mem net proc"\n'
                            'custom_cpu_name = "Miami Cruise"\nclock_format = ""\n'
                            'show_battery = false\nshow_disks = false\ncheck_temp = false\n'
                            'proc_sorting = "pid"\nproc_gradient = true\n')
            args = [btop, '--no-tty', '--filter', '!^mc-dashboard$']
            if lowcolor:
                args += ['--low-color', '--config', str(conf), '--themes-dir', str(themes)]
            command = shlex.join(args) + '; printf "%s" "$?" > exit-code; exec sleep 30'
            tmux('new-session', '-d', '-s', 'preview', '-x', '120', '-y', '36', command)
            tmux('resize-window', '-t', 'preview:0', '-x', '120', '-y', '36')
            return conf

        sections = []
        try:
            # Keep a separate session so successive runs cannot race server shutdown.
            tmux('-f', os.devnull, 'new-session', '-d', '-s', 'keeper', 'sleep 3600')
            tmux('set-option', '-g', 'status', 'off')
            for variant, p in palettes.items():
                conf = start(variant)
                wait(lambda s: str(worker.pid) in plain(s), 'filtered demo process')
                key('Down')
                shot = wait(lambda s: '48;2;' + rgb(p['accent']) in s, 'selected process')
                for token in ('text', 'accent', 'info', 'success', 'orchid'):
                    assert '38;2;' + rgb(p[token]) in shot, (variant, token)
                assert '48;2;' + rgb(p['bg']) in shot
                assert '38;2;' + rgb(p['on-accent']) in shot
                # Let the real app accumulate some graph history before capture.
                time.sleep(1)
                shot = screen()
                sections.append(f'<section style="background:{p["bg"]};color:{p["text"]}">'
                                f'<header style="color:{p["accent"]}">Miami Cruise · btop · {variant} · live metrics / demo process</header>'
                                f'<pre>{ansi_html(shot, p)}</pre></section>')
                key('u')
                wait(lambda s: '48;2;' + rgb(p['warning']) in s, 'paused-list banner')
                key('u')
                key('F')
                wait(lambda s: '48;2;' + rgb(p['info']) in s, 'followed-process banner')
                key('F')
                key('f')
                tmux('send-keys', '-t', 'preview:0.0', '-l', '--', 'x')
                wait(lambda s: str(worker.pid) not in plain(s), 'process filter')
                key('Escape')
                wait(lambda s: str(worker.pid) in plain(s), 'restored filter')
                key('h')
                wait(lambda s: 'Help' in plain(s) or 'help' in plain(s) and 'Key' in plain(s), 'help')
                key('Escape')
                key('o')
                wait(lambda s: 'color_theme' in plain(s) or 'Color theme' in plain(s), 'options')
                other = 'light' if variant == 'dark' else 'dark'
                key('Right' if variant == 'dark' else 'Left')
                wait(lambda s: f'miami-cruise-{other}' in plain(s) and '38;2;' + rgb(palettes[other]['accent']) in s,
                     'native theme switch')
                key('Escape')
                key('q')
                deadline = time.monotonic() + 10
                while not (base / 'exit-code').exists() and time.monotonic() < deadline:
                    time.sleep(.1)
                assert (base / 'exit-code').read_text() == '0'
                saved = conf.read_text()
                assert f'miami-cruise-{other}' in saved
                assert 'proc_sorting = "pid"' in saved, 'Unrelated setting changed'
                (base / 'exit-code').unlink()
                tmux('kill-session', '-t', 'preview')
                start(variant, lowcolor=True)
                low = wait(lambda s: str(worker.pid) in plain(s), '256-colour mode')
                assert '38;5;' in low and '38;2;' not in low, '256-colour conversion missing'
                key('q')
                tmux('kill-session', '-t', 'preview')
            css = '''body{margin:0;padding:14px;display:grid;gap:14px;background:transparent}
section{border-radius:8px;overflow:hidden;padding:16px 20px}
header{font:600 15px system-ui;margin-bottom:12px}
pre{font:15px/1.25 'DejaVu Sans Mono',monospace;margin:0;white-space:pre}'''
            output.write_text('<!doctype html><meta charset="utf-8"><style>' + css + '</style>' + ''.join(sections))
        finally:
            tmux('kill-server', check=False)
            worker.terminate()
            worker.wait(timeout=5)
    print('Verified btop: both themes, RGB, panels, selection, pause/follow banners, filter, help/options, theme switch, saved/custom config and 256-colour fallback.', file=sys.stderr)


if __name__ == '__main__':
    capture(Path(sys.argv[1]))
