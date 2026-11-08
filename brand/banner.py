"""HTML for the README banner (dark and light) and the GitHub social-preview image, from the palette.
Usage: python3 -I brand/banner.py <banner-dark|banner-light|social> out.html"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
T = json.load(open(ROOT / "dist/tokens/tokens.json"))
LOGO = (ROOT / "dist/brand/logo.svg").read_text()
TAGLINE = "Teal-ink neutrals. One magenta hero."
SUB = "A dark and light colour scheme for your editor, terminal and web."
STRIP = ("bg", "panel", "border", "text", "accent", "success", "warning", "danger", "info", "orange", "orchid")


def strip(p, h):
    return '<div class="strip">' + "".join(f'<i style="background:{p[k]}"></i>' for k in STRIP) + "</div>"


def page(kind):
    mode = "light" if kind.endswith("light") else "dark"
    p = T[mode]
    social = kind == "social"
    w, h = (1280, 640) if social else (1280, 300)
    logo = f'<div class="logo">{LOGO}</div>'
    css = f"""*{{box-sizing:border-box;margin:0}}
html,body{{width:{w}px;height:{h}px;overflow:hidden}}
body{{font-family:'Inter','Segoe UI',system-ui,-apple-system,Roboto,'Helvetica Neue',Arial,sans-serif;color:{p['text']};
 background:{'radial-gradient(90% 120% at 50% -10%, color-mix(in oklab, ' + p['accent'] + ' 16%, ' + p['bg'] + '), ' + p['bg'] + ' 62%)' if social else 'transparent'}}}
.wrap{{height:100%;display:flex;flex-direction:column;justify-content:center;align-items:{'center' if social else 'flex-start'};
 padding:{'0 80px' if social else '0 56px'};gap:{22 if social else 0}px;text-align:{'center' if social else 'left'}}}
.row{{display:flex;align-items:center;gap:{40 if social else 32}px;flex-direction:{'column' if social else 'row'}}}
.logo svg{{width:{200 if social else 150}px;height:{200 if social else 150}px;display:block}}
h1{{font-size:{104 if social else 72}px;line-height:1.02;font-weight:800;letter-spacing:-.02em}}
h1 em{{font-style:normal;color:{p['accent']}}}
.tag{{font-size:{34 if social else 26}px;color:{p['muted']};margin-top:8px;font-weight:500}}
.sub{{font-size:{24 if social else 19}px;color:{p['disabled'] if False else p['muted']};margin-top:6px;opacity:.9}}
.strip{{display:flex;height:{14 if social else 10}px;width:{720 if social else 100}{'px' if social else '%'};border-radius:99px;overflow:hidden;
 box-shadow:0 0 0 1px {p['border']}}}
.strip i{{flex:1}}
.bottom{{position:absolute;left:0;right:0;bottom:0;padding:0 56px 28px}}"""
    if social:
        body = f'<div class="wrap"><div class="row">{logo}<div><h1>Miami <em>Cruise</em></h1><div class="tag">{TAGLINE}</div><div class="sub">{SUB}</div></div></div>{strip(p, 14)}</div>'
    else:
        body = (f'<div class="wrap"><div class="row">{logo}<div><h1>Miami <em>Cruise</em></h1><div class="tag">{TAGLINE}</div>'
                f'<div class="sub">{SUB}</div></div></div></div><div class="bottom">{strip(p, 10)}</div>')
    return f"<!doctype html><html><meta charset=utf-8><style>{css}</style><body>{body}</body></html>"


Path(sys.argv[2]).write_text(page(sys.argv[1]))
