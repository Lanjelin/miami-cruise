"""Token exporter: JSON for tools that map tokens themselves, plus contrast ratios."""
import json
from pathlib import Path

from palette import TOKEN_ORDER, contrast

TEXT_KEYS = ("text", "muted", "disabled", "accent", "success", "warning", "danger", "info", "orange", "orchid")


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
