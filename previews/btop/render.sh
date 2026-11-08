#!/bin/sh
# BTOP=/path/to/btop sh previews/btop/render.sh
set -eu
cd "$(dirname "$0")/../.." && . previews/lib.sh
python3 -I previews/btop/render.py "$tmp/palette.html"
shot 1200,1540 previews/btop/palette.png "$tmp/palette.html"
