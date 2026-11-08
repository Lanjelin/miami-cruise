# Changelog

All notable changes to this project are documented here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project uses [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- Dark/light bat syntax themes and delta diff themes, sharing one TextMate mapping, with install guides and previews captured from real app output.
- Clear type-badge fallbacks (`eza`, `CSS`, `{}`), with palette-aware accents and short initial-based defaults for long app names.
- Original Neovim, Vim and WezTerm icons on website cards and app pages, with uniform tiles, text fallbacks and a generated credits/licences page.
- Generated eza themes in dark and light, with shared install guides and a preview captured from real eza output.

## [0.1.0]

First release.

### Added
- The Miami Cruise palette: 17 tokens in dark and light, defined in OKLCH, with a checked minimum contrast for every text and accent colour.
- Themes for Neovim, Vim and WezTerm (WezTerm follows the system dark/light setting and can be overridden), CSS variables with an optional glow layer, and the tokens as JSON.
- A static website with a page and install guide for each app, downloads with checksums, and a palette page.
- Logo, mark and README/social-preview images generated from the palette.
- A porting guide and a generated specification in `docs/`.
