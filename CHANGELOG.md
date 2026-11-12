# Changelog

All notable changes to this project are documented here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project uses [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Fixed
- Ignore stale Python venv metadata when its bin directory is missing or no longer on PATH; valid inherited environments remain visible without a deactivate function.

### Changed
- Use uniform screenshot preview sizes on app pages, with an accessible click-to-zoom viewer and original-image fallback.
- Simplify website reading and installation layouts: stronger body text, roomier steps, quieter inline code and expandable secondary download/testing details.
- Prefer an active Python venv's `VIRTUAL_ENV_PROMPT` display name, falling back to its directory name.
- Move the native Python/Conda environment segment to the leftmost position in the Zsh right prompt.
- Enable the Zsh read-only-directory marker by default; set `MIAMI_CRUISE_SHOW_READ_ONLY=0` to opt out.

### Added
- Nerd Font icons for Zsh Python environments, command duration and nested shell/Yazi levels; ASCII mode retains text-only labels.
- Vi-mode indicators use the prompt arrow by default; ASCII mode alone uses right-side text labels.
- Zsh same-directory transient prompts and optional rightmost submission timestamps; read-only indicators now use a lock immediately before the path, with an ASCII fallback.
- Dependency-free opt-in Zsh pipeline/signal status, Git operation/progress labels, smart SSH/root context, read-only-directory and nested-shell/Yazi indicators, and ASCII theme symbols; defaults preserve the existing prompt.
- Zsh `MIAMI_CRUISE_SHOW_RETURN_CODE` flag to hide failed-command return codes; enabled by default.
- Configurable Zsh command duration (3-second default threshold), running/suspended job counts, opt-in vi-mode labels, native Python/Conda environments and asynchronous Git refresh with directory-safe results; existing widgets and layout/transient modes preserved.
- Independent Zsh flags for single-line layout and transient prompts, preserving the existing two-line persistent default.
- Dark/light Oh My Zsh prompt themes with palette-driven colours, adaptive path shortening, and Git branch, ahead/behind, staged, unstaged and untracked counts.
- Native dark/light Brave browser-chrome themes as local-install ZIPs, with a site download page and unpacked-extension instructions; Web Store publishing remains optional.
- Native Glow/Glamour dark/light Markdown styles with palette backgrounds, shared-palette code syntax, install instructions and real rendered-output previews; browser/pager chrome remains unchanged.
- Colour-only native tmux dark/light files, preserving existing status/powerline formats, bindings and layout, with layered install instructions and isolated real-client previews.
- Native btop dark/light themes with a shared-palette dashboard, install guide and live-app previews.
- Native fzf dark/light colour option files, preserving existing picker behaviour, with shell instructions and real interactive previews.
- Native lazygit GUI themes with automatic/fixed dark and light variants, layered install instructions and real UI/delta previews.
- Dark/light bat syntax themes and delta diff themes, sharing one TextMate mapping, with install guides and previews captured from real app output.
- Clear type-badge fallbacks (`eza`, `CSS`, `{}`), with palette-aware accents and short initial-based defaults for long app names.
- Text badges for Neovim (`nvim`), Vim (`vim`), WezTerm (`wez`) and lazygit (`lzg`), with original artwork retained in the credits/licences page.
- Generated eza themes in dark and light, with shared install guides and a preview captured from real eza output.

### Fixed
- Let Vim/Neovim editor surfaces, delta's ordinary diff lines, fzf and eza inherit the terminal background; retain deliberate selection/panel fills and an opt-in opaque editor background. Recommend btop's native background toggle for the same effect.
- Verify WezTerm on Linux/X11, fix fancy/retro tab colours and window-frame colours, replace mock previews with live captures, and document existing-config overrides and Linux appearance-portal requirements.
- Clarify delta's native Git-config theme versus its supporting TextMate syntax palettes; put delta setup first in its README and website guide.

## [0.1.0]

First release.

### Added
- The Miami Cruise palette: 17 tokens in dark and light, defined in OKLCH, with a checked minimum contrast for every text and accent colour.
- Themes for Neovim, Vim and WezTerm (WezTerm follows the system dark/light setting and can be overridden), CSS variables with an optional glow layer, and the tokens as JSON.
- A static website with a page and install guide for each app, downloads with checksums, and a palette page.
- Logo, mark and README/social-preview images generated from the palette.
- A porting guide and a generated specification in `docs/`.
