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
  # :TOhtml substitutes black/white for an unset Normal background. Simulate
  # the matching terminal background around the real Neovim highlight output.
  python3 -I - "$tmp/nvim-$bg.html" "$bg" <<'PY'
import json
from pathlib import Path
import sys

path = Path(sys.argv[1])
bg = json.loads(Path('dist/tokens/tokens.json').read_text())[sys.argv[2]]['bg']
page = path.read_text().replace('</style>', f'body, pre {{ background-color: {bg} !important; }}\n</style>')
path.write_text(page)
PY
  shot 640,470 "previews/nvim/$bg.png" "$tmp/nvim-$bg.html"
done
