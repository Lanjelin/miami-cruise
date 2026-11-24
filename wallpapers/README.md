# Miami Coast wallpapers

Approved dark/light **3840 × 2160** PNG assets for Miami Cruise. These exact files
are the source of the website and `dist/wallpapers/` downloads. They are copied
byte-for-byte during builds, never regenerated. Offered under the collection’s
[MIT licence](../LICENSE).

The artwork was created with the built-in image generation tool using Miami
Cruise palette anchors, then enhanced with Real-ESRGAN’s illustration-oriented
`realesr-animevideov3` model. Learned 4× outputs were downsampled to exact 4K.
Some texture was simplified and fine edges inferred. These are AI-generated,
super-resolution-upscaled images, not native-resolution photographs or exact
flat-palette renders. Both final images were visually approved by the user.

[provenance.json](provenance.json) records asset checksums, model provenance and
processing. [prompts.json](prompts.json) preserves the generation prompts as
background information, not a reproducible build step. The Dark image was the
composition reference for Light. Models, virtual environments, processing caches,
private paths and desktop screenshots are not shipped.

The build needs only Python’s standard library. To refresh the small public
previews from these fixed assets, run `sh previews/wallpapers/render.sh`
(ImageMagick required only for that optional preview task). Validate with
`python3 tests/wallpapers.py` after a full build.

Installation is optional and does not accompany desktop-theme selection
automatically. See the [user guide](../dist/wallpapers/README.md) and
[agent playbook](../docs/agent-install/wallpapers.md).
