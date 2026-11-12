#!/bin/sh
# GLOW=/path/to/glow sh previews/glow/render.sh
set -eu
cd "$(dirname "$0")/../.." && . previews/lib.sh
python3 -I previews/glow/render.py "$tmp/palette.html"
shot 1200,1080 previews/glow/palette.png "$tmp/palette.html" section dark light
