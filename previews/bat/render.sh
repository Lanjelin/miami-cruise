#!/bin/sh
# BAT=/path/to/bat sh previews/bat/render.sh
set -eu
cd "$(dirname "$0")/../.." && . previews/lib.sh
python3 -I previews/_syntax.py bat "$tmp/bat.html"
shot 1200,760 previews/bat/palette.png "$tmp/bat.html" section dark light
