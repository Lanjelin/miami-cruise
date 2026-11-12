#!/bin/sh
# Real Zsh prompts in disposable homes/repos; Oh My Zsh is optional.
set -eu
cd "$(dirname "$0")/../.." && . previews/lib.sh
python3 -I previews/zsh/render.py "$tmp/zsh.html"
shot 1120,450 previews/zsh/palette.png "$tmp/zsh.html" section dark light
