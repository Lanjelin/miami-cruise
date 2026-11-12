"""Native bat .tmTheme files, generated from the shared syntax mapping."""
from ._textmate import export_themes, install_steps

GUIDE = dict(
    name="bat", category="Reading & monitoring", mono="bat",
    tags=["CLI", "Syntax", "TextMate"], aliases="bat batcat cat syntax highlighting pager tmtheme",
    status="Beta. Tested with bat 0.26.1 on Linux; macOS and Windows not tested",
    tagline="Readable syntax highlighting for source files, with Miami Cruise colours.",
    files=[(f"bat/miami-cruise-{v}.tmTheme", f"miami-cruise-{v}.tmTheme", f"{v.title()} theme") for v in ("dark", "light")],
    shots=[("bat/dark.png", "bat syntax highlighting with the dark theme"),
           ("bat/light.png", "bat syntax highlighting with the light theme")],
    tested="bat 0.26.1 on Linux: both variants, custom cache loading, Python, JavaScript, Rust, JSON and Markdown; macOS and Windows not tested",
    covers="Keywords, strings, numbers, functions, types, comments, markup, punctuation and gutters",
    glow="No: terminal output uses the flat palette",
    steps=[install_steps(), ("Choose a variant", [
        ("code", [(None, "bash", "bat --theme=miami-cruise-dark --color=always --paging=never build.py")]),
        ("p", "Use <code>--theme=miami-cruise-light</code> for light mode. Alternatively, after installing the themes and rebuilding the cache, select the default through <code>BAT_THEME</code>:"),
        ("code", [
            ("macOS / Linux", "bash", 'export BAT_THEME="miami-cruise-dark"'),
            ("Windows (PowerShell)", "powershell", '$env:BAT_THEME = "miami-cruise-dark"'),
        ]),
        ("p", "Use <code>miami-cruise-light</code> for the light variant. These assignments affect the current shell and its child processes; add the appropriate assignment to your shell profile if you want it in new sessions. The variable selects an installed theme; it does not install or rebuild the syntax cache. An explicit command-line <code>--theme</code> overrides this selection."),
        ("p", "If you prefer bat's own config file instead, add <code>--theme=miami-cruise-dark</code> to the file reported by <code>bat --config-file</code>, preserving your other options. Choose one default-selection method rather than setting conflicting defaults."),
        ("note", "bat colours the output, not the terminal's background. Use the matching Miami Cruise terminal palette. This port does not automatically switch variants."),
    ])],
)


def export(pals, dist):
    export_themes(pals, dist / "bat")
