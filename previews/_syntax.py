"""Real bat/delta captures in isolated config/cache directories; no personal config.

Run: BAT=/path/to/bat DELTA=/path/to/delta python3 -I previews/_syntax.py bat|delta out.html
Only the terminal's default foreground/background are supplied by HTML; app colours
are converted from actual ANSI output. Unhandled escape sequences fail loudly.
"""
import difflib
import html
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def ansi_html(text):
    # Delta erases to the right margin using the current background colour.
    # Expand just that known operation into spaces before interpreting SGR.
    lines = []
    for line in text.split('\n'):
        while '\x1b[0K' in line:
            before, after = line.split('\x1b[0K', 1)
            width = len(re.sub(r'\x1b\[[0-9;]*m', '', before))
            line = before + ' ' * max(0, 110 - width) + after
        lines.append(line)
    text = '\n'.join(lines)
    out, style, start = [], {}, 0
    for match in re.finditer(r"\x1b\[([0-9;]*)m", text):
        out.append('<span style="' + ';'.join(f'{k}:{v}' for k, v in style.items()) + '">' +
                   html.escape(text[start:match.start()]) + '</span>')
        codes = [int(n) for n in match[1].split(';') if n] or [0]
        i = 0
        while i < len(codes):
            c = codes[i]
            if c == 0:
                style = {}
            elif c in (1, 2, 3, 4, 9):
                key, value = {1: ('font-weight', 'bold'), 2: ('opacity', '.65'),
                              3: ('font-style', 'italic'), 4: ('text-decoration', 'underline'),
                              9: ('text-decoration', 'line-through')}[c]
                style[key] = value
            elif c in (22, 23, 24, 29, 39, 49):
                for key in {22: ['font-weight', 'opacity'], 23: ['font-style'],
                            24: ['text-decoration'], 29: ['text-decoration'],
                            39: ['color'], 49: ['background']}[c]:
                    style.pop(key, None)
            elif c in (38, 48) and codes[i + 1] == 2:
                style['color' if c == 38 else 'background'] = 'rgb(' + ','.join(map(str, codes[i + 2:i + 5])) + ')'
                i += 4
            else:
                raise ValueError(f'Unexpected SGR: {codes}')
            i += 1
        start = match.end()
    out.append(html.escape(text[start:]))
    result = ''.join(out)
    if '\x1b' in result:
        raise ValueError('Unconverted terminal escape')
    return result


def run(args, env, cwd, text=None):
    result = subprocess.run(args, input=text, cwd=cwd, env=env,
                            capture_output=True, text=True, check=True)
    if result.stderr:
        raise RuntimeError(result.stderr)
    return result.stdout


