#!/bin/sh
# Offline illustrative UI; native theme colours, synthetic content only.
set -eu
cd "$(dirname "$0")/../.." && . previews/lib.sh
python3 -I previews/openclaw/render.py "$tmp/openclaw.html"
shot 2460,820 previews/openclaw/palette.png "$tmp/openclaw.html" .preview dark light
