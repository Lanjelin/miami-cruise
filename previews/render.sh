#!/bin/sh
# Re-render every theme screenshot from dist/. Each app owns previews/<app>/render.sh; this runs them all.
# Needs Python 3, Node 22+ and headless Chromium (BRAVE=... or brave-origin). Neovim shots also need NVIM=/path/to/nvim;
# eza shots need eza 0.23.5+ (or EZA=/path/to/eza) on Linux.
# bat/delta shots need compatible bat and delta (or BAT=... and DELTA=...).
# lazygit shots also need lazygit 0.66.3 and tmux (or LAZYGIT=...).
# fzf shots need fzf 0.75.0, bat and tmux (or FZF=... and BAT=...).
# btop shots need btop 1.4.8 and tmux on Linux (or BTOP=...).
# Yazi shots need Yazi 26.9.1 and tmux (or YAZI=/path/to/yazi).
# Merged contact sheets remain available; galleries use individual dark/light panels.
# Optional CDP_URL=http://127.0.0.1:PORT reuses an existing headless browser.
# Run one app only:  ./previews/vim/render.sh
set -eu
cd "$(dirname "$0")/.."
for script in previews/*/render.sh; do
  echo "rendering $(basename "$(dirname "$script")")"
  sh "$script"
done
