"""Website content: everything you edit to change what the site says. No rendering code lives here.

Publishing: SITE_URL and REPO_URL point at the published project. The site uses them for source links and
curl download commands; if you empty them it leaves those out.

Adding an app: add one dict to APPS below (files, steps, tags), put its screenshots under ../previews/,
and run `python3 -I build.py website`. The build fails on a broken link or a low-contrast pair.
"""
# Where the project is published. Leave empty to omit repo links and download commands.
SITE_URL = "https://lanjelin.github.io/miami-cruise"
REPO_URL = "https://github.com/lanjelin/miami-cruise"

TAGLINE = "Teal-ink neutrals. One magenta hero. Dark and light, for your editor, terminal and web."

# ------------------------------------------------------------------ content
# Step blocks: ("p", html) | ("note", html) | ("warn", html) | ("code", [(os_label|None, lang, text), ...])

APPS = [
    dict(
        id="nvim", name="Neovim", mono="N", tags=["Editor", "Lua"],
        aliases="neovim nvim lua treesitter lsp editor vim",
        tagline="A Neovim colorscheme with Treesitter, LSP, diagnostics, diff, gitsigns and Telescope.",
        files=[("nvim/colors/miami-cruise.lua", "miami-cruise.lua", "Neovim colorscheme")],
        shots=[("nvim/dark.png", "Neovim with the dark theme"), ("nvim/light.png", "Neovim with the light theme")],
        tested="Neovim 0.12 with Treesitter",
        covers="Editor UI, Treesitter, LSP, diagnostics, diff, gitsigns, Telescope, :terminal colours",
        glow="No: a flat palette",
        steps=[
            ("Download", [("p", "Download <code>miami-cruise.lua</code> using the box on this page.")]),
            ("Put it where Neovim looks for colorschemes", [
                ("code", [
                    ("macOS / Linux", "bash", "mkdir -p ~/.config/nvim/colors\ncp ~/Downloads/miami-cruise.lua ~/.config/nvim/colors/"),
                    ("Windows (PowerShell)", "powershell",
                     'New-Item -ItemType Directory -Force "$env:LOCALAPPDATA\\nvim\\colors" | Out-Null\nCopy-Item "$HOME\\Downloads\\miami-cruise.lua" "$env:LOCALAPPDATA\\nvim\\colors\\"'),
                ]),
                ("note", "If you set <code>$XDG_CONFIG_HOME</code>, use <code>$XDG_CONFIG_HOME/nvim/colors/</code> instead."),
            ]),
            ("Turn it on", [
                ("p", "Add this to your <code>init.lua</code>. To try it first, run <code>:colorscheme miami-cruise</code> inside Neovim."),
                ("code", [(None, "lua", 'vim.o.background = "dark" -- or "light"\nvim.cmd.colorscheme("miami-cruise")')]),
            ]),
            ("Switch between dark and light", [
                ("p", "The theme follows <code>'background'</code>. Change it at any time and the colours update: <code>:set background=light</code>."),
                ("note", "It turns on <code>termguicolors</code> for you, so a true-colour terminal is needed."),
            ]),
        ],
    ),
    dict(
        id="vim", name="Vim", mono="V", tags=["Editor", "Vimscript"],
        aliases="vim vi vimscript editor gvim",
        tagline="A Vim colorscheme with true colour and a 256-colour fallback.",
        files=[("vim/colors/miami-cruise.vim", "miami-cruise.vim", "Vim colorscheme")],
        shots=[("vim/dark.png", "Vim with the dark theme"), ("vim/light.png", "Vim with the light theme")],
        tested="Vim 9.1",
        covers="Editor UI, syntax groups, diff, spell, popup menu, tab line, terminal colours",
        glow="No: a flat palette",
        steps=[
            ("Download", [("p", "Download <code>miami-cruise.vim</code> using the box on this page.")]),
            ("Put it where Vim looks for colorschemes", [
                ("code", [
                    ("macOS / Linux", "bash", "mkdir -p ~/.vim/colors\ncp ~/Downloads/miami-cruise.vim ~/.vim/colors/"),
                    ("Windows (PowerShell)", "powershell",
                     'New-Item -ItemType Directory -Force "$HOME\\vimfiles\\colors" | Out-Null\nCopy-Item "$HOME\\Downloads\\miami-cruise.vim" "$HOME\\vimfiles\\colors\\"'),
                ]),
            ]),
            ("Turn it on", [
                ("p", "Add this to your <code>vimrc</code>. To try it first, run <code>:colorscheme miami-cruise</code>."),
                ("code", [(None, "vim", 'syntax on\nset background=dark   " or light\ncolorscheme miami-cruise')]),
            ]),
            ("Colours in the terminal", [
                ("p", "In a true-colour terminal (<code>$COLORTERM</code> is <code>truecolor</code> or <code>24bit</code>) the theme uses its exact colours. "
                      "Elsewhere it falls back to the nearest of the 256 xterm colours, so it still looks right."),
                ("note", "Changing <code>background</code> later reloads the theme by itself."),
            ]),
        ],
    ),
    dict(
        id="wezterm", name="WezTerm", mono="W", tags=["Terminal", "Lua"],
        aliases="wezterm wez terminal lua tabs windows macos linux",
        tagline="Colour schemes and tab bar that follow your system's dark or light setting.",
        files=[("wezterm/miami-cruise.lua", "miami-cruise.lua", "WezTerm module")],
        shots=[("wezterm/palette.png", "WezTerm window in the dark and light variants (mock-up)")],
        tested="Logic tested against a stand-in for WezTerm's Lua API; colour fields checked against WezTerm's docs and source",
        covers="Foreground, background, cursor, selection, 16 ANSI colours, tab bar, copy mode, quick select",
        glow="No: a flat palette",
        steps=[
            ("Download", [("p", "Download <code>miami-cruise.lua</code> using the box on this page.")]),
            ("Put it next to your wezterm.lua", [
                ("code", [
                    ("macOS / Linux", "bash", "mkdir -p ~/.config/wezterm\ncp ~/Downloads/miami-cruise.lua ~/.config/wezterm/"),
                    ("Windows (PowerShell)", "powershell",
                     'New-Item -ItemType Directory -Force "$HOME\\.config\\wezterm" | Out-Null\nCopy-Item "$HOME\\Downloads\\miami-cruise.lua" "$HOME\\.config\\wezterm\\"'),
                ]),
                ("note", "It must sit in the same folder as your config file. If you use a single <code>~/.wezterm.lua</code>, put it in your home folder."),
            ]),
            ("Load it in your config", [
                ("code", [(None, "lua",
                           'local wezterm = require("wezterm")\nlocal config = wezterm.config_builder()\n\n'
                           'package.path = wezterm.config_dir .. "/?.lua;" .. package.path\nrequire("miami-cruise").apply(config)\n\nreturn config')]),
                ("p", "That is all. The theme follows the system dark/light setting, and WezTerm reloads your config when the system switches."),
            ]),
            ("Force dark or light (optional)", [
                ("p", "Set <code>MIAMI_CRUISE</code> to <code>dark</code>, <code>light</code> or <code>auto</code> (the default) in the environment WezTerm starts from:"),
                ("code", [
                    ("macOS / Linux", "bash", "MIAMI_CRUISE=light wezterm"),
                    ("Windows (PowerShell)", "powershell", '$env:MIAMI_CRUISE = "light"; wezterm'),
                ]),
                ("p", "Or pin it in the config file. The environment variable still wins over this:"),
                ("code", [(None, "lua", 'require("miami-cruise").apply(config, { mode = "light" })')]),
                ("warn", "<b>Launched from the Dock or Start menu?</b> Those don't see variables you set in a shell, so pin it in the config with <code>mode</code>."),
                ("note", "The schemes are registered as <code>Miami Cruise</code> and <code>Miami Cruise Day</code>, so <code>config.color_scheme = \"Miami Cruise Day\"</code> also works."),
            ]),
        ],
    ),
    dict(
        id="web", name="Web / CSS", mono="W3", tags=["Web", "CSS"],
        aliases="web css website html variables custom properties glow theme",
        tagline="CSS variables for the palette, plus an optional glow layer.",
        files=[("web/miami-cruise.css", "miami-cruise.css", "CSS variables"), ("web/glow.css", "glow.css", "Optional glow layer")],
        shots=[("web/palette.png", "A sample interface in the dark theme, the light theme, and the dark theme without glow")],
        tested="This site is built on exactly these files",
        covers="All 17 palette tokens as --mc-* variables, dark and light, and four optional glow classes",
        glow="Optional: glow.css",
        steps=[
            ("Download", [("p", "Download <code>miami-cruise.css</code>, and <code>glow.css</code> if you want the glow.")]),
            ("Link the stylesheets", [
                ("code", [(None, "html", '<link rel="stylesheet" href="miami-cruise.css">\n<!-- optional -->\n<link rel="stylesheet" href="glow.css">')]),
            ]),
            ("Use the variables", [
                ("code", [(None, "css", "body { background: var(--mc-bg); color: var(--mc-text); }\na { color: var(--mc-accent); }\n.card { background: var(--mc-panel); border: 1px solid var(--mc-border); }\n.btn { background: var(--mc-accent); color: var(--mc-on-accent); }")]),
                ("p", "With <code>glow.css</code> you can add <code>mc-primary</code> (glowing button), <code>mc-focus</code> (glowing focus ring), <code>mc-selected</code> and <code>mc-surface</code> (soft top-lit background)."),
                ("note", "The glow only decorates states that already work without it, and browsers without <code>color-mix</code> simply skip it."),
            ]),
            ("Dark, light, or follow the system", [
                ("p", "Dark is the default. Set <code>data-theme=\"light\"</code> on <code>&lt;html&gt;</code> for the light variant. To follow the system:"),
                ("code", [(None, "html", '<script>\n  var m = matchMedia("(prefers-color-scheme: light)");\n  function sync() { document.documentElement.dataset.theme = m.matches ? "light" : "dark"; }\n  m.addEventListener("change", sync); sync();\n</script>')]),
            ]),
        ],
    ),
    dict(
        id="tokens", name="Design tokens", mono="{}", tags=["JSON", "Any app"],
        aliases="tokens json design palette colours colors port other app custom",
        tagline="The palette as JSON, for any app that isn't listed yet.",
        files=[("tokens/tokens.json", "tokens.json", "Palette tokens"), ("tokens/contrast.json", "contrast.json", "Contrast ratios")],
        shots=[],
        tested="Generated from the same source as every other target",
        covers="17 tokens in dark and light, plus contrast ratios against the background",
        glow="n/a",
        steps=[
            ("Download", [("p", "Download <code>tokens.json</code>. <code>contrast.json</code> lists the contrast ratios if you want to check your own pairings.")]),
            ("Read the tokens", [
                ("p", "The file has a <code>dark</code> and a <code>light</code> object, each mapping a token name to a hex colour."),
                ("code", [(None, "python", 'import json\n\ntokens = json.load(open("tokens.json"))\nprint(tokens["dark"]["accent"])  # the hero colour')]),
            ]),
            ("Map them to your app", [
                ("p", "<code>accent</code> is the single highlight colour: primary action, selection, focus, links. "
                      "<code>success</code>, <code>warning</code>, <code>danger</code> and <code>info</code> are green, yellow, red and cyan. "
                      "<code>text</code>, <code>muted</code> and <code>disabled</code> are the text ramp. "
                      "<code>bg</code>, <code>panel</code>, <code>border</code>, <code>hover</code> and <code>row</code> are surfaces. "
                      "<code>on-accent</code> is the text colour to use on an <code>accent</code> fill."),
                ("note", "Every text and accent colour is at least 4.5:1 against <code>bg</code>, so you can use them for text without checking."),
            ]),
        ],
    ),
]

TOKEN_USE = {
    "bg": "Page / main surface", "panel": "Sidebars, headers, recessed panels", "border": "Dividers and borders",
    "hover": "Hover background", "row": "Alternate table row", "text": "Body text", "muted": "Secondary text",
    "disabled": "Disabled and placeholder text", "accent": "Hero: primary action, selection, focus, links",
    "on-accent": "Text on an accent fill", "focus": "Focus ring", "success": "Done, positive", "warning": "Waiting, caution",
    "danger": "Error, overdue, destructive", "info": "Information, in progress", "orange": "Materials, review",
    "orchid": "Secondary highlight",
}
