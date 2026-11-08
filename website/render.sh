#!/bin/sh
# Re-render the website screenshots (used by the README) from website/dist/. Needs brave-browser.
set -eu
cd "$(dirname "$0")/.."
[ -f website/dist/index.html ] || { echo "build the website first: python3 -I build.py" >&2; exit 1; }
site="$PWD/website/dist"
shot() { brave-browser --headless=new --no-sandbox --disable-gpu --hide-scrollbars --window-size="$1" --screenshot="$2" "$3" >/dev/null 2>&1; }
shot 1200,900 website/previews/home-dark.png "file://$site/index.html?theme=dark"
shot 1200,900 website/previews/home-light.png "file://$site/index.html?theme=light"
