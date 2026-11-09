"""Capture actual Glow stdout with native JSON styles; never mock Markdown HTML."""
import json
import os
from pathlib import Path
import pty
import re
import select
import shutil
import subprocess
import sys
import tempfile
import time
import unicodedata

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / 'previews')]
from _terminal import ansi_html


def capture(output):
    glow = shutil.which(os.environ.get('GLOW', 'glow'))
    if not glow:
        raise SystemExit('Preview needs Glow 3.0.0; set GLOW=/path/to/glow.')
    palettes = json.loads((ROOT / 'dist/tokens/tokens.json').read_text())
    sample = (ROOT / 'previews/glow/sample.md').read_text()
    extended = '''
### Heading three
#### Heading four
##### Heading five
###### Heading six

![A small image](https://example.com/image.png)

Palette
: A definition of our colours.

```json
{"ready": true, "count": 42, "route": "Miami\\nCruise"}
```

```python
# Chroma's JSON lexer keeps a whole string as one token; Python splits
# out the escape sequence, so exercise that token here instead.
greeting = "Miami\\nCruise"
```

```text
Plain code remains readable.
```

```unknownlanguage
Unknown language stays readable too.
```
'''
    with tempfile.TemporaryDirectory(prefix='miami-glow-') as tmp:
        base = Path(tmp)
        env = {k: v for k, v in os.environ.items()
               if not k.startswith(('GLOW_', 'GLAMOUR_', 'TMUX'))
               and k not in ('NO_COLOR', 'CLICOLOR', 'CLICOLOR_FORCE', 'FORCE_COLOR')}
        env.update(TERM='xterm-256color', COLORTERM='truecolor', CLICOLOR_FORCE='1', FORCE_COLOR='1',
                   LC_ALL='C.UTF-8', XDG_CONFIG_HOME=str(base / 'config'), XDG_CACHE_HOME=str(base / 'cache'),
                   GLOW_CONFIG_HOME=str(base / 'config/glow'))
        fixture = base / 'sample with spaces.md'
        fixture.write_text(sample)
        conf = base / 'config/glow/glow.yml'
        conf.parent.mkdir(parents=True)

        def render(*args, stdin=None):
            # A file-arg render needs a closed/non-pty stdin; an inherited pipe
            # makes Glow 3.0.0 print nothing instead of the rendered Markdown.
            kwargs = dict(input=stdin) if stdin is not None else dict(stdin=subprocess.DEVNULL)
            result = subprocess.run([glow, *args], env=env, cwd=base,
                                  text=True, capture_output=True, timeout=20, **kwargs)
            if result.returncode:
                raise RuntimeError(result.stderr)
            return result.stdout

        def terminal_render(*args):
            # Glow 3.0.0 deliberately substitutes its notty style for config-only
            # selection when stdout is a pipe. Verify config loading in a PTY.
            master, slave = pty.openpty()
            proc = None
            try:
                proc = subprocess.Popen([glow, *args], env=env, cwd=base,
                                        stdin=subprocess.DEVNULL, stdout=slave, stderr=subprocess.PIPE)
                os.close(slave)
                slave = None
                chunks = []
                deadline = time.monotonic() + 20
                while time.monotonic() < deadline:
                    if select.select([master], [], [], .1)[0]:
                        try:
                            data = os.read(master, 65536)
                        except OSError as err:
                            if err.errno != 5:
                                raise
                            break
                        if not data:
                            break
                        chunks.append(data)
                else:
                    raise TimeoutError('Glow terminal render timed out')
                assert proc.wait(timeout=5) == 0, proc.stderr.read().decode()
                return b''.join(chunks).decode().replace('\r\n', '\n')
            finally:
                os.close(master)
                if slave is not None:
                    os.close(slave)
                if proc is not None and proc.poll() is None:
                    proc.kill()
                    proc.wait()

        def plain(s):
            # Glow emits OSC 8 terminal hyperlinks around link text; keep the text.
            s = re.sub(r'\x1b\]8;[^\x1b\x07]*(?:\x1b\\|\x07)', '', s)
            s = re.sub(r'\x1b\[[0-9;]*m', '', s)
            assert '\x1b' not in s, 'Unexpected terminal control code'
            return s

        def rgb(h):
            return ';'.join(str(int(h[i:i + 2], 16)) for i in (1, 3, 5))

        def colours(s, p, tokens):
            for token in tokens:
                # Glow combines SGR attributes in one sequence; RGB may follow a semicolon.
                assert re.search(r'\x1b\[[0-9;]*38;2;' + rgb(p[token]) + r'(?:;|m)', s), (token, repr(s[:500]))

        def syntax_colours(s, p, tokens):
            # Glamour 2.0.1 explicitly uses Chroma's terminal256 formatter.
            levels = (0, 95, 135, 175, 215, 255)
            candidates = {16 + r*36 + g*6 + b: (rv, gv, bv)
                          for r, rv in enumerate(levels) for g, gv in enumerate(levels)
                          for b, bv in enumerate(levels)}
            candidates.update({232 + i: (8 + i*10,) * 3 for i in range(24)})
            for token in tokens:
                rgb_value = tuple(int(p[token][i:i+2], 16) for i in (1, 3, 5))
                index = min(candidates, key=lambda n: sum((a-b)**2 for a,b in zip(rgb_value,candidates[n])))
                assert f'38;5;{index}m' in s, (token, index)

        sections = []
        for variant, p in palettes.items():
            theme = ROOT / f'dist/glow/miami-cruise-{variant}.json'
            # Native config loading, width/pager preservation and CLI override.
            conf.write_text('style: ' + json.dumps(str(theme)) + '\nwidth: 56\npager: false\nmouse: true\n')
            config_before = conf.read_bytes()
            shot = render('-s', str(theme), '-w', '56', str(fixture))
            via_stdin = render('-s', str(theme), '-w', '56', '-', stdin=sample)
            assert shot == via_stdin
            tty_shot = terminal_render(str(fixture))
            colours(tty_shot, p, ('accent', 'text'))
            assert conf.read_bytes() == config_before
            colours(shot, p, ('text', 'accent', 'info', 'muted'))
            syntax_colours(shot, p, ('disabled', 'accent', 'orange', 'success', 'danger'))
            assert '48;2;' + rgb(p['accent']) in shot
            assert '48;2;' + rgb(p['bg']) in shot
            assert '48;2;' + rgb(p['panel']) in shot
            text = plain(shot)
            for expected in ('Miami Cruise', 'Ready to sail', '│', '[✓]', '[ ]', 'Element', 'Purpose',
                             'def', 'cruise', '42', 'return', 'theme =', '--------'):
                assert expected in text, expected
            assert re.search(r'\x1b\[[0-9;]*;?3(?:;|m)', shot), 'Italics missing'
            extra = render('-s', str(theme), '-', stdin=extended)
            for expected in ('Heading three', 'Heading six', 'A small image', 'A definition',
                             'Plain code remains readable', 'Unknown language stays readable'):
                assert expected in plain(extra), expected
            syntax_colours(extra, p, ('success', 'orange', 'warning'))
            # A supplied style must override an opposite-variant config style.
            other = 'light' if variant == 'dark' else 'dark'
            override = render('-s', str(ROOT / f'dist/glow/miami-cruise-{other}.json'), str(fixture))
            colours(override, palettes[other], ('accent', 'text'))
            narrow = plain(render('-s', str(theme), '-w', '40', str(fixture)))
            assert max(sum(0 if unicodedata.combining(c) else 2 if unicodedata.east_asian_width(c) in 'WF' else 1
                           for c in line) for line in narrow.splitlines()) <= 40, 'Width override ignored'
            # OSC 8 wraps the rendered link text; ansi_html only parses SGR colour codes.
            shot_html = re.sub(r'\x1b\]8;[^\x1b\x07]*(?:\x1b\\|\x07)', '', shot)
            sections.append(f'<section style="background:{p["bg"]};color:{p["text"]}">'
                            f'<header style="color:{p["accent"]}">Miami Cruise · Glow · {variant}</header>'
                            f'<pre>{ansi_html(shot_html, p, fixed_cells=True)}</pre></section>')
        css = '''body{margin:0;padding:14px;display:grid;grid-template-columns:1fr 1fr;gap:14px;background:transparent}
section{border-radius:8px;overflow:hidden;padding:16px 20px}
header{font:600 15px system-ui;margin-bottom:12px}
pre{font:15px/18px 'DejaVu Sans Mono',monospace;margin:0;white-space:pre;font-variant-ligatures:none}
.terminal-cell{display:inline-block;width:9px;height:18px;vertical-align:top;text-align:center}'''
        output.write_text('<!doctype html><meta charset="utf-8"><style>' + css + '</style>' + ''.join(sections))
    print('Verified Glow 3.0.0: RGB Markdown and 256-colour code, Markdown structures, Python/JSON/diff/plain syntax, file/stdin equivalence, config preservation, CLI style precedence and width control.', file=sys.stderr)


if __name__ == '__main__':
    capture(Path(sys.argv[1]))
