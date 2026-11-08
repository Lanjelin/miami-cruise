#!/bin/sh
# Render the README banners and the GitHub social-preview image from dist/. Needs python3 and brave-browser.
# Upload brand/social-preview.png under Settings -> General -> Social preview once the repo is on GitHub.
set -eu
cd "$(dirname "$0")/.."
[ -f dist/brand/logo.svg ] || { echo "build first: python3 -I build.py" >&2; exit 1; }
tmp=$(mktemp -d)
shot() { brave-browser --headless=new --no-sandbox --disable-gpu --hide-scrollbars --default-background-color=00000000 --window-size="$1" --screenshot="$2" "file://$3" >/dev/null 2>&1; }
for kind in banner-dark banner-light social; do python3 -I brand/banner.py "$kind" "$tmp/$kind.html"; done
shot 1280,300 brand/banner-dark.png "$tmp/banner-dark.html"
shot 1280,300 brand/banner-light.png "$tmp/banner-light.html"
shot 1280,640 brand/social-preview.png "$tmp/social.html"
rm -rf "$tmp"
