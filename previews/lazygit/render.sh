#!/bin/sh
# LAZYGIT=/path/to/lazygit BAT=/path/to/bat DELTA=/path/to/delta sh previews/lazygit/render.sh
# Uses an isolated tmux server and disposable Git/config/cache directories.
set -eu
cd "$(dirname "$0")/../.." && . previews/lib.sh
python3 -I previews/lazygit/render.py "$tmp"
shot 1280,1460 previews/lazygit/palette.png "$tmp/palette.html"
shot 1280,1460 previews/lazygit/delta.png "$tmp/delta.html"
