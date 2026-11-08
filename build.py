#!/usr/bin/env python3
"""Build Miami Cruise: theme files into dist/<target>/, docs, and the website into website/dist/.

Run:  python3 -I build.py                 (everything)
      python3 -I build.py nvim web        (selected targets)
      python3 -I build.py -v              (also print the token table and contrast ratios)
Fails if a contrast requirement in palette.py is not met.

Adding an app: drop one module in themes/ (see themes/nvim.py). It is found automatically.
Targets run in this order: app themes (alphabetical), brand, guides, docs, website.
"""
import sys
from pathlib import Path

sys.dont_write_bytecode = True  # no __pycache__ in the project: stale bytecode can never affect a build

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import themes  # noqa: E402
from docs import generate as docs  # noqa: E402
from palette import PALETTES, TOKEN_ORDER, build_palette, contrast  # noqa: E402
from themes import brand, guides  # noqa: E402
from website import generate as website  # noqa: E402

DIST = HERE / "dist"


def targets():
    return {**themes.modules(), "brand": brand, "guides": guides, "docs": docs, "website": website}


def print_tokens(pals):
    for name, (p, _) in pals.items():
        print(f"[{name}]")
        for k in TOKEN_ORDER:
            plain = k in ("bg", "panel", "border", "hover", "row", "on-accent", "focus")
            ratio = None if plain else contrast(p[k], p["bg"])
            print(f"  {k:10s} {p[k]}" + (f"  {ratio:4.1f}:1" if ratio else ""))
        print(f"  on-accent vs accent {contrast(p['on-accent'], p['accent']):.1f}:1")


def main(wanted, verbose):
    pals = {n: build_palette(n) for n in PALETTES}
    if verbose:
        print_tokens(pals)
    available = targets()
    for name in wanted:
        available[name].export(pals, DIST)
        print(f"built {name}")


if __name__ == "__main__":
    args = sys.argv[1:]
    verbose = "-v" in args or "--verbose" in args
    names = [a for a in args if not a.startswith("-")]
    available = targets()
    bad = [n for n in names if n not in available]
    if bad:
        raise SystemExit(f"unknown target(s): {bad}; choose from {list(available)}")
    main(names or list(available), verbose)
