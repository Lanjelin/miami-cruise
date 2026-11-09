"""Illustrative browser-chrome previews built from the shipped Brave manifests.

These are diagrams, not screenshots of a live Brave window. The page area uses
the light palette in both variants to make the theme's scope explicit.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from palette import build_palette  # noqa: E402


def colour(values):
    return '#%02x%02x%02x' % tuple(values)


def render(variant):
    path = ROOT / 'dist/brave' / variant / 'manifest.json'
    c = {k: colour(v) for k, v in json.loads(path.read_text())['theme']['colors'].items()}
    page = build_palette('light')[0]
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="420" viewBox="0 0 1200 420" role="img" aria-label="Illustrative {variant} Brave browser theme preview; page content is unchanged">
<defs><clipPath id="window"><rect x="20" y="20" width="1160" height="380" rx="20"/></clipPath></defs>
<style>text {{ font-family: system-ui, -apple-system, sans-serif; }} .tab {{font-size: 18px;font-weight: 600}} .small {{font-size: 14px}} .body {{font-size: 19px}}</style>
<rect width="1200" height="420" fill="{c['frame']}"/>
<rect x="20" y="20" width="1160" height="380" rx="20" fill="{c['toolbar']}" stroke="{c['tab_background_text']}" stroke-opacity=".35" stroke-width="2"/>
<g clip-path="url(#window)">
<rect x="20" y="20" width="1160" height="66" fill="{c['frame']}"/>
<rect x="52" y="37" width="255" height="50" rx="13" fill="{c['toolbar']}"/>
<text x="76" y="69" class="tab" fill="{c['tab_text']}">Miami Cruise</text>
<text x="337" y="68" class="tab" fill="{c['tab_background_text']}">Another tab</text>
<text x="1100" y="66" class="tab" fill="{c['tab_background_text']}">+</text>
<rect x="20" y="86" width="1160" height="82" fill="{c['toolbar']}"/>
<text x="57" y="136" class="body" fill="{c['toolbar_button_icon']}">‹</text>
<text x="95" y="136" class="body" fill="{c['toolbar_button_icon']}">›</text>
<text x="135" y="136" class="body" fill="{c['toolbar_button_icon']}">↻</text>
<rect x="190" y="104" width="810" height="48" rx="24" fill="{c['omnibox_background']}"/>
<text x="213" y="135" class="small" fill="{c['omnibox_text']}">example.com</text>
<text x="1030" y="136" class="body" fill="{c['toolbar_button_icon']}">☆</text>
<text x="1080" y="136" class="body" fill="{c['toolbar_button_icon']}">☰</text>
<rect x="20" y="168" width="1160" height="232" fill="{page['bg']}"/>
<text x="66" y="246" font-size="29" font-weight="700" fill="{page['text']}">Web pages keep their own colours</text>
<text x="66" y="281" class="body" fill="{page['muted']}">Miami Cruise themes the browser frame, tabs, toolbar and address bar.</text>
<rect x="66" y="317" width="345" height="43" rx="9" fill="{page['panel']}"/>
<text x="84" y="345" class="small" fill="{page['muted']}">Illustrative preview · {variant.title()} variant</text>
</g></svg>'''
    (ROOT / 'previews/brave' / f'{variant}.svg').write_text(svg + '\n')


if __name__ == '__main__':
    for variant in ('dark', 'light'):
        render(variant)
