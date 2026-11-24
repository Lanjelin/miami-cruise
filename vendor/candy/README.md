# Candy artwork and licensing

Original artwork: [Candy icons](https://github.com/EliverLara/candy-icons),
by EliverLara and contributors, distributed under **GPL-3.0**.
The complete licence is in [LICENSE](LICENSE). See [upstream.json](upstream.json)
for the pinned commit, official archive URL and SHA-256 checksum.
`upstream.tar.gz` preserves the original source and its notices unmodified.

Miami Cruise modifies SVG paint, gradient endpoints, neutral colours and theme
metadata. Drawing geometry and embedded bitmap artwork are preserved; editor
metadata is removed from installable files. Original aliases are materialised as
regular SVG files so installation archives do not need symlink extraction.
The adapted artwork remains GPL-3.0, separate from this collection’s MIT files.
The source download includes the original archive, palette and generator and
rebuilds both packs without network access or third-party Python modules.

All 3,860 icon names (1,152 distinct source SVGs and 2,708 aliases) are included.
Four icons contain embedded bitmap images: itch, multimedia-audio-player,
net.retrodeck.retrodeck and orcaslicer. Those images retain their original colours.
Dark uses palette-token endpoints; Light adds a restrained palette-ink blend for
readable strokes. Gradients/transparency introduce intermediate shades. This is an
icon-specific treatment, not a change to the shared flat palette specification.
Application identities remain recognisable. Marks belong to their owners;
inclusion does not imply endorsement. Any original artwork notices are retained
in the unmodified source archive.
