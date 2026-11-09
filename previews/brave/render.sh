#!/bin/sh
set -eu
cd "$(dirname "$0")/../.."
python3 -I previews/brave/render.py
