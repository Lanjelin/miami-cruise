"""Native fzf option files: appearance only, no shell code or picker behaviour."""
from palette import contrast


def render(p, variant):
    for fg, bg in (("text", "hover"), ("text", "bg"), ("accent", "bg")):
        if contrast(p[fg], p[bg]) < 4.5:
            raise ValueError(f"fzf: {fg} on {bg} is below 4.5:1")
    roles = {
        "fg": "text", "bg": "terminal", "hl": "accent",
        "fg+": "text", "bg+": "hover", "hl+": "text",
        "selected-fg": "text", "selected-bg": "hover", "selected-hl": "text",
        "gutter": "terminal", "query": "text", "disabled": "disabled", "ghost": "disabled",
        "info": "muted", "border": "disabled", "separator": "disabled",
        "scrollbar": "info", "label": "accent", "prompt": "accent",
        "pointer": "accent", "marker": "accent", "spinner": "info",
        "header": "info", "footer": "muted", "preview-fg": "text",
        "preview-bg": "terminal", "preview-border": "disabled", "preview-scrollbar": "info",
        "input-bg": "terminal", "header-bg": "terminal", "footer-bg": "terminal",
    }
    entries = [variant]
    for role, token in roles.items():
        # Matches on tinted selections use body text + underline, not low-contrast accents.
        attrs = ":regular:bold:underline" if role in ("hl+", "selected-hl") else ":regular"
        if role in ("hl", "prompt", "pointer", "marker"):
            attrs += ":bold"
        entries.append(f"{role}:{'-1' if token == 'terminal' else p[token]}{'' if token == 'terminal' else attrs}")
    return "--color=" + ",".join(entries) + "\n"


GUIDE = dict(
    name="fzf", category="Files & finding", mono="fzf",
    tags=["Search", "CLI", "Options"], aliases="fzf fuzzy finder search picker shell",
    status="Beta. Tested with fzf 0.75.0 on Linux; macOS and Windows not tested",
    tagline="Magenta search highlights and clear selections over your terminal background.",
    files=[(f"fzf/miami-cruise-{v}.opts", f"miami-cruise-{v}.opts", f"Native fzf options · {v}") for v in ("dark", "light")],
    file_note="These are plain fzf option files containing only <code>--color</code>, not shell scripts. Do not source them. No dependency on bat or delta is required.",
    shots=[("fzf/dark.png", "fzf picker with the dark theme: search matches, multi-selection and bat preview"),
           ("fzf/light.png", "fzf picker with the light theme: search matches, multi-selection and bat preview")],
    tested="fzf 0.75.0 on Linux: native options-file loading, existing defaults, search, current/multi-selection, accept/cancel, no matches and optional bat 0.26.1 preview; macOS, Windows and fish not tested",
    covers="Text, terminal background, search matches, current and multi-selected rows, markers, prompt, counters, borders, labels, scrollbars, header, footer and preview chrome",
    glow="No: the flat palette",
    steps=[("Load the colours alongside your current options", [
        ("p", "Install fzf first and keep the downloaded file in a permanent folder. Append its contents to your current <code>FZF_DEFAULT_OPTS</code>, using the actual absolute path. The picker and preview base backgrounds use the terminal default (<code>bg:-1</code>); selected rows retain a tint. Use a matching dark/light terminal background. Existing bindings, layout and preview commands remain unchanged. Run once in your current shell to try it."),
        ("code", [
            ("Bash / Zsh", "bash", 'export FZF_DEFAULT_OPTS="${FZF_DEFAULT_OPTS-} $(cat /absolute/path/to/miami-cruise-dark.opts)"\nfzf'),
            ("Fish", "fish", 'set -gx FZF_DEFAULT_OPTS "$FZF_DEFAULT_OPTS "(string join " " < /absolute/path/to/miami-cruise-dark.opts)\nfzf'),
            ("Windows (PowerShell)", "powershell", '$theme = [System.IO.File]::ReadAllText("C:/absolute/path/to/miami-cruise-dark.opts").Trim()\n$env:FZF_DEFAULT_OPTS = "$env:FZF_DEFAULT_OPTS $theme"\nfzf'),
        ]),
        ("p", "For light mode, substitute <code>miami-cruise-light.opts</code>. There is no automatic switching in these files. To keep the theme, add the corresponding assignment once after your existing fzf options in your shell config; do not replace your config or repeatedly append the assignment. Remove that assignment to uninstall, then start a new shell."),
        ("note", "fzf also supports <code>FZF_DEFAULT_OPTS_FILE</code>. If you do not already use it, you may point it at this file instead. If you already have an options file, keep it and use the append method above: replacing the variable would discard that file's settings. Explicit command-line colour options and integration-specific overrides can take precedence."),
    ]), ("Optional: add a matching bat preview", [
        ("p", "The fzf theme colours the picker and preview frame, not syntax emitted by other programs. Install the separate Miami Cruise bat port only if you want matching syntax colours. Then try this from a directory of source files (requires <code>rg</code> and <code>bat</code>):"),
        ("code", [("Bash / Zsh", "bash", "rg --files | fzf --multi --preview 'bat --color=always --paging=never --style=numbers --theme=miami-cruise-dark -- {}' --preview-window=right:60%")]),
        ("p", "For light mode, change both the loaded fzf options and bat's theme name. The preview command is an example only; the downloaded theme does not set a preview, keybindings, commands or layout."),
        ("note", "Use a true-colour terminal. ANSI-coloured input and preview output may supply their own colours. The tested release is fzf 0.75.0; older versions may not recognize newer colour names. Native option reference: https://github.com/junegunn/fzf/blob/master/man/man1/fzf.1"),
    ])],
)


def export(pals, dist):
    out = dist / "fzf"
    out.mkdir(parents=True, exist_ok=True)
    for variant, (p, _) in pals.items():
        (out / f"miami-cruise-{variant}.opts").write_text(render(p, variant))
