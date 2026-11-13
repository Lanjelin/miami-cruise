"""Illustrative, offline OpenClaw UI fixture. No live sessions or host data.

Colours come from the native theme artifact. Layout is a generic illustration,
not a capture of OpenClaw components or proof of native browser rendering.
"""
import html
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
theme = json.loads((ROOT / 'dist/openclaw/miami-cruise.json').read_text())

CSS = '''
*{box-sizing:border-box}body{margin:0;padding:20px;display:flex;gap:20px;background:transparent;font:15px/1.55 system-ui,sans-serif}
.preview{width:1200px;height:780px;flex:none;overflow:hidden;border:1px solid var(--border);border-radius:14px;background:var(--background);color:var(--foreground)}
header{height:66px;display:flex;align-items:center;justify-content:space-between;padding:0 24px;border-bottom:1px solid var(--border);background:var(--card)}
.brand{font-size:19px;font-weight:750;letter-spacing:-.5px}.brand span{color:var(--primary);margin-right:9px}.quiet{color:var(--muted-foreground)}
.pill{border:1px solid var(--border);background:var(--secondary);color:var(--secondary-foreground);border-radius:20px;padding:5px 12px;font-size:12px}
.layout{display:flex;height:676px}aside{width:232px;flex:none;padding:22px 14px;background:var(--card);border-right:1px solid var(--border)}
button{font:inherit;cursor:default;border:1px solid var(--border);background:var(--secondary);color:var(--secondary-foreground);border-radius:8px;padding:9px 14px}
.new{font-size:13px;white-space:nowrap;width:100%;background:var(--primary);color:var(--primary-foreground);border-color:var(--primary);font-weight:650;text-align:left}
.label{font-size:11px;letter-spacing:1.4px;font-weight:650;color:var(--muted-foreground);margin:30px 12px 10px}
.item{padding:10px 12px;border-radius:7px;margin:3px 0;font-size:14px;color:var(--muted-foreground)}
.item.active{background:var(--secondary);color:var(--foreground);box-shadow:inset 3px 0 var(--primary)}
.dot{display:inline-block;width:7px;height:7px;background:var(--primary);border-radius:50%;margin-right:9px}
main{flex:1;min-width:0;display:flex;flex-direction:column}.toolbar{height:62px;border-bottom:1px solid var(--border);display:flex;align-items:center;justify-content:space-between;padding:0 28px}
.toolbar b{font-size:14px}.content{padding:27px 40px 0;flex:1}.who{font-size:12px;font-weight:700;margin-bottom:9px;display:flex;gap:9px;align-items:center}.avatar{width:24px;height:24px;display:grid;place-items:center;border-radius:7px;background:var(--secondary);color:var(--secondary-foreground);font-size:11px}
.user{margin-left:120px;margin-bottom:25px}.bubble{background:var(--secondary);color:var(--secondary-foreground);border:1px solid var(--border);border-radius:10px;padding:12px 17px;font-size:14px}
.assistant .avatar{background:var(--primary);color:var(--primary-foreground)}p{margin:8px 0 16px}.answer{padding-left:33px;font-size:14px}
.task{background:var(--card);color:var(--card-foreground);border:1px solid var(--border);border-radius:10px;padding:14px 18px;margin:15px 0}
.task strong{font-size:13px}.row{display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid var(--border);font-size:13px}.row:last-child{border:0;padding-bottom:0}
.state{color:var(--muted-foreground);font-size:12px}.link{color:var(--primary);text-decoration:underline;text-underline-offset:3px}
.composer{margin:0 28px 20px;border:1px solid var(--input);border-radius:12px;background:var(--card);padding:14px 16px}.placeholder{color:var(--muted-foreground);font-size:14px}.controls{display:flex;justify-content:space-between;align-items:center;margin-top:16px}.send{background:var(--primary);color:var(--primary-foreground);border:0;padding:5px 13px;font-weight:700}.hint{font-size:11px;color:var(--muted-foreground)}
footer{height:38px;border-top:1px solid var(--border);color:var(--muted-foreground);font-size:11px;display:flex;align-items:center;justify-content:space-between;padding:0 20px}
'''


def panel(mode):
    variables = ';'.join(f'--{key}:{value}' for key, value in theme[mode].items())
    return f'''<section class="preview" style="{html.escape(variables)}" aria-label="{mode} illustrative OpenClaw preview">
<header><div class="brand"><span>✳</span>OpenClaw</div><div class="pill">Miami Cruise · {mode.title()}</div></header>
<div class="layout"><aside><button class="new">+ &nbsp; New conversation</button>
<div class="label">CONVERSATIONS</div><div class="item active"><span class="dot"></span>Plan a release</div><div class="item">Explore the palette</div><div class="item">Weekend reading</div>
<div class="label">WORKSPACE</div><div class="item">◇ &nbsp; Dashboard</div><div class="item">◷ &nbsp; Automations</div><div class="item">⚙ &nbsp; Settings</div></aside>
<main><div class="toolbar"><b>Plan a release</b><span class="quiet">⋯</span></div>
<div class="content"><div class="user"><div class="who"><span class="avatar">Y</span>You</div><div class="bubble">Help me get the next release ready. What should we check?</div></div>
<div class="assistant"><div class="who"><span class="avatar">✳</span>Assistant</div><div class="answer"><p>Here’s a short checklist for a smooth release.</p>
<div class="task"><strong>Release checklist</strong><div class="row"><span>Review the changelog</span><span class="state">Complete</span></div><div class="row"><span>Check dark and light palettes</span><span class="state">Complete</span></div><div class="row"><span>Preview the installation guide</span><span class="state">Ready for review</span></div></div>
<p>The theme includes both modes in one file. You can switch between them in <span class="link">Settings → Appearance</span>.</p><span class="hint">Example response · synthetic content</span>
</div></div></div>
<div class="composer"><div class="placeholder">Message your assistant…</div><div class="controls"><span class="hint">+ &nbsp; Attach files</span><button class="send">↑</button></div></div>
</main></div><footer><span>Illustrative OpenClaw UI · not a live-session capture</span><span>Miami Cruise / {mode}</span></footer></section>'''


output = '<!doctype html><html lang="en"><meta charset="utf-8"><title>Miami Cruise · illustrative OpenClaw preview</title><style>' + CSS + '</style><body>' + ''.join(panel(mode) for mode in ('dark', 'light')) + '</body></html>'
Path(sys.argv[1]).write_text(output)
