#!/bin/sh
# Real Oh My Zsh prompts in disposable homes and Git repositories.
set -eu
cd "$(dirname "$0")/../.." && . previews/lib.sh
python3 -I previews/zsh/render.py "$tmp/zsh.html"
shot 1120,450 previews/zsh/palette.png "$tmp/zsh.html"
