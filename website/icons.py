"""Optional, locally vendored app logos. No asset means the GUIDE's text fallback."""
import json
from pathlib import Path

ASSETS = Path(__file__).resolve().parent / "assets" / "apps"


def load_icons():
    icons = {}
    for asset in sorted(ASSETS.glob("*.svg")):
        record = asset.with_suffix(".json")
        if not record.is_file():
            raise ValueError(f"App logo needs source and licence metadata: {asset}")
        meta = json.loads(record.read_text())
        for field in ("name", "creator", "license", "license_url", "source", "evidence", "changes", "checked"):
            if not meta.get(field):
                raise ValueError(f"App logo missing {field}: {record}")
        if meta.get("license_file") and not (ASSETS / meta["license_file"]).is_file():
            raise ValueError(f"App logo licence notice missing: {record}")
        icons[asset.stem] = meta
    return icons


ICONS = load_icons()
