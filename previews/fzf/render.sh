#!/bin/sh
# FZF=/path/to/fzf BAT=/path/to/bat sh previews/fzf/render.sh
set -eu
cd "$(dirname "$0")/../.." && . previews/lib.sh
python3 -I previews/fzf/render.py "$tmp/palette.html"
shot 1120,1240 previews/fzf/palette.png "$tmp/palette.html" section dark light
