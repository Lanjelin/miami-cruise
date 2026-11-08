"""App themes. Each module here that defines `export(pals, dist)` is a theme and is found automatically.

A theme module may also define GUIDE (its install guide, metadata and screenshots); see themes/nvim.py.
Adding an app is dropping one file in this folder. `brand` and `guides` are helpers, not apps.
"""
import importlib
import pkgutil

NOT_APPS = {"brand", "guides"}


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
    """{app_id: GUIDE} for every theme that has one, in display order (order, then name)."""
    guides = {name: m.GUIDE for name, m in modules().items() if hasattr(m, "GUIDE")}
    return dict(sorted(guides.items(), key=lambda kv: (kv[1].get("order", 50), kv[1]["name"].lower())))
