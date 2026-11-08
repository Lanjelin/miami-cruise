"""Website content: everything you edit to change what the site says. No rendering code lives here.

The project URLs live in ../project.py. Each app's install guide, files, screenshots, category and tags live in
its theme module (../themes/<app>.py), so this file only holds site-wide text.

Adding an app: add one module to themes/ and run `python3 -I build.py`. The build fails on a broken link or a
low-contrast pair.
"""
import re

from project import REPO_URL, SITE_URL  # noqa: F401  (re-exported for the generator)
from themes import load_guides

TAGLINE = "Teal-ink neutrals. One magenta hero. Dark and light, for your editor, terminal and web."

# ------------------------------------------------------------------ apps
# Everything about an app (guide, files, screenshots, category, tags, search words) comes from its theme
# module (GUIDE in themes/<app>.py), so adding an app never means editing this file.

DEFAULTS = dict(category="Other", tags=[], aliases="")


def default_badge(name):
    """Short names stay readable; longer names use at most three initials."""
    words = re.findall(r"[^\W_]+", name, re.UNICODE)
    if not words:
        return "?"
    if len(words) == 1 and len(words[0]) <= 4:
        return words[0]
    return "".join(word[0] for word in words[:3]).upper()


APPS = [{**DEFAULTS, "mono": default_badge(g["name"]), "id": app_id, **g} for app_id, g in load_guides().items()]

TOKEN_USE = {
    "bg": "Page / main surface", "panel": "Sidebars, headers, recessed panels", "border": "Dividers and borders",
    "hover": "Hover background", "row": "Alternate table row", "text": "Body text", "muted": "Secondary text",
    "disabled": "Disabled and placeholder text", "accent": "Hero: primary action, selection, focus, links",
    "on-accent": "Text on an accent fill", "focus": "Focus ring", "success": "Done, positive", "warning": "Waiting, caution",
    "danger": "Error, overdue, destructive", "info": "Information, in progress", "orange": "Materials, review",
    "orchid": "Secondary highlight",
}
