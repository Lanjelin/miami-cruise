"""HTML mock-up of a WezTerm window in both variants, drawn from the same code the exporter uses.
Usage: python3 -I previews/wezterm/mock.py out.html"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from themes import _hl  # noqa: E402

T = json.load(open(ROOT / "dist/tokens/tokens.json"))


def term(title, p):
    a = _hl.ansi(p)
    sel = _hl.mix(p["bg"], p["accent"], 0.20)
    sw = "".join(f'<i style="background:{c}"></i>' for c in a)
    return f"""<div class="w" style="--bg:{p['bg']};--panel:{p['panel']};--border:{p['border']};--hover:{p['hover']};--fg:{p['text']};--mut:{p['muted']};--acc:{p['accent']};--on:{p['on-accent']};--sel:{sel};--c1:{a[1]};--c2:{a[2]};--c3:{a[3]};--c4:{a[4]};--c5:{a[5]};--c6:{a[6]};--c0:{a[0]};--c7:{a[7]};--c8:{a[8]}">
<div class="tabs"><span class="t act">1: zsh</span><span class="t">2: nvim</span><span class="t">3: ssh</span><span class="plus">+</span><b class="title">{title}</b></div>
<pre><span class="c2">lars@host</span> <span class="c4">~/projects/miami-cruise</span> <span class="c3">(main)</span>
<span class="c5">$</span> ls -la
drwxr-xr-x  <span class="c6">themes</span>
drwxr-xr-x  <span class="c6">previews</span>
-rw-r--r--  build.py
-rw-r--r--  <span class="c1">README.md</span>
<span class="c5">$</span> git diff --stat
 build.py | 4 <span class="c2">++++</span><span class="c1">--</span>
<span class="c5">$</span> echo "selected <span class="sel">text</span> and a <span class="c8">dim comment</span>"
selected <span class="sel">text</span> and a <span class="c8">dim comment</span>
<span class="c5">$</span> <span class="cur"> </span></pre>
<div class="sw">{sw}</div></div>"""


css = """body{margin:0;display:flex;gap:14px;padding:14px;background:transparent;font:12.5px 'DejaVu Sans Mono',monospace}
.w{flex:1;min-width:0;background:var(--bg);color:var(--fg);border-radius:8px;overflow:hidden}
.tabs{display:flex;align-items:center;background:var(--panel);font-family:system-ui,sans-serif;font-size:12px}
.t{padding:7px 14px;color:var(--mut)}.t.act{background:var(--bg);color:var(--acc);font-weight:700}
.plus{padding:7px 12px;color:var(--mut)}.title{margin-left:auto;padding:0 12px;color:var(--mut);font-weight:500}
pre{margin:0;padding:12px 14px;line-height:1.5;min-height:215px}
.c1{color:var(--c1)}.c2{color:var(--c2)}.c3{color:var(--c3)}.c4{color:var(--c4)}.c5{color:var(--c5)}.c6{color:var(--c6)}.c8{color:var(--c8)}
.sel{background:var(--sel);color:var(--fg)}.cur{background:var(--acc);color:var(--on)}
.sw{display:flex;height:12px}.sw i{flex:1}"""
html = "<!doctype html><html><style>" + css + "</style>" + term("Miami Cruise", T["dark"]) + term("Miami Cruise Day", T["light"]) + "</html>"
Path(sys.argv[1] if len(sys.argv) > 1 else "/tmp/wez.html").write_text(html)
