"""Install-guide renderer. The guides themselves live in each theme module (GUIDE in themes/<app>.py).

Each guide is written once and used three times: rendered to dist/<app>/README.md here (so the folder
explains itself on GitHub), read by the website for its app pages, and listed in the README apps table.
Commands in guides use the bare file name and assume you run them from the folder that holds the file.
"""
import html
import re
from pathlib import Path

from project import REPO_URL, SITE_URL

from . import load_guides

# ------------------------------------------------------------------ README rendering


def _md(text):
    """The small subset of HTML used in step text, as Markdown."""
    text = re.sub(r"<code>(.*?)</code>", lambda m: "`" + html.unescape(m.group(1)) + "`", text)
    text = re.sub(r"<b>(.*?)</b>", r"**\1**", text)
    return html.unescape(text)


def render_readme(app_id, g):
    out = [f"# Miami Cruise for {g['name']}", "", g["tagline"], ""]
    for src, alt in g["shots"]:
        out.append(f"![{alt}](../../previews/{src})")
    if g["shots"]:
        out.append("")
    rel = [(src.split("/", 1)[1], name, label) for src, name, label in g["files"]]  # relative to dist/<app>/
    files = "\n".join(f"- [`{path}`]({path}): {label}" for path, _, label in rel)
    folders = sorted({str(Path(path).parent) for path, _, _ in rel})
    where = "this folder" if folders == ["."] else "the [`" + folders[0] + "/`](" + folders[0] + ") folder"
    has_commands = any(
        kind == 'code' and any(lang != 'text' for _, lang, _ in content)
        for _, blocks in g['steps'] for kind, content in blocks
    )
    out += [
        "## Install", "",
        g.get("files_heading", "The theme files:"), "", files, "",
        *([_md(g["file_note"]), ""] if g.get("file_note") else []),
        *([f"Run the commands below from {where}, or from wherever you saved the file.", ""] if has_commands else []),
    ]
    for n, (title, blocks) in enumerate(g["steps"], 1):
        out += [f"### {n}. {title}", ""]
        for kind, content in blocks:
            if kind == "p":
                out += [_md(content), ""]
            elif kind in ("note", "warn"):
                tag = "NOTE" if kind == "note" else "WARNING"
                out += [f"> [!{tag}]", f"> {_md(content)}", ""]
            elif kind == "code":
                for label, lang, text in content:
                    if label:
                        out += [f"**{label}**", ""]
                    out += [f"```{lang}", text, "```", ""]
    out += [
        "## Details", "",
        f"- **Variants:** {g.get('variants', 'dark and light')}",
        f"- **Covers:** {g['covers']}",
        f"- **Glow:** {g['glow']}",
        f"- **Tested:** {g['tested']}",
        "",
        "## More", "",
        f"- [Website page for {g['name']}]({SITE_URL}/apps/{app_id}.html)",
        "- [Palette and specification](../../docs/SPEC.md)",
        f"- [Report a problem]({REPO_URL}/issues/new/choose)",
        "- [MIT licence](../../LICENSE)",
        "",
    ]
    return "\n".join(out)


def export(pals, dist: Path):
    for app_id, guide in load_guides().items():
        (dist / app_id).mkdir(parents=True, exist_ok=True)
        (dist / app_id / "README.md").write_text(render_readme(app_id, guide))
