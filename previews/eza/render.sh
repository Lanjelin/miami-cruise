#!/bin/sh
# Real eza output rendered on the matching terminal backgrounds. Needs eza 0.23.5+.
# EZA=/path/to/eza sh previews/eza/render.sh
set -eu
cd "$(dirname "$0")/../.." && . previews/lib.sh
python3 -I previews/eza/render.py "$tmp/eza.html"
shot 1200,780 previews/eza/palette.png "$tmp/eza.html" section dark light