def capture(app):
    bat = shutil.which(os.environ.get('BAT', 'bat')) or shutil.which('batcat')
    delta = shutil.which(os.environ.get('DELTA', 'delta'))
    if not bat or (app == 'delta' and not delta):
        raise SystemExit('This preview requires bat (BAT=...) and, for delta, delta (DELTA=...).')
    palettes = json.loads((ROOT / 'dist/tokens/tokens.json').read_text())
    with tempfile.TemporaryDirectory(prefix='miami-syntax-preview-') as tmp:
        base = Path(tmp)
        config = base / 'bat'
        (config / 'themes').mkdir(parents=True)
        for path in (ROOT / 'dist/bat').glob('*.tmTheme'):
            shutil.copyfile(path, config / 'themes' / path.name)
        env = {k: v for k, v in os.environ.items()
               if not k.startswith(('BAT_', 'DELTA_', 'GIT_')) and k != 'NO_COLOR'}
        env.update(BAT_CONFIG_DIR=str(config), XDG_CACHE_HOME=str(base / 'cache'),
                   GIT_CONFIG_NOSYSTEM='1', GIT_CONFIG_GLOBAL=os.devnull,
                   COLORTERM='truecolor', TERM='xterm-256color', LC_ALL='C.UTF-8')
        # bat cache --build reports normal progress on stderr.
        subprocess.run([bat, 'cache', '--build'], env=env, cwd=base,
                       capture_output=True, text=True, check=True)
        executable = bat if app == 'bat' else delta
        version = run([executable, '--version'], env, base).strip()
        if app == 'delta':
            available = run([delta, '--no-gitconfig', '--list-syntax-themes'], env, base)
            assert all(f'miami-cruise-{v}' in available for v in palettes), available
        sections = []
        for variant, p in palettes.items():
            theme = f'miami-cruise-{variant}'
            if app == 'bat':
                output = run([bat, '--theme', theme, '--color=always', '--paging=never',
                              '--style=numbers', '--terminal-width=110',
                              str(ROOT / 'previews/bat/sample.py')], env, base)
                # Exercise other bundled syntax definitions with the same installed theme.
                examples = {
                    'js': ('// cruise\nconst speed = 88;\nfunction depart() { return "Miami"; }\n', ['accent', 'success', 'orange']),
                    'rs': ('// cruise\nfn main() { let speed = 88; println!("Miami"); }\n', ['accent', 'success', 'orange']),
                    'json': ('{"destination": "Miami", "speed": 88}\n', ['success', 'orange']),
                    'md': ('# Miami Cruise\n\n**Night drive** with `cruise` and a [guide](https://example.invalid).\n', ['accent', 'success']),
                }
                for extension, (sample, expected) in examples.items():
                    rendered = run([bat, '--theme', theme, '--color=always', '--paging=never',
                                    '--style=plain', '--language', extension], env, base, sample)
                    for token in expected:
                        rgb_sample = ';'.join(str(int(p[token][i:i+2], 16)) for i in (1, 3, 5))
                        assert f'38;2;{rgb_sample}' in rendered, (variant, extension, token)
            else:
                before = (ROOT / 'previews/delta/before.py').read_text().splitlines(True)
                after = (ROOT / 'previews/delta/after.py').read_text().splitlines(True)
                diff = 'diff --git a/cruise.py b/cruise.py\n' + ''.join(difflib.unified_diff(before, after, 'a/cruise.py', 'b/cruise.py'))
                args = [delta, '--config', str(ROOT / 'dist/delta/miami-cruise.gitconfig'),
                        '--features', theme, '--paging=never', '--true-color=always',
                        '--width=110', '--line-numbers']
                output = run(args, env, base, diff)
                # Exercise side-by-side without changing the theme's layout preferences.
                side = run(args + ['--side-by-side'], env, base, diff)
                assert 'Miami Beach' in re.sub(r'\x1b\[[0-9;]*m', '', side)
            assert 'Cruise' in output
            rgb = lambda value: ';'.join(str(int(value[i:i+2], 16)) for i in (1, 3, 5))
            for token in ('accent', 'success', 'orange'):
                assert f'38;2;{rgb(p[token])}' in output, (app, variant, token)
            if app == 'delta':
                assert f'38;2;{rgb(p["danger"])}' in output
                emphasis_bg = p['panel'] if variant == 'dark' else p['bg']
                assert f'48;2;{rgb(emphasis_bg)}' in output
            sections.append(f'<section style="background:{p["bg"]};color:{p["text"]}">'
                            f'<header style="color:{p["accent"]}">Miami Cruise · {app} · {variant}</header>'
                            f'<pre>{ansi_html(output)}</pre></section>')
        print(f'Verified {version}: dark/light loading and exact RGB; ' +
              ('unified + side-by-side diff' if app == 'delta' else 'Python, JS, Rust, JSON and Markdown'), file=sys.stderr)
        return '<!doctype html><meta charset="utf-8"><style>' + CSS + '</style>' + ''.join(sections)


CSS = '''body{margin:0;padding:14px;display:grid;gap:14px;background:transparent}
section{border-radius:8px;overflow:hidden;padding:16px 24px}
header{font:600 15px system-ui;margin-bottom:12px}
pre{font:16px/1.5 'DejaVu Sans Mono',monospace;margin:0;white-space:pre}'''

if __name__ == '__main__':
    Path(sys.argv[2]).write_text(capture(sys.argv[1]))
