"""Brand exporter: the logo and mark as standalone SVGs, rendered from brand/ templates.

Output: dist/brand/logo.svg, mark.svg, and palette-dark.svg / palette-light.svg (the README palette graphics). The logo and mark sit on their own dark tile, so one
file works on any background. The website and the README both use these files; the animated hero scene
is website-only and reuses brand_values()/fill() from here.
"""
import html
import re
from pathlib import Path

from palette import TOKEN_ORDER

from . import _hl

BRAND = Path(__file__).resolve().parent.parent / "brand"


def fill(tpl, values):
    return re.sub(r"\{\{(\w+)\}\}", lambda m: values[m.group(1)], tpl)


def brand_values(p):
    v = dict(p)
    v["ground"] = _hl.mix(p["panel"], "#000000", 0.5)
    v["sky"] = _hl.mix(p["panel"], p["accent"], 0.14)
    v["roof"] = _hl.mix(p["panel"], p["border"], 0.5)
    v["glass"] = _hl.mix(p["panel"], "#000000", 0.6)
    v["body"] = p["border"]
    v["car"] = fill((BRAND / "car.svg.part").read_text(), v)
    return v


def palette_svg(name, p):
    """Swatch grid of every token; background and text colours come from the palette itself."""
    cols, cw, ch, gap, pad = 6, 134, 112, 12, 28
    rows = -(-len(TOKEN_ORDER) // cols)
    w = pad * 2 + cols * cw + (cols - 1) * gap
    top = 78
    h = top + rows * ch + (rows - 1) * gap + pad
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="Miami Cruise {name} palette">',
        f'<rect width="{w}" height="{h}" rx="18" fill="{p["bg"]}"/>',
        f'<text x="{pad}" y="48" font-family="system-ui,-apple-system,Segoe UI,Roboto,sans-serif" font-size="26" font-weight="700" fill="{p["text"]}">'
        f'Miami <tspan fill="{p["accent"]}">Cruise</tspan> <tspan font-weight="500" fill="{p["muted"]}" font-size="20">{name}</tspan></text>',
    ]
    for i, tok in enumerate(TOKEN_ORDER):
        r, c = divmod(i, cols)
        x = pad + c * (cw + gap)
        y = top + r * (ch + gap)
        out.append(f'<rect x="{x}" y="{y}" width="{cw}" height="{ch - 36}" rx="12" fill="{p[tok]}" stroke="{p["border"]}" stroke-width="1"/>')
        out.append(
            f'<text x="{x + 2}" y="{y + ch - 18}" font-family="system-ui,-apple-system,Segoe UI,Roboto,sans-serif" font-size="14" font-weight="600" fill="{p["text"]}">{html.escape(tok)}</text>'
            f'<text x="{x + 2}" y="{y + ch - 2}" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" font-size="12.5" fill="{p["muted"]}">{p[tok]}</text>'
        )
    out.append("</svg>")
    return "\n".join(out) + "\n"


def export(pals, dist: Path):
    out = dist / "brand"
    out.mkdir(parents=True, exist_ok=True)
    bv = brand_values(pals["dark"][0])
    for name in ("logo", "mark"):
        (out / f"{name}.svg").write_text(fill((BRAND / f"{name}.svg.tpl").read_text(), bv))
    for mode in ("dark", "light"):
        (out / f"palette-{mode}.svg").write_text(palette_svg(mode.capitalize(), pals[mode][0]))
