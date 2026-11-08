"""TextMate syntax palette shared by bat and delta's bat-backed highlighter."""
import plistlib


def render(p, variant):
    rules = [
        ("Comments", "comment", "disabled", "italic"),
        ("Strings", "string", "success", ""),
        ("Escapes", "constant.character.escape", "warning", ""),
        ("Numbers and constants", "constant.numeric, constant.language, constant.other", "orange", ""),
        ("Keywords", "keyword, storage", "accent", ""),
        ("Operators", "keyword.operator", "muted", ""),
        ("Functions", "entity.name.function, support.function", "info", ""),
        ("Types", "entity.name.type, entity.name.class, support.type, support.class", "orchid", ""),
        ("Variables", "variable", "text", ""),
        ("Parameters", "variable.parameter", "text", ""),
        ("Punctuation", "punctuation", "muted", ""),
        ("Tags", "entity.name.tag", "accent", ""),
        ("Attributes", "entity.other.attribute-name", "info", ""),
        ("Invalid", "invalid", "danger", "underline"),
        ("Headings", "markup.heading, entity.name.section", "accent", "bold"),
        ("Emphasis", "markup.italic", "text", "italic"),
        ("Strong", "markup.bold", "text", "bold"),
        ("Inline code", "markup.raw", "success", ""),
        ("Links", "markup.underline.link", "info", "underline"),
        ("Added", "markup.inserted", "success", ""),
        ("Removed", "markup.deleted", "danger", ""),
        ("Changed", "markup.changed", "warning", ""),
    ]
    settings = [{"settings": {
        "foreground": p["text"], "background": p["bg"], "caret": p["accent"],
        "selection": p["hover"], "lineHighlight": p["row"],
        "gutter": p["panel"], "gutterForeground": p["disabled"],
        "invisibles": p["border"], "findHighlight": p["warning"],
        "findHighlightForeground": p["bg"],
    }}]
    settings += [{"name": name, "scope": scope,
                  "settings": {"foreground": p[token], "fontStyle": style}}
                 for name, scope, token, style in rules]
    return plistlib.dumps({"name": f"miami-cruise-{variant}", "author": "Miami Cruise",
                          "settings": settings}, sort_keys=False).decode()


def export_themes(pals, out):
    out.mkdir(parents=True, exist_ok=True)
    for variant, (p, _) in pals.items():
        (out / f"miami-cruise-{variant}.tmTheme").write_text(render(p, variant))


def install_steps(for_delta=False):
    """Native bat cache installation, also required by delta for custom syntax."""
    introduction = ("delta uses bat's syntax-highlighting engine and reads its custom syntax cache. "
                    "The two <code>.tmTheme</code> files are supporting syntax palettes, not delta feature configurations. "
                    "Install bat to build that cache (some Linux packages call it <code>batcat</code>); "
                    "delta does not run bat afterwards. If you already installed the Miami Cruise bat themes, "
                    "skip copying them and check discovery below. See "
                    '<a href="https://dandavison.github.io/delta/supported-languages-and-themes.html">delta\'s custom-syntax documentation</a>.'
                    if for_delta else "Install bat first (some Linux packages name the command <code>batcat</code>). Use a true-colour terminal with the matching dark or light background. These commands use bat's own config directory and do not replace your config file.")
    steps = [
        ("p", introduction),
        ("code", [
            ("macOS / Linux", "bash", 'bat_dir="$(bat --config-dir)"\nmkdir -p "$bat_dir/themes"\ncp miami-cruise-dark.tmTheme miami-cruise-light.tmTheme "$bat_dir/themes/"\nbat cache --build\nbat --list-themes'),
            ("Windows (PowerShell)", "powershell", '$batDir = bat --config-dir\nNew-Item -ItemType Directory -Force "$batDir/themes" | Out-Null\nCopy-Item miami-cruise-dark.tmTheme, miami-cruise-light.tmTheme "$batDir/themes/"\nbat cache --build\nbat --list-themes'),
        ]),
        ("note", "If files with these same names already exist, back them up before copying. To uninstall, remove just these two files from the themes directory and run <code>bat cache --build</code> again. Existing unrelated themes are preserved."),
    ]
    if for_delta:
        steps.append(("p", "Confirm that delta discovers both palettes. You should see <code>miami-cruise-dark</code> and <code>miami-cruise-light</code>:"))
        steps.append(("code", [(None, "bash", "delta --no-gitconfig --list-syntax-themes")]))
    return ("Install delta's supporting syntax palettes" if for_delta else "Install the syntax themes", steps)
