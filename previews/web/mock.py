import json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
T=json.load(open(ROOT / 'dist/tokens/tokens.json'))
def panel(title,p,glow):
    v=';'.join(f'--{k}:{x}' for k,x in p.items())
    g='glow' if glow else 'flat'
    return f'''<div class="p {g}" style="{v}"><div class="top"><b>{title}</b><span class="btn">+ New</span></div>
<div class="body"><div class="side"><div class="i act">Projects</div><div class="i">Reports</div><div class="i">Settings</div></div><div class="main">
<table><tr><th>ID</th><th>Task</th><th>Status</th></tr>
<tr><td>#1042</td><td>Ship release notes</td><td style="color:var(--success)">Done</td></tr>
<tr class="sel"><td>#1043</td><td>Review pull request</td><td style="color:var(--info)">Active</td></tr>
<tr><td>#1044</td><td>Update dependencies</td><td style="color:var(--warning)">Waiting</td></tr>
<tr><td>#1045</td><td>Fix failing build</td><td style="color:var(--danger)">Overdue</td></tr>
<tr><td>#1046</td><td>Tune alert thresholds</td><td style="color:var(--orange)">Review</td></tr>
<tr><td>#1047</td><td>Security audit</td><td style="color:var(--orchid)">Blocked</td></tr></table>
<div class="tools"><span class="inp">Search…</span><span class="btn s">Export</span></div>
<div class="m">6 of 212 · <a>link</a> · <span style="color:var(--disabled)">disabled</span></div></div></div>
<div class="sw">{''.join(f'<i style="background:{p[k]}"></i>' for k in ['panel','bg','row','border','disabled','muted','text','accent','success','warning','orange','danger','orchid','info'])}</div></div>'''
css='''body{margin:0;display:flex;gap:14px;padding:14px;background:transparent;font:12px system-ui,sans-serif}
.p{flex:1;min-width:0;background:var(--bg);color:var(--text);border-radius:8px;overflow:hidden}
.top{display:flex;justify-content:space-between;align-items:center;background:var(--panel);padding:9px 12px;border-bottom:1px solid var(--border)}
.btn{background:var(--accent);color:var(--on-accent);padding:4px 11px;border-radius:4px;font-weight:700}
.btn.s{background:none;border:1px solid var(--border);color:var(--text);font-weight:500}
.body{display:flex}.side{width:96px;background:var(--panel);padding:6px 0;min-height:215px}
.i{padding:7px 12px;color:var(--muted)}.i.act{color:var(--accent);background:color-mix(in oklab,var(--accent) 14%,transparent);box-shadow:inset 3px 0 0 var(--accent)}
.main{flex:1;padding:10px}table{width:100%;border-collapse:collapse}
th{text-align:left;color:var(--muted);padding:6px;background:var(--panel);border-bottom:1px solid var(--border)}
td{padding:6px}tr:nth-child(even) td{background:var(--row)}
tr.sel td{background:color-mix(in oklab,var(--accent) 16%,transparent)}tr.sel td:first-child{box-shadow:inset 3px 0 0 var(--accent)}
.tools{display:flex;gap:8px;margin-top:10px}.inp{flex:1;border:1px solid var(--focus);border-radius:4px;padding:4px 8px;color:var(--disabled)}
.m{margin-top:9px;color:var(--muted)}a{color:var(--accent);text-decoration:underline}.sw{display:flex;height:12px}.sw i{flex:1}
.glow{background:radial-gradient(120% 90% at 50% 0,color-mix(in oklab,var(--accent) 8%,var(--bg)),var(--bg) 55%);box-shadow:inset 0 0 90px rgba(0,0,0,.25)}
.glow.light{box-shadow:none}
.glow .btn:not(.s){box-shadow:0 0 14px color-mix(in oklab,var(--accent) 50%,transparent)}
.glow .i.act{box-shadow:inset 3px 0 0 var(--accent),inset 14px 0 18px -14px var(--accent)}
.glow tr.sel td{text-shadow:0 0 8px color-mix(in oklab,var(--accent) 45%,transparent)}
.glow .inp{box-shadow:0 0 0 3px color-mix(in oklab,var(--accent) 22%,transparent),0 0 12px color-mix(in oklab,var(--accent) 35%,transparent)}'''
h='<!doctype html><html><style>'+css+'</style>'+panel('Miami Cruise',T['dark'],True)+panel('Miami Cruise Day',T['light'],True).replace('class="p glow"','class="p glow light"')+panel('Dark · no glow',T['dark'],False)+'</html>'
open(sys.argv[1] if len(sys.argv) > 1 else '/tmp/mc.html','w').write(h)
