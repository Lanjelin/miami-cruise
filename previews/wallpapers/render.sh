#!/bin/sh
# Thumbnail the approved fixed PNGs; never generates or modifies the artwork.
set -eu
cd "$(dirname "$0")/../.."
for variant in dark light; do
  magick "wallpapers/miami-coast-$variant-4k.png" -filter Lanczos -resize 960x540 -strip "previews/wallpapers/$variant.png"
  cp "previews/wallpapers/$variant.png" "website/previews/wallpapers/$variant.png"
done
