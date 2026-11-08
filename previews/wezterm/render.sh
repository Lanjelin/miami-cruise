#!/bin/sh
# WezTerm preview: an HTML mock-up of a window, drawn from the same code the theme uses.
set -eu
cd "$(dirname "$0")/../.." && . previews/lib.sh
python3 -I previews/wezterm/mock.py "$tmp/wezterm.html"
shot 1100,330 previews/wezterm/palette.png "$tmp/wezterm.html"
