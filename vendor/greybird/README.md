# Greybird base for the Miami Cruise desktop theme

Upstream: https://github.com/shimmerproject/Greybird
Pinned revision: 7e4507d7713b2aaf41f8cfef2a1a9e214a4d8b6f
Copyright 2009–2019 Simon Steinbeiß, Satyajit Sahoo, Pasi Lallinaho,
Carson Black, Maurizio Galli; additional contributor notices remain in source files.

Greybird is dual-licensed GPL-2.0-or-later / CC-BY-SA-3.0-or-later.
Miami Cruise distributes this derivative under GPL-2.0-or-later. The desktop
packages and this vendored base are NOT covered by the root MIT licence.
Both upstream licence texts and copyright notices are retained.

The snapshot retains light/gtk-3.0 sources and assets, plus light/xfwm4 artwork.
base-light.css and base-dark.css are unmodified SCSS compilations with libsass
0.23.0, expanded output (gtk-contained.scss / gtk-contained-dark.scss).
These precompiled bases keep the normal Python build dependency-free and offline.
To refresh them, use an isolated maintainer environment with libsass and run
`sass.compile(filename=..., output_style="expanded")` for both entry points.
Never install a Sass compiler or modify host configuration as part of a normal build.

Miami Cruise modifications (2026): palette-derived neutral/semantic colour mapping,
recoloured PNG/SVG/XPM artwork, explicit selection/focus/readability overrides,
fixed-variant CSS, theme metadata and reproducible packaging. Widget geometry and
states remain based on Greybird. Mapping logic is in themes/xfce.py and
PNG decoding/re-encoding in themes/_xfce_assets.py in the matching source archive (available beside the theme downloads) and the Miami Cruise source:
https://github.com/Lanjelin/miami-cruise

The complete corresponding source consists of this snapshot and those generator
files, shipped in the source repository. No upstream software is downloaded by
the normal build. GTK2 and non-XFCE window-manager components are not included.

To rebuild the supplied corresponding-source archive, extract it and run
`python3 -I build.py` inside its directory. This uses the precompiled upstream
bases and requires only Python 3; no installed theme is changed.

SVG editor export-path metadata was removed from this snapshot; rendering data
and copyright/licence metadata are unchanged. Missing upstream high-DPI and
handle assets are resolved to existing artwork or native CSS by the generator.

The derivative additionally replaces the blanket unfocused Thunar dimming rule
with semantic foregrounds, pins public unfocused colour aliases, and supplies
explicit desktop, panel, menu, tooltip, tab and control-state colours.

The derivative uses original dependency-free, antialiased Xfwm4 button symbols
in place of the shaded upstream button artwork, retaining native tile dimensions
and all supported button functions. It also provides restrained panel styling,
flat external plugin wrappers and translucent desktop drag-selection overlays.
