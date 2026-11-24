# Agent playbook: optional wallpapers

Follow [INSTALL.md](../../INSTALL.md) and the
[user guide](../../dist/wallpapers/README.md). Download selected PNGs directly
from the website or a pinned revision. These are optional image files, not an
application, theme dependency or automatic part of XFCE installation.

## Inspect and propose

Ask which image the user wants, where to save it, and whether they want file-only
preparation or live selection. Detect the real Pictures path, destination files,
symlinks and managed configuration without modifying them. On XFCE, identify the
requesting display/session and the precise monitor/workspace backdrop properties.
If the session or property mapping is unclear, use manual Desktop Settings handoff;
never guess a session bus or apply a wildcard across all monitors/workspaces.

Record existing image path, image-style, colour settings and any cycling or
shared-workspace behaviour affecting the specific target. Explain potential
cropping on non-16:9 displays. Do not enable or disable cycling, change wallpaper
selection scope or overwrite earlier images without including it in the proposal.
Do not copy the user's old wallpaper into public assets or share a real desktop
screenshot. Never rewrite XFConf XML directly.

Present exact download URL(s), destination(s), backup scope and selection changes.
Wait for explicit approval before target writes, including backups. Under the
shared restore procedure, create the manifest, backups, manual instructions and
guarded restore script before installation writes. File-only approval does not
authorize desktop selection. Wallpaper selection requires specific approval.

## Apply, verify and restore

Download only chosen PNGs into approved persistent paths; verify supplied
checksums, valid PNG decoding and 3840 × 2160 dimensions. Preserve pre-existing
same-named files and symlink targets. No model, Python environment, image generator
or package installation is needed. Record all installation-owned files.

Default to manual Desktop Settings → Background. If selection is approved, change
only the recorded properties for the intended monitor/workspace and verify them
by reading back. Do not change GTK themes, icons, fonts, panel layout or other
appearance settings. Check the resulting crop and readability; property readback
alone is not proof of rendering.

For restoration, check that affected properties still match the installed values.
Stop on later edits. Restore original property values/types or original absence,
then remove only unchanged installation-owned PNGs or restore overwritten files.
Preserve conflicts, unrelated displays/workspaces and the restore record.
RESTORE.md must list the original image and scaling/scope settings and give the
manual route through Desktop Settings. Switch away before removing an active PNG.
