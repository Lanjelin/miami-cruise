"""Verify/capture real lazygit UI states in an isolated tmux server.

Needs lazygit 0.66.3, tmux, and compatible bat/delta for the integration capture.
Set LAZYGIT, BAT and DELTA to executable paths. No config or repository outside
the scratch directory is modified. Native Git ANSI colours use the matching
Miami Cruise terminal palette; all explicit UI RGB comes from lazygit itself.
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
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "previews"))
from _terminal import ansi_html

WIDTH, HEIGHT = 120, 34


def run(args, env, cwd, check=True):
    return subprocess.run(args, env=env, cwd=cwd, capture_output=True, text=True, check=check).stdout


def capture(output):
    paths = {name: shutil.which(os.environ.get(name.upper(), name)) for name in ('lazygit', 'bat', 'delta')}
    paths['bat'] = paths['bat'] or shutil.which('batcat')
    if not all(paths.values()) or not shutil.which('tmux'):
        raise SystemExit('Needs lazygit, bat, delta and tmux; set LAZYGIT, BAT and DELTA if necessary.')
    tokens = json.loads((ROOT / 'dist/tokens/tokens.json').read_text())
    with tempfile.TemporaryDirectory(prefix='miami-lazygit-') as tmp:
        base = Path(tmp)
        repo = base / 'night-drive'
        repo.mkdir()
        env = {k: v for k, v in os.environ.items()
               if not k.startswith(('GIT_', 'BAT_', 'DELTA_', 'LG_', 'TMUX')) and
               k not in ('NO_COLOR', 'CONFIG_DIR')}
        env.update(GIT_CONFIG_NOSYSTEM='1', GIT_CONFIG_GLOBAL=os.devnull,
                   TERM='tmux-256color', COLORTERM='truecolor', LC_ALL='C.UTF-8', TZ='UTC',
                   XDG_CONFIG_HOME=str(base / 'config'), XDG_CACHE_HOME=str(base / 'cache'),
                   XDG_STATE_HOME=str(base / 'state'),
                   GIT_AUTHOR_DATE='2025-01-01T12:00:00Z', GIT_COMMITTER_DATE='2025-01-01T12:00:00Z')

        def git(*args):
            return run(['git', *args], env, repo)

        git('init', '-b', 'main')
        for key, value in [('user.name', 'Miami Cruise'), ('user.email', 'preview@example.invalid'),
                           ('commit.gpgsign', 'false'), ('core.hooksPath', os.devnull)]:
            git('config', key, value)
        sample = (ROOT / 'previews/lazygit/sample.py').read_text()
        (repo / 'cruise.py').write_text(sample.replace('Miami Beach', 'Ocean Drive').replace('88.0', '55.0'))
        (repo / 'README.md').write_text('# Miami Cruise\n\nNight drive.\n')
        (repo / 'old.txt').write_text('Old route\n')
        git('add', '.')
        git('commit', '-m', 'feat: start the night drive')
        git('branch', 'feat/daylight')
        (repo / 'cruise.py').write_text(sample)
        (repo / 'README.md').write_text('# Miami Cruise\n\nDark and light, one palette.\n')
        git('add', 'README.md')
        (repo / 'old.txt').unlink()
        (repo / 'notes.txt').write_text('Next stop: Miami\n')
        preview = base / 'preview.yml'
        preview.write_text('gui:\n  showRandomTip: false\n  showCommandLog: false\n'
                           '  showFileTree: false\n  showBottomLine: false\n  showListFooter: false\n'
                           'update:\n  method: never\ngit:\n  autoFetch: false\n'
                           '  autoRefresh: false\ndisableStartupPopups: true\n')
        # Build an isolated standard bat cache; delta ignores BAT_CACHE_PATH.
        bat_config = base / 'bat'
        (bat_config / 'themes').mkdir(parents=True)
        for path in (ROOT / 'dist/delta').glob('*.tmTheme'):
            shutil.copyfile(path, bat_config / 'themes' / path.name)
        env['BAT_CONFIG_DIR'] = str(bat_config)
        run([paths['bat'], 'cache', '--build'], env, base)
        delta_config = base / 'delta.gitconfig'
        delta_config.write_text('[include]\n  path = ' + str(ROOT / 'dist/delta/miami-cruise.gitconfig') + '\n')
        calls = base / 'delta-calls.jsonl'
        wrapper = base / 'delta-wrapper'
        wrapper.write_text('#!/usr/bin/env python3\nimport json,os,sys\n'
                           f'with open({str(calls)!r}, "a") as f: f.write(json.dumps(sys.argv[1:])+"\\n")\n'
                           f'os.execv({paths["delta"]!r}, [{paths["delta"]!r}]+sys.argv[1:])\n')
        wrapper.chmod(0o755)
        delta_layer = base / 'delta.yml'
        command = (shlex.quote(str(wrapper)) + ' --config ' + shlex.quote(str(delta_config)) +
                   ' --features=miami-cruise-{{colorScheme}} --{{colorScheme}} --paging=never --true-color=always')
        delta_layer.write_text('git:\n  diffRenderers:\n    - colorArg: never\n      command: ' + json.dumps(command) + '\n')
        socket = base / 'tmux.sock'

        def tmux(*args, check=True):
            return run(['tmux', '-S', str(socket), *args], env, base, check)

        def screen():
            return tmux('capture-pane', '-p', '-e', '-N', '-t', 'preview:0.0')

        def plain(value):
            return re.sub(r'\x1b\[[0-9;]*m', '', value)

        def wait_for(predicate, label):
            deadline = time.monotonic() + 12
            last = ''
            while time.monotonic() < deadline:
                last = screen()
                if predicate(last):
                    return last
                time.sleep(.08)
            raise RuntimeError(f'Timed out waiting for {label}:\n{plain(last)}')

        def key(value):
            tmux('send-keys', '-t', 'preview:0.0', value)

        def stable_screen():
            previous, repeats = '', 0
            deadline = time.monotonic() + 4
            while time.monotonic() < deadline:
                current = screen()
                repeats = repeats + 1 if current == previous else 0
                if repeats >= 2:
                    return current
                previous = current
                time.sleep(.1)
            return previous

        def rgb(value):
            return ';'.join(str(int(value[i:i+2], 16)) for i in (1, 3, 5))

        captures = {'palette': [], 'delta': []}
        try:
            for integration in (False, True):
                for variant, p in tokens.items():
                    # Also exercise both branches of the auto file with explicit selection.
                    force = base / 'scheme.yml'
                    force.write_text('gui:\n  colorScheme: ' + variant + '\n')
                    layers = [preview, ROOT / 'dist/lazygit/miami-cruise.yml', force]
                    if integration:
                        layers.append(delta_layer)
                    args = [paths['lazygit'], '--use-config-dir', str(base / ('state-' + variant)),
                            '--use-config-file', ','.join(map(str, layers))]
                    tmux('-f', os.devnull, 'new-session', '-d', '-s', 'preview', '-x', str(WIDTH),
                         '-y', str(HEIGHT), '-c', str(repo), shlex.join(args))
                    tmux('set-option', '-g', 'status', 'off')
                    wait_for(lambda s: 'README.md' in s and '38;2;' + rgb(p['accent']) in s, 'loaded theme')
                    key('j')
                    shot = wait_for(lambda s: 'Ocean Drive' in plain(s) and 'Miami Beach' in plain(s), 'file diff')
                    shot = stable_screen()
                    assert '48;2;' + rgb(p['hover']) in shot, 'Selected-line background missing'
                    if not integration:
                        key('/')
                        tmux('send-keys', '-t', 'preview:0.0', '-l', '--', 'cruise')
                        key('Enter')
                        wait_for(lambda s: '38;2;' + rgb(p['info']) in s, 'search border')
                        # Real staging/unstaging in the disposable repository only.
                        key('Space')
                        wait_for(lambda s: 'cruise.py' in git('diff', '--cached', '--name-only'), 'stage file')
                        key('Space')
                        wait_for(lambda s: 'cruise.py' not in git('diff', '--cached', '--name-only'), 'unstage file')
                        key('Escape')
                        key('3')
                        wait_for(lambda s: 'feat/daylight' in s and 'main' in s, 'branches')
                        key('4')
                        wait_for(lambda s: 'feat: start the night drive' in plain(s), 'commits')
                        key('2')
                        wait_for(lambda s: 'Ocean Drive' in plain(s) and 'Miami Beach' in plain(s), 'return to files')
                    else:
                        assert calls.exists()
                        recorded = calls.read_text()
                        assert f'--features=miami-cruise-{variant}' in recorded
                        assert '38;2;' + rgb(p['success']) in shot, 'Delta syntax missing'
                    captures['delta' if integration else 'palette'].append((variant, p, shot))
                    # Test the fixed file in the same app too, without the auto file.
                    tmux('kill-server')
                    if not integration:
                        existing = base / 'existing-theme.yml'
                        existing.write_text('gui:\n  ' + variant + 'Theme:\n    activeBorderColor: ' +
                                            json.dumps([p['info']]) + '\n')
                        fixed_args = [paths['lazygit'], '--use-config-dir', str(base / ('fixed-' + variant)),
                                      '--use-config-file', ','.join(map(str, [preview, existing, ROOT / f'dist/lazygit/miami-cruise-{variant}.yml']))]
                        tmux('-f', os.devnull, 'new-session', '-d', '-s', 'preview', '-x', str(WIDTH),
                             '-y', str(HEIGHT), '-c', str(repo), shlex.join(fixed_args))
                        tmux('set-option', '-g', 'status', 'off')
                        wait_for(lambda s: 'README.md' in s and '38;2;' + rgb(p['accent']) in s, 'fixed theme')
                        tmux('kill-server')
            for name, frames in captures.items():
                sections = []
                for variant, p, shot in frames:
                    label = ' · delta renderer' if name == 'delta' else ' · native Git diff'
                    sections.append(f'<section style="background:{p["bg"]};color:{p["text"]}">'
                                    f'<header style="color:{p["accent"]}">Miami Cruise · lazygit · {variant}{label}</header>'
                                    f'<pre>{ansi_html(shot, p)}</pre></section>')
                (output / f'{name}.html').write_text('<!doctype html><meta charset="utf-8"><style>' + CSS + '</style>' + ''.join(sections))
        finally:
            tmux('kill-server', check=False)
    print('Verified lazygit: dark/light auto-file branches and fixed themes; search, stage/unstage, branches, commits and delta renderer.', file=sys.stderr)


CSS = '''body{margin:0;padding:14px;display:grid;gap:14px;background:transparent}
section{border-radius:8px;overflow:hidden;padding:16px 20px}
header{font:600 15px system-ui;margin-bottom:12px}
pre{font:15px/1.25 'DejaVu Sans Mono',monospace;margin:0;white-space:pre}'''

if __name__ == '__main__':
    capture(Path(sys.argv[1]))
