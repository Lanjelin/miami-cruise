#!/usr/bin/env python3
"""Build Miami Cruise: theme files into dist/<target>/ and the website into website/dist/.

Run:  python3 -I build.py            (all targets)
      python3 -I build.py nvim web   (selected targets)
      python3 -I build.py website    (the website only; needs the themes built first)
Fails if a contrast requirement in palette.py is not met.
To add an app theme: write themes/<app>.py with export(pals, dist), then list it in EXPORTERS.
The website lives in website/ (content in website/content.py); it is the last target.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from palette import PALETTES, TOKEN_ORDER, build_palette, contrast  # noqa: E402
from themes import brand, nvim, tokens, vim, web, wezterm  # noqa: E402
from website import generate as site  # noqa: E402

DIST = HERE / "dist"
EXPORTERS = {"tokens": tokens, "web": web, "nvim": nvim, "vim": vim, "wezterm": wezterm, "brand": brand, "website": site}


def main(targets):
    pals = {n: build_palette(n) for n in PALETTES}
    for n, (p, _) in pals.items():
        print(f"[{n}]")
        for k in TOKEN_ORDER:
            ratio = contrast(p[k], p["bg"]) if k not in ("bg", "panel", "border", "hover", "row", "on-accent", "focus") else None
            print(f"  {k:10s} {p[k]}" + (f"  {ratio:4.1f}:1" if ratio else ""))
        print(f"  on-accent vs accent {contrast(p['on-accent'], p['accent']):.1f}:1")
    for t in targets:
        EXPORTERS[t].export(pals, DIST)
        print(f"built {t}")


if __name__ == "__main__":
    wanted = sys.argv[1:] or list(EXPORTERS)
    bad = [t for t in wanted if t not in EXPORTERS]
    if bad:
        raise SystemExit(f"unknown target(s): {bad}; choose from {list(EXPORTERS)}")
    main(wanted)
