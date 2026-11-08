#!/bin/sh
# Web / CSS preview: an HTML mock-up drawn from the tokens.
set -eu
cd "$(dirname "$0")/../.." && . previews/lib.sh
python3 -I previews/web/mock.py "$tmp/web.html"
shot 1500,345 previews/web/palette.png "$tmp/web.html"
