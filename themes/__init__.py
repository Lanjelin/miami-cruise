"""App themes. Each module here that defines `export(pals, dist)` is a theme and is found automatically.

A theme module may also define GUIDE (its install guide, metadata and screenshots); see themes/nvim.py.
Adding an app is dropping one file in this folder. `brand` and `guides` are helpers, not apps.
"""
import importlib
import pkgutil

NOT_APPS = {"brand", "guides"}

# Catalogue order and text-badge tone. Each app chooses one group in its GUIDE;
# cards, filter chips and the README table follow the same order.
GROUPS = {
    "Editors": "accent",
    "Terminal & shell": "accent",
    "Files & finding": "info",
    "Git & diffs": "orchid",
    "Reading & monitoring": "info",
    "Browser & web": "accent",
    "Design resources": "orchid",
}


def modules():
    """{name: module} for every app theme, sorted by name."""
    found = {}
    for info in sorted(pkgutil.iter_modules(__path__), key=lambda i: i.name):
        if info.name.startswith("_") or info.name in NOT_APPS:
            continue
        module = importlib.import_module(f"{__name__}.{info.name}")
        if hasattr(module, "export"):
            found[info.name] = module
    return found


def load_guides():
    """{app_id: GUIDE} in catalogue group order, then alphabetically by name."""
    guides = {name: m.GUIDE for name, m in modules().items() if hasattr(m, "GUIDE")}
    unknown = {g["category"] for g in guides.values()} - GROUPS.keys()
    if unknown:
        raise ValueError(f"Unknown app group(s): {sorted(unknown)}; add them to themes.GROUPS")
    rank = {name: i for i, name in enumerate(GROUPS)}
    return dict(sorted(guides.items(), key=lambda kv: (rank[kv[1]["category"]], kv[1]["name"].casefold())))
