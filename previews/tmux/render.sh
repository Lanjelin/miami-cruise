#!/bin/sh
# Real attached tmux client, in two isolated servers; no personal sessions used.
set -eu
cd "$(dirname "$0")/../.." && . previews/lib.sh
python3 -I previews/tmux/render.py "$tmp/palette.html"
shot 1080,886 previews/tmux/palette.png "$tmp/palette.html"
