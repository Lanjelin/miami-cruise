#!/bin/sh
# Native plugin capture; supply the plugin checkout path (see CONTRIBUTING.md).
set -eu
cd "$(dirname "$0")/../.." && . previews/lib.sh
python3 -I previews/airline/render.py "$tmp/preview.html"
shot 960,1050 previews/airline/palette.png "$tmp/preview.html" section dark light
