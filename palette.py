"""Miami Cruise palette: colour maths, OKLCH source values, token build.

This is the single source of truth. Modules in themes/ and website/ only read the result.
Palettes are defined in OKLCH (lightness, chroma, hue) in PALETTES below.
"""
import json
import math

VERSION = "0.1.0"


# ---------------------------------------------------------------- colour maths


def _lin_to_srgb(x):
    return 12.92 * x if x <= 0.0031308 else 1.055 * x ** (1 / 2.4) - 0.055


def _oklch_to_lin(L, C, h):
    a, b = C * math.cos(math.radians(h)), C * math.sin(math.radians(h))
    l = (L + 0.3963377774 * a + 0.2158037573 * b) ** 3
    m = (L - 0.1055613458 * a - 0.0638541728 * b) ** 3
    s = (L - 0.0894841775 * a - 1.291485548 * b) ** 3
    return (
        4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
        -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
        -0.0041960863 * l - 0.7034186147 * m + 1.707614701 * s,
    )


def oklch_hex(L, C, h):
    """OKLCH -> sRGB hex; chroma is reduced until the colour is in gamut."""
    lo, hi = 0.0, C
    rgb = _oklch_to_lin(L, C, h)
    if not all(-1e-4 <= v <= 1 + 1e-4 for v in rgb):
        for _ in range(30):
            mid = (lo + hi) / 2
            if all(-1e-4 <= v <= 1 + 1e-4 for v in _oklch_to_lin(L, mid, h)):
                lo = mid
            else:
                hi = mid
        rgb = _oklch_to_lin(L, lo, h)
    return "#%02x%02x%02x" % tuple(round(max(0, min(1, _lin_to_srgb(v))) * 255) for v in rgb)


def luminance(hexv):
    c = [int(hexv[i : i + 2], 16) / 255 for i in (1, 3, 5)]
    c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def contrast(a, b):
    hi, lo = sorted((luminance(a), luminance(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def rgb(hexv):
    return tuple(int(hexv[i : i + 2], 16) for i in (1, 3, 5))


# ------------------------------------------------------------------- palettes
# name: (L, C, hue, min contrast vs bg or None). L is nudged until the minimum is met.
NEUTRAL_HUE = 215  # teal ink
HERO_HUE = 350  # magenta

PALETTES = {
    "dark": dict(
        neutrals=dict(
            bg=(0.22, 0.024, NEUTRAL_HUE),
            panel=(0.185, 0.026, NEUTRAL_HUE),
            border=(0.34, 0.030, NEUTRAL_HUE),
            hover=(0.28, 0.028, NEUTRAL_HUE),
            row=(0.245, 0.025, NEUTRAL_HUE),
        ),
        text=dict(
            text=(0.93, 0.014, 205, 7.0),
            muted=(0.77, 0.030, 210, 4.5),
            disabled=(0.62, 0.040, 210, 4.5),
        ),
        accents=dict(
            accent=(0.76, 0.20, HERO_HUE, 4.5),
            success=(0.80, 0.14, 160, 4.5),
            warning=(0.86, 0.13, 95, 4.5),
            danger=(0.72, 0.17, 18, 4.5),
            info=(0.82, 0.10, 215, 4.5),
            orange=(0.78, 0.14, 55, 4.5),
            orchid=(0.78, 0.11, 320, 4.5),
        ),
    ),
    "light": dict(
        neutrals=dict(
            bg=(0.975, 0.008, 205),
            panel=(0.945, 0.012, 205),
            border=(0.880, 0.020, 205),
            hover=(0.935, 0.014, 205),
            row=(0.960, 0.010, 205),
        ),
        text=dict(
            text=(0.27, 0.030, 215, 7.0),
            muted=(0.42, 0.030, 215, 4.5),
            disabled=(0.52, 0.030, 215, 4.5),
        ),
        accents=dict(
            accent=(0.52, 0.20, HERO_HUE, 4.5),
            success=(0.60, 0.13, 160, 4.5),
            warning=(0.62, 0.12, 85, 4.5),
            danger=(0.58, 0.17, 20, 4.5),
            info=(0.60, 0.10, 215, 4.5),
            orange=(0.60, 0.14, 50, 4.5),
            orchid=(0.58, 0.12, 320, 4.5),
        ),
    ),
}


def build_palette(name):
    spec = PALETTES[name]
    dark = name == "dark"
    out, meta = {}, {}
    for k, (L, C, h) in spec["neutrals"].items():
        out[k] = oklch_hex(L, C, h)
        meta[k] = (L, C, h)
    bg = out["bg"]
    for group in ("text", "accents"):
        for k, (L, C, h, need) in spec[group].items():
            step = 0.005 if dark else -0.005
            for _ in range(200):
                hexv = oklch_hex(L, C, h)
                if contrast(hexv, bg) >= need:
                    break
                L += step
            else:
                raise SystemExit(f"{name}.{k}: cannot reach {need}:1")
            out[k] = hexv
            meta[k] = (round(L, 3), C, h)
    # text drawn on top of the accent fill (primary button, selected badge)
    out["on-accent"] = out["bg"] if contrast(out["bg"], out["accent"]) >= contrast(out["panel"], out["accent"]) else out["panel"]
    if contrast(out["on-accent"], out["accent"]) < 4.5:
        raise SystemExit(f"{name}: text on accent below 4.5:1")
    out["focus"] = out["accent"]
    return out, meta


# -------------------------------------------------------------------- exports

TOKEN_ORDER = [
    "bg", "panel", "border", "hover", "row", "text", "muted", "disabled",
    "accent", "on-accent", "focus", "success", "warning", "danger", "info", "orange", "orchid",
]
TOKEN_DOC = {
    "bg": "page / main surface", "panel": "raised or recessed panel, headers, sidebars",
    "border": "dividers, borders, selected neutral", "hover": "hover background", "row": "alternate table row",
    "text": "body text", "muted": "secondary text", "disabled": "disabled / placeholder text",
    "accent": "hero: primary action, selection, focus, links", "on-accent": "text on an accent fill",
    "focus": "focus ring (solid)", "success": "done / positive", "warning": "waiting / caution",
    "danger": "error / overdue / destructive", "info": "information / in progress", "orange": "materials / review",
    "orchid": "secondary highlight / communication",
}
