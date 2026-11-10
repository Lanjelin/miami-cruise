#!/bin/sh
# Capture both real Yazi flavors with disposable config/data, using an isolated tmux server.
# YAZI=/path/to/yazi sh previews/yazi/render.sh
set -eu
cd "$(dirname "$0")/../.." && . previews/lib.sh
python3 -I previews/yazi/render.py "$tmp/yazi.html"
shot 1280,740 previews/yazi/palette.png "$tmp/yazi.html"
