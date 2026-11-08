<h3 align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="brand/banner-dark.png">
    <img src="brand/banner-light.png" alt="Miami Cruise: teal-ink neutrals, one magenta hero" width="100%">
  </picture>
</h3>

<p align="center">
  <img alt="Licence: MIT" src="https://img.shields.io/badge/licence-MIT-ff7fc0?labelColor=0d1d22">
  <img alt="Version 0.1.0" src="https://img.shields.io/badge/version-0.1.0-70d5ed?labelColor=0d1d22">
  <img alt="Text contrast at least 4.5:1" src="https://img.shields.io/badge/text%20contrast-%E2%89%A54.5%3A1-5ed99e?labelColor=0d1d22">
</p>

<p align="center">
  <a href="https://lanjelin.github.io/miami-cruise"><b>Website</b></a> &nbsp;·&nbsp;
  <a href="#install">Install</a> &nbsp;·&nbsp;
  <a href="docs/PORTING.md">Port to your app</a> &nbsp;·&nbsp;
  <a href="CONTRIBUTING.md">Contribute</a>
</p>

<p align="center">
  A dark and light colour scheme for your editor, terminal and web, with <b>teal-ink neutrals</b> and a <b>single magenta hero accent</b>.<br>
  Inspired by 80s night drives, tuned for long days in front of a screen.
</p>

<table>
  <tr>
    <td><img src="previews/nvim/dark.png" alt="Neovim, dark"></td>
    <td><img src="previews/nvim/light.png" alt="Neovim, light"></td>
  </tr>
</table>

## Why Miami Cruise

- **One hero.** Magenta is the only loud colour. It marks keywords, selection, focus and links. Everything else stays calm, so what matters stands out.
- **Dark and light, same identity.** Both variants share one tinted hue family and ship together.
- **Readable by construction.** The palette is defined in [OKLCH](https://oklch.com), and the build adjusts every text and accent colour until it reaches at least 4.5:1 contrast against the background. It fails if it can't.
- **Meaning without glow.** Selection is a tint plus a solid stripe, and focus is a solid outline. The optional glow layer only decorates them, so ports without shadows lose nothing.
- **One source.** Every port is generated from the same palette, so they never drift apart.

## Palette

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="dist/brand/palette-dark.svg">
  <img src="dist/brand/palette-light.svg" alt="Miami Cruise palette" width="100%">
</picture>

The light and dark palettes, with the full specification and contrast ratios, are in [docs/SPEC.md](docs/SPEC.md).

## Supported apps

| App | Files | Status |
|---|---|---|
| [Neovim](#neovim) | [`dist/nvim/colors/miami-cruise.lua`](dist/nvim/colors/miami-cruise.lua) | Stable. Tested on Neovim 0.12 with Treesitter |
| [Vim](#vim) | [`dist/vim/colors/miami-cruise.vim`](dist/vim/colors/miami-cruise.vim) | Stable. Tested on Vim 9.1 |
| [WezTerm](#wezterm) | [`dist/wezterm/miami-cruise.lua`](dist/wezterm/miami-cruise.lua) | Beta. Logic and colour fields checked; not yet run in the app on every platform |
| [Web / CSS](#web--css) | [`dist/web/`](dist/web) | Stable. This project's own website is built on it |
| [Any other app](#design-tokens) | [`dist/tokens/tokens.json`](dist/tokens/tokens.json) | Design tokens as JSON |

Your app isn't listed? [Request a port](../../issues/new/choose) or [write one](docs/PORTING.md); a port is a single small file.

## Install

Every theme is a ready-to-use file in [`dist/`](dist). Copy it into place; there is nothing to build. The [website](https://lanjelin.github.io/miami-cruise) offers the same files with step-by-step guides for macOS, Linux and Windows, and the source of the site is in [`website/`](website).

### Neovim

```sh
mkdir -p ~/.config/nvim/colors
cp dist/nvim/colors/miami-cruise.lua ~/.config/nvim/colors/
```

```lua
vim.o.background = "dark" -- or "light"
vim.cmd.colorscheme("miami-cruise")
```

The theme follows `'background'`: `:set background=light` switches it live. On Windows the folder is `%LOCALAPPDATA%\nvim\colors`.

### Vim

```sh
mkdir -p ~/.vim/colors
cp dist/vim/colors/miami-cruise.vim ~/.vim/colors/
```

```vim
syntax on
set background=dark   " or light
colorscheme miami-cruise
```

True colour is used when `$COLORTERM` is `truecolor` or `24bit`; otherwise Vim falls back to the nearest of the 256 colours. On Windows the folder is `~\vimfiles\colors`.

### WezTerm

Copy `dist/wezterm/miami-cruise.lua` next to your `wezterm.lua` (`~/.config/wezterm/`), then add:

```lua
package.path = wezterm.config_dir .. "/?.lua;" .. package.path
require("miami-cruise").apply(config)
```

It follows the system dark/light setting, and WezTerm reloads the config when that changes. To force a variant, set `MIAMI_CRUISE=dark` or `light` (`auto` returns to the system) in the environment WezTerm starts from, for example `MIAMI_CRUISE=light wezterm`, or pin it in the config with `apply(config, { mode = "light" })`. Apps launched from the Dock or Start menu don't see shell variables, so pin the mode in the config there.

### Web / CSS

```html
<link rel="stylesheet" href="miami-cruise.css">
<link rel="stylesheet" href="glow.css"> <!-- optional -->
```

```css
body { background: var(--mc-bg); color: var(--mc-text); }
a    { color: var(--mc-accent); }
```

Dark is the default; set `data-theme="light"` on `<html>` for the light variant.

### Design tokens

`dist/tokens/tokens.json` has a `dark` and a `light` object mapping each token to a hex colour; `contrast.json` lists the contrast ratios. Use it to port the palette to anything else. The role of each token is described in the [porting guide](docs/PORTING.md#token-roles).

## Repository

```
dist/          the themes, generated from the palette and committed
themes/        one small module per app
palette.py     the palette: OKLCH values and contrast rules
website/       the source of the project website, built separately
brand/         logo, banner and social-preview sources
docs/          specification and porting guide
previews/      screenshots and the samples they come from
```

To rebuild after changing the palette or a port: `python3 -I build.py` (Python 3, no dependencies). The files in `dist/` are generated, so CI fails if they are out of date.

## Contributing

Contributions are welcome: bug reports, ports to new apps, and fixes. Read [CONTRIBUTING.md](CONTRIBUTING.md) and the [porting guide](docs/PORTING.md), and please follow the [code of conduct](CODE_OF_CONDUCT.md). Changes to the palette affect every port, so open an issue to discuss them first.

## Licence

[MIT](LICENSE). Free to use, change and share.
