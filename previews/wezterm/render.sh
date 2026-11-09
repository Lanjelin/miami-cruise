#!/bin/sh
# Import screenshots from the real desktop app; never substitute a mock-up.
# Capture the same window in both variants, without private shell output.
# Crop to the terminal UI, keeping tabs and splits but excluding desktop panels,
# window-manager title bars and desktop overlays before importing.
# Usage: render.sh /absolute/path/to/dark.png /absolute/path/to/light.png
set -eu
cd "$(dirname "$0")/../.."
if [ "$#" -eq 0 ]; then
  test -s previews/wezterm/dark.png && test -s previews/wezterm/light.png
  echo 'WezTerm: retaining verified desktop captures (pass dark.png light.png to replace).'
  exit 0
fi
test "$#" -eq 2
cp "$1" previews/wezterm/dark.png
cp "$2" previews/wezterm/light.png
