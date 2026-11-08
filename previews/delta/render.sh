#!/bin/sh
# Needs compatible bat and delta; set BAT and DELTA to executable paths if needed.
set -eu
cd "$(dirname "$0")/../.." && . previews/lib.sh
python3 -I previews/_syntax.py delta "$tmp/delta.html"
shot 1200,1200 previews/delta/palette.png "$tmp/delta.html"
