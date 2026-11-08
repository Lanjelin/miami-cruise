# Porting guide

How to add Miami Cruise to another app. A port is one small Python module that turns the shared palette into that app's format, so every port stays in step with the palette automatically.

Before you start, read [SPEC.md](SPEC.md) for the tokens and the principles. Open an issue first if you plan a large port, so work isn't duplicated.

## What a port is

```
themes/<app>.py       the exporter: export(pals, dist) writes files to dist/<app>/
dist/<app>/...        the generated theme, committed
previews/<app>/       a sample file and screenshots (optional but expected)
website/content.py    the install page for the app (optional until the port is released)
```

`pals` maps `"dark"` and `"light"` to `(tokens, meta)`. `tokens` is a dict from token name (`bg`, `accent`, `danger`, ...) to a `#rrggbb` string. Use only these values; never hard-code a colour in a port.

## Steps

1. **Write the exporter** in `themes/<app>.py` with an `export(pals, dist)` function. Look at `themes/wezterm.py` (a config module) or `themes/vim.py` (a colorscheme) for a model. `themes/_hl.py` holds highlight groups shared by Vim and Neovim.
2. **Register it** in `EXPORTERS` in `build.py`, before `website`.
3. **Map the tokens** using the table below.
4. **Build and test** it in the real app, in both dark and light. Write down which version you tested.
5. **Add a preview**: a short sample file and a screenshot under `previews/<app>/`, then add the render step to `previews/render.sh`.
6. **Run `python3 -I build.py`** and commit the changes in `dist/`. CI fails if `dist/` is out of date.
7. **Add the site page** (optional now, needed for release): add an entry to `APPS` in `website/content.py` with the files, install steps for macOS, Linux and Windows, and the screenshots.
8. **Update the README** supported-apps table and `CHANGELOG.md`.

## Token roles

| Token | Use it for |
|---|---|
| `bg` | main surface: editor and terminal background, page background |
| `panel` | sidebars, status lines, tab bars, popups, headers |
| `border` | dividers, borders, inactive selection, ANSI black on dark |
| `hover` | hover and cursor-line background |
| `row` | alternate table or list rows |
| `text` | body text and default foreground |
| `muted` | secondary text, punctuation, operators |
| `disabled` | comments, line numbers, placeholders, disabled items |
| `accent` | the hero: keywords, primary action, selection stripe, links, cursor |
| `on-accent` | text drawn on top of an `accent` fill |
| `focus` | focus ring (same colour as `accent`) |
| `success` | strings, added lines, positive status |
| `warning` | special characters, warnings, search highlight |
| `danger` | errors, removed lines, destructive actions |
| `info` | functions, informational status, directories |
| `orange` | numbers, constants, builtins |
| `orchid` | types, preprocessor, secondary highlight |

For terminals map ANSI red, green, yellow, blue, magenta and cyan to `danger`, `success`, `warning`, `orchid`, `accent` and `info`. On a light palette ANSI black must be `text` and ANSI white a light neutral, so "black" stays readable; `themes/_hl.py:ansi()` does this.

## Rules

- **Support both variants.** Dark and light ship together; follow the app's own dark/light switch where it has one.
- **No glow in ports without shadows.** Terminals and editors get the flat palette. Only web-like targets may use `dist/web/glow.css`, and never for anything that carries meaning.
- **Meaning without glow.** Selection must be a tint plus a solid marker and focus a solid outline.
- **Don't hard-code colours.** Everything comes from `pals`, so palette changes flow through.
- **Say what you tested.** State the app version and what you did and didn't check; untested claims don't belong in the docs.
- **Keep it self-contained.** A port should not need extra dependencies beyond the app itself.
- **Respect the licence.** If you adapt an existing theme's structure, credit it and keep its licence notice.

## Checklist for a pull request

- [ ] `python3 -I build.py` passes and `dist/` is committed
- [ ] Tested in the app, dark and light (version noted)
- [ ] Preview screenshot added
- [ ] README table and `CHANGELOG.md` updated
- [ ] No hard-coded colours outside the palette
