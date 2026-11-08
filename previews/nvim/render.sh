#!/bin/sh
# Neovim preview: renders previews/nvim/sample.lua with the theme via :TOhtml. Needs NVIM=/path/to/nvim.
set -eu
cd "$(dirname "$0")/../.." && . previews/lib.sh
if [ -z "${NVIM:-}" ]; then echo "nvim: skipped (set NVIM=/path/to/nvim)"; exit 0; fi
for bg in dark light; do
  "$NVIM" --clean --headless previews/nvim/sample.lua \
    -c "packadd nvim.tohtml" -c "set rtp^=dist/nvim" -c "set background=$bg" \
    -c "colorscheme miami-cruise" -c "lua vim.treesitter.start()" \
    -c "TOhtml" -c "write! $tmp/nvim-$bg.html" -c "qa!" >/dev/null 2>&1
  shot 640,470 "previews/nvim/$bg.png" "$tmp/nvim-$bg.html"
done
