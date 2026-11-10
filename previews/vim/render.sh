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
  # :TOhtml substitutes black/white for an unset Normal background. Simulate
  # the matching terminal background around the real Vim highlight output.
  python3 -I - "$tmp/vim-$bg.html" "$bg" <<'PY'
import json
from pathlib import Path
import sys

path = Path(sys.argv[1])
bg = json.loads(Path('dist/tokens/tokens.json').read_text())[sys.argv[2]]['bg']
page = path.read_text().replace('</style>', f'body, pre {{ background-color: {bg} !important; }}\n</style>')
path.write_text(page)
PY
  shot 640,560 "previews/vim/$bg.png" "$tmp/vim-$bg.html"
done
