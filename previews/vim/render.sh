#!/bin/sh
# Vim preview: renders previews/vim/sample.py with the theme via :TOhtml. Uses `vim` from PATH.
set -eu
cd "$(dirname "$0")/../.." && . previews/lib.sh
if ! command -v vim >/dev/null 2>&1; then echo "vim: skipped (vim not found)"; exit 0; fi
for bg in dark light; do
  vim -u NONE -N -es previews/vim/sample.py \
    -c "set rtp^=$PWD/dist/vim" -c "syntax on" -c "set termguicolors background=$bg" \
    -c "colorscheme miami-cruise" -c "let g:html_no_progress=1" -c "runtime syntax/2html.vim" \
    -c "write! $tmp/vim-$bg.html" -c "qa!" </dev/null >/dev/null 2>&1
  shot 640,560 "previews/vim/$bg.png" "$tmp/vim-$bg.html"
done
