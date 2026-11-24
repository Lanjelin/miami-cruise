#!/bin/sh
# Native GTK3/Pixbuf, Xvnc and Python GI required; no live desktop changes.
set -eu
cd "$(dirname "$0")/../.."
/usr/bin/python3 previews/icons/render.py
