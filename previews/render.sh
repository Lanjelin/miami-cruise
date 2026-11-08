#!/bin/sh
# Re-render every theme screenshot from dist/. Each app owns previews/<app>/render.sh; this runs them all.
# Needs python3 and brave-browser (headless). Neovim shots also need NVIM=/path/to/nvim;
# eza shots need eza 0.23.5+ (or EZA=/path/to/eza) on Linux.
# bat/delta shots need compatible bat and delta (or BAT=... and DELTA=...).
# lazygit shots also need lazygit 0.66.3 and tmux (or LAZYGIT=...).
# fzf shots need fzf 0.75.0, bat and tmux (or FZF=... and BAT=...).
# btop shots need btop 1.4.8 and tmux on Linux (or BTOP=...).
# Run one app only:  ./previews/vim/render.sh
set -eu
cd "$(dirname "$0")/.."
for script in previews/*/render.sh; do
  echo "rendering $(basename "$(dirname "$script")")"
  sh "$script"
done
