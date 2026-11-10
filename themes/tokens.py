"""Token exporter: JSON for tools that map tokens themselves, plus contrast ratios."""
import json
from pathlib import Path

from palette import TOKEN_ORDER, contrast

TEXT_KEYS = ("text", "muted", "disabled", "accent", "success", "warning", "danger", "info", "orange", "orchid")


# Install guide: rendered to dist/tokens/README.md and used by the website and the README table.
# Step blocks: ("p", html) | ("note", html) | ("warn", html) | ("code", [(os_label | None, lang, text), ...])
GUIDE = dict(
    category='Design resources', mono='{}',
    tags=['JSON', 'Any app'],
    aliases='tokens json design palette colours colors port other app custom',
    status='Design tokens as JSON',
    name="Design tokens",
    tagline="The palette as JSON, for any app that isn't listed yet.",
    files=[("tokens/tokens.json", "tokens.json", "Palette tokens"), ("tokens/contrast.json", "contrast.json", "Contrast ratios")],
    shots=[],
    tested="Generated from the same source as every other target",
    covers="17 tokens in dark and light, plus contrast ratios against the background",
    glow="n/a",
    steps=[
        ("Read the tokens", [
            ("p", "The file has a <code>dark</code> and a <code>light</code> object, each mapping a token name to a hex colour. <code>contrast.json</code> lists the contrast ratios if you want to check your own pairings."),
            ("code", [(None, "python", 'import json\n\ntokens = json.load(open("tokens.json"))\nprint(tokens["dark"]["accent"])  # the hero colour')]),
        ]),
        ("Map them to your app", [
            ("p", "<code>accent</code> is the single highlight colour: primary action, selection, focus, links. "
                  "<code>success</code>, <code>warning</code>, <code>danger</code> and <code>info</code> are green, yellow, red and cyan. "
                  "<code>text</code>, <code>muted</code> and <code>disabled</code> are the text ramp. "
                  "<code>bg</code>, <code>panel</code>, <code>border</code>, <code>hover</code> and <code>row</code> are surfaces. "
                  "<code>on-accent</code> is the text colour to use on an <code>accent</code> fill. "
                  "The full role table is in the porting guide."),
            ("note", "Every text and accent colour is at least 4.5:1 against <code>bg</code>, so you can use them for text without checking."),
        ]),
    ],
)


def export(pals, dist: Path):
    out = dist / "tokens"
    out.mkdir(parents=True, exist_ok=True)
    (out / "tokens.json").write_text(
        json.dumps({n: {k: p[k] for k in TOKEN_ORDER} for n, (p, _) in pals.items()}, indent=2) + "\n"
    )
    ratios = {
        n: {k: round(contrast(p[k], p["bg"]), 2) for k in TEXT_KEYS} | {"on-accent": round(contrast(p["on-accent"], p["accent"]), 2)}
        for n, (p, _) in pals.items()
    }
    (out / "contrast.json").write_text(json.dumps(ratios, indent=2) + "\n")
