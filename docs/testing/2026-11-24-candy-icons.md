# Candy-derived icon pack: Arch/XFCE review

Date: 2026-11-24. Tested the uncommitted Candy icon integration against upstream
Candy commit `750fe2ca7909a721179ec34336042b15808d8ab9`.

## Environment and isolation

Arch Linux; GTK 3.24.52, xfdesktop 4.20.2, xfce4-panel 4.20.8,
Thunar 4.20.10 and Xfwm4 4.20.0. Both Miami Cruise GTK/Xfwm and Candy icon
variants were loaded in real XFCE processes on a private Xvnc display, separate
session bus, temporary home and isolated XDG directories. Only synthetic fixtures
were used. No live user theme, icon selection or installed files were changed.
Thumbnail generation was disabled for the file-icon inspection.

## Reviewed

- Dark and Light desktop file/folder icons and 32px launcher-panel artwork.
- Actual Applications menu and desktop context menu icons, including system
  fallbacks where Candy does not supply an action icon.
- Thunar folder, application launcher, text, Markdown, Python and PDF artwork.
- Single-file selection, all-files selection and the native GTK selection tint.
- Real view zoom from 38% to 200%, driven by keyboard shortcuts. The resulting
  saved zoom levels were checked: changing a saved default alone does not zoom
  an already-open Thunar view.
- Native session lookup confirms representative icons come from the selected
  Candy-derived pack, rather than silently falling back to another theme.

The native frames were visually inspected. Both variants are coherent and
readable at the tested sizes. The one refinement from this pass is darker
palette-derived strokes for Light's small places/folder artwork; larger filled
folders and Dark remain unchanged. Light was rechecked after that refinement.

## Reproduction

```sh
python3 -I build.py icons
/usr/bin/python3 previews/icons/desktop.py
# Repeat only a changed variant:
/usr/bin/python3 previews/icons/desktop.py --mode light
sh previews/icons/render.sh
python3 tests/icons.py
```

The desktop script captures diagnostics to ignored `previews/icons/review/`.
They are review evidence, not automatically published screenshots. The regular
public galleries contain only synthetic labels and icon artwork.
`render.sh` also decodes all generated SVGs and checks all 3,780 discoverable
SVG names per variant, with representative loading at 16–128px. The archive test
checks 3,860 paths per pack, original shape preservation, all 2,708 aliases,
unchanged embedded bitmaps, provenance, safe archives and offline source rebuild.

## Limits

This is real desktop-process testing in an isolated display, not a test of every
application's own UI or every icon's meaning. No physical HiDPI display, mixed-DPI,
other desktop environment or user-installed theme conflict testing was done.
Some apps ignore icon themes. Four embedded bitmap images retain their original
colours. Missing Candy names use installed system fallbacks; fallback styling can
vary between systems. Desktop selection tint is applied by GTK, independently
of the underlying SVG paint. Personal desktop approval is still pending.
