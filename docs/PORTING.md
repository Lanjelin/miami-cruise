# Porting guide

How to add Miami Cruise to another app. A port is one small Python module that turns the shared palette into that app's format, so every port stays in step with the palette automatically.

Before you start, read [SPEC.md](SPEC.md) for the tokens and the principles. Open an issue first if you plan a large port, so work isn't duplicated.

## What a port is

A port is one Python module in `themes/`. It turns the shared palette into the app's format and carries the app's install guide, so adding an app means adding one file; nothing needs registering.

```
themes/<app>.py       export(pals, dist) writes the theme to dist/<app>/, and GUIDE describes the app
dist/<app>/...        the generated theme and its README (from GUIDE), committed
previews/<app>/       a sample file, a render.sh and the screenshots
```

`pals` maps `"dark"` and `"light"` to `(tokens, meta)`. `tokens` is a dict from token name (`bg`, `accent`, `danger`, ...) to a `#rrggbb` string. Use only these values; never hard-code a colour in a port.

`GUIDE` holds the app's name, tagline, files, screenshots, install steps (for macOS, Linux and Windows), what you tested, and its `category`, `tags`, `aliases` and `status`. The build renders it into `dist/<app>/README.md`, the website page and the README apps table. See `themes/wezterm.py` for a full example.

## Steps

1. **Write the module** `themes/<app>.py`, with `export(pals, dist)` and `GUIDE`. Copy the nearest existing port: `themes/wezterm.py` (a config module) or `themes/vim.py` (a colorscheme). `themes/_hl.py` has highlight groups shared by Vim and Neovim.
   `themes/_textmate.py` maps syntax scopes once for bat and delta; delta adds native Git-config features. Delta's native custom-syntax installation needs bat to build the shared cache, but not at runtime. Both ports ship the same generated syntax files, so installing either set suffices.
2. **Map the tokens** using the table below.
3. **Build and test it in the real app**, dark and light. Write down the version you tested in `GUIDE["tested"]`.
4. **Add a preview**: `previews/<app>/` with a short sample file, a `render.sh` (copy `previews/vim/render.sh`) and the screenshots.
5. **Run `python3 -I build.py`** and commit what it generated: `dist/`, `docs/SPEC.md` and the README apps table. CI fails if they are out of date.
6. **Update `CHANGELOG.md`** under `[Unreleased]`.

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

- [ ] `python3 -I build.py` passes and the generated files are committed
- [ ] Tested in the app, dark and light (version noted)
- [ ] `GUIDE` written, with install steps for macOS, Linux and Windows
- [ ] Preview screenshot added
- [ ] `CHANGELOG.md` updated
- [ ] No hard-coded colours outside the palette

## Hand-written ports

You don't have to use the generator. If an app is better served by a theme written in its own idiom, or you'd rather keep it in your own repository, that's welcome too:

1. Build the theme from `dist/tokens/tokens.json` (see [Token roles](#token-roles)) in your own repo, with the same dark and light variants.
2. Keep the colours in step with the palette. Don't pick new ones.
3. Open a [port request](../../../issues/new?template=port_request.yml) with a link to your repository.

Accepted ports are listed in the README under a "Community ports" heading with a link to the repository. We won't copy them into `dist/`, since that folder is generated. If a hand-written port turns out to be popular, it can be moved into a generated exporter later.
