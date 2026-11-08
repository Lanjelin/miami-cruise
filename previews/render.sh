#!/bin/sh
# Re-render the screenshots from dist/. Needs python3 and brave-browser (headless).
# Neovim shots also need a Neovim binary: NVIM=/path/to/nvim ./previews/render.sh
# Vim shots use `vim` from PATH (skipped if absent).
set -eu
cd "$(dirname "$0")/.."
tmp=$(mktemp -d)
shot() { brave-browser --headless=new --no-sandbox --disable-gpu --hide-scrollbars --default-background-color=00000000 --window-size="$1" --screenshot="$2" "file://$3" >/dev/null 2>&1; }

python3 -I previews/web/mock.py "$tmp/web.html"
shot 1500,345 previews/web/palette.png "$tmp/web.html"

python3 -I previews/wezterm/mock.py "$tmp/wezterm.html"
shot 1100,330 previews/wezterm/palette.png "$tmp/wezterm.html"

if [ -n "${NVIM:-}" ]; then
  for bg in dark light; do
    "$NVIM" --clean --headless previews/nvim/sample.lua \
      -c "packadd nvim.tohtml" -c "set rtp^=dist/nvim" -c "set background=$bg" \
      -c "colorscheme miami-cruise" -c "lua vim.treesitter.start()" \
      -c "TOhtml" -c "write! $tmp/nvim-$bg.html" -c "qa!" >/dev/null 2>&1
    shot 640,470 "previews/nvim/$bg.png" "$tmp/nvim-$bg.html"
  done
fi

if command -v vim >/dev/null 2>&1; then
  for bg in dark light; do
    vim -u NONE -N -es previews/vim/sample.py \
      -c "set rtp^=$PWD/dist/vim" -c "syntax on" -c "set termguicolors background=$bg" \
      -c "colorscheme miami-cruise" -c "let g:html_no_progress=1" -c "runtime syntax/2html.vim" \
      -c "write! $tmp/vim-$bg.html" -c "qa!" </dev/null >/dev/null 2>&1
    shot 640,560 "previews/vim/$bg.png" "$tmp/vim-$bg.html"
  done
fi

rm -rf "$tmp"
