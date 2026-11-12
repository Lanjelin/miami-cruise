"""Verify colours and preservation in disposable tmux servers, including the status bar.

An outer tmux captures a real attached inner client: capture-pane on the inner
server alone would omit its status bar, borders, menus and message overlays.
The demonstration layout is preview-only, never part of the theme files.
"""
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys
import tempfile
import time

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / 'previews')]
from _terminal import ansi_html
from themes.tmux import STYLES


def capture(output):
    palettes = json.loads((ROOT / 'dist/tokens/tokens.json').read_text())
    with tempfile.TemporaryDirectory(prefix='miami-tmux-') as tmp:
        base = Path(tmp)
        env = {k: v for k, v in os.environ.items() if not k.startswith('TMUX') and k != 'NO_COLOR'}
        env.update(SHELL='/bin/sh', TERM='tmux-256color', COLORTERM='truecolor', LC_ALL='C.UTF-8',
                   XDG_CONFIG_HOME=str(base / 'config'), XDG_CACHE_HOME=str(base / 'cache'))
        outer, inner = base / 'outer.sock', base / 'inner.sock'

        def tm(socket, *args, check=True):
            return subprocess.run(['tmux', '-S', str(socket), *args], env=env,
                                  cwd=base, text=True, capture_output=True, check=check).stdout

        def value(option, window=False):
            return tm(inner, 'show-options', '-gwv' if window else '-gv', option).strip()

        def screen():
            return tm(outer, 'capture-pane', '-p', '-e', '-N', '-t', 'viewer:0.0')

        def wait(predicate, label):
            deadline = time.monotonic() + 8
            while time.monotonic() < deadline:
                s = screen()
                if predicate(s):
                    return s
                time.sleep(.08)
            raise RuntimeError(f'Timed out: {label}\n{s}')

        def rgb(h):
            return ';'.join(str(int(h[i:i + 2], 16)) for i in (1, 3, 5))

        def has_colour(s, h, background=False):
            return ('48' if background else '38') + ';2;' + rgb(h) in s

        def source(variant):
            tm(inner, 'source-file', str(ROOT / f'dist/tmux/miami-cruise-{variant}.conf'))

        changed = {option for _, option, _, _ in STYLES} | {
            'display-panes-colour', 'display-panes-active-colour', 'clock-mode-colour'}

        def unrelated():
            # Includes all format strings, lengths, positions, hooks and behaviour.
            return '\n'.join(line for flag in ('-g', '-gw', '-gs')
                             for line in tm(inner, 'show-options', flag).splitlines()
                             if line.split(' ', 1)[0] not in changed)

        sections = []
        try:
            tm(outer, '-f', os.devnull, 'new-session', '-d', '-s', 'keeper', 'sleep 3600')
            tm(outer, 'set-option', '-g', 'status', 'off')
            tm(inner, '-f', os.devnull, 'new-session', '-d', '-s', 'cruise', '-n', 'editor',
               '-x', '112', '-y', '20', 'sleep 3600')
            # Sentinel powerline strings with explicit colours must not be rewritten.
            tm(inner, 'set-option', '-g', 'status-left', '#[fg=red] session \ue0b0 ')
            tm(inner, 'set-option', '-g', 'status-right', '#[fg=blue] CPU #{pane_index} \ue0b2')
            tm(inner, 'set-option', '-gw', 'window-status-format', ' #I:#W \ue0b0 ')
            tm(inner, 'set-option', '-gw', 'window-status-current-format', ' #I:#W#F \ue0b0 ')
            tm(inner, 'set-option', '-g', 'status-style', 'bold,italics')
            tm(inner, 'set-option', '-g', 'prefix', 'C-a')
            tm(inner, 'bind-key', 'Y', 'display-message', 'kept binding')
            tm(inner, 'set-option', '-g', '@fixture', 'kept user option')
            before, bindings = unrelated(), tm(inner, 'list-keys')
            for variant, p in palettes.items():
                source(variant)
                source(variant)
                assert before == unrelated(), 'Non-colour options changed'
                assert bindings == tm(inner, 'list-keys'), 'Bindings changed'
                assert 'bold' in value('status-style') and 'italics' in value('status-style')
                for scope, option, fg, bg in STYLES:
                    got = value(option, scope == 'w')
                    assert f'fg={p[fg]}' in got, (variant, option, got)
                    if bg:
                        assert f'bg={p[bg]}' in got, (variant, option, got)
                # Local overrides are also deliberately preserved.
                tm(inner, 'set-option', '-t', 'cruise', 'status-right-style', 'fg=red,bg=blue')
                source(variant)
                assert tm(inner, 'show-options', '-v', '-t', 'cruise', 'status-right-style').strip() == 'fg=red,bg=blue'
                tm(inner, 'set-option', '-u', '-t', 'cruise', 'status-right-style')
            # Preview fixture only; no hard-coded inline colours obscure the base styles.
            tm(inner, 'set-option', '-g', 'status-left', ' #{session_name} ')
            tm(inner, 'set-option', '-g', 'status-right', ' colour-only ')
            tm(inner, 'set-option', '-gw', 'window-status-format', ' #I:#W ')
            tm(inner, 'set-option', '-gw', 'window-status-current-format', ' #I:#W#F ')
            tm(inner, 'set-option', '-g', 'status-style', 'default')
            tm(inner, 'new-window', '-d', '-t', 'cruise', '-n', 'logs', 'sleep 3600')
            tm(inner, 'split-window', '-h', '-t', 'cruise:0', 'sleep 3600')
            tm(inner, 'select-pane', '-t', 'cruise:0.0')
            command = shlex.join(['tmux', '-S', str(inner), '-T', 'RGB', 'attach-session', '-t', 'cruise'])
            tm(outer, 'new-session', '-d', '-s', 'viewer', '-x', '112', '-y', '20', command)
            wait(lambda s: 'colour-only' in s, 'attached inner client')
            client = tm(inner, 'list-clients', '-F', '#{client_name}').strip()
            fixture = base / 'fixture.py'
            fixture.write_text('import sys,time\nprint(sys.argv[1],flush=True)\ntime.sleep(3600)\n')
            for variant, p in palettes.items():
                source(variant)
                for pane, label in [(0, 'EDITOR'), (1, 'LOGS')]:
                    text = (f'\033[38;2;{rgb(p["text"])}m\033[48;2;{rgb(p["bg"])}m\033[2J\033[H'
                            f'MIAMI CRUISE / {label}\n\n'
                            'Your applications keep their own colours.\n\n'
                            'Existing status layout and keybindings stay.\n'
                            'Only tmux chrome receives this palette.\n\n'
                            'Copy selection uses the magenta accent.\n')
                    tm(inner, 'respawn-pane', '-k', '-t', f'cruise:0.{pane}',
                       shlex.join([sys.executable, str(fixture), text]))
                wait(lambda s: 'MIAMI CRUISE / EDITOR' in s and has_colour(s, p['accent'], True), 'RGB status bar')
                tm(inner, 'copy-mode', '-t', 'cruise:0.0')
                tm(inner, 'send-keys', '-t', 'cruise:0.0', '-X', 'history-top')
                tm(inner, 'send-keys', '-t', 'cruise:0.0', '-X', '-N', '7', 'cursor-down')
                tm(inner, 'send-keys', '-t', 'cruise:0.0', '-X', 'start-of-line')
                tm(inner, 'send-keys', '-t', 'cruise:0.0', '-X', 'begin-selection')
                tm(inner, 'send-keys', '-t', 'cruise:0.0', '-X', '-N', '14', 'cursor-right')
                shot = wait(lambda s: has_colour(s.splitlines()[7], p['accent'], True)
                            and 'Copy selection' in re.sub(r'\x1b\[[0-9;]*m', '', s.splitlines()[7]), 'copy selection')
                sections.append(f'<section style="background:{p["bg"]};color:{p["text"]}">'
                                f'<header style="color:{p["accent"]}">Miami Cruise · tmux · {variant} · colour-only / demo layout</header>'
                                f'<pre>{ansi_html(shot, p, fixed_cells=True)}</pre></section>')
                tm(inner, 'send-keys', '-t', 'cruise:0.0', '-X', 'cancel')
                tm(inner, 'display-message', '-c', client, '-d', '5000', 'Miami Cruise message')
                wait(lambda s: 'Miami Cruise message' in s and has_colour(s, p['text']), 'message')
                tm(outer, 'send-keys', '-t', 'viewer:0.0', 'Escape')
                menu = subprocess.Popen(['tmux', '-S', str(inner), 'display-menu', '-c', client,
                                         '-T', 'Miami menu', '-x', 'C', '-y', 'C',
                                         'Selected entry', 'a', 'display-message menu-accepted', 'Other entry', 'b', ''],
                                        env=env, cwd=base, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
                try:
                    wait(lambda s: 'Selected entry' in s and has_colour(s, p['accent']), 'menu')
                finally:
                    tm(outer, 'send-keys', '-t', 'viewer:0.0', 'Escape')
                    tm(outer, 'send-keys', '-t', 'viewer:0.0', 'a')
                    menu.wait(timeout=5)
                popup = subprocess.Popen(['tmux', '-S', str(inner), 'display-popup', '-c', client,
                                          '-w', '48', '-h', '8', '-E', 'printf "Miami popup"; sleep 2'],
                                         env=env, cwd=base, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
                try:
                    wait(lambda s: 'Miami popup' in s and has_colour(s, p['accent']), 'popup')
                finally:
                    tm(outer, 'send-keys', '-t', 'viewer:0.0', 'Escape')
                    popup.wait(timeout=5)
            css = '''body{margin:0;padding:14px;display:grid;gap:14px;background:transparent}
section{border-radius:8px;overflow:hidden;padding:16px 20px}
header{font:600 15px system-ui;margin-bottom:12px}
pre{font:15px/18px 'DejaVu Sans Mono',monospace;margin:0;white-space:pre;font-variant-ligatures:none}
.terminal-cell{display:inline-block;width:9px;height:18px;vertical-align:top;text-align:center}'''
            output.write_text('<!doctype html><meta charset="utf-8"><style>' + css + '</style>' + ''.join(sections))
        finally:
            tm(outer, 'kill-server', check=False)
            tm(inner, 'kill-server', check=False)
    print('Verified tmux: both palettes, RGB attached-client captures, selection/messages/menus/popups, repeated sourcing, switching and preservation of formats, attributes, local overrides, bindings and unrelated options.', file=sys.stderr)


if __name__ == '__main__':
    capture(Path(sys.argv[1]))
