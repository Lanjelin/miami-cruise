# Agent playbook: Candy-derived icons

Follow [INSTALL.md](../../INSTALL.md), the [human guide](../../dist/icons/README.md)
and [generator metadata](../../themes/icons.py). Read the site guide and download
only the selected archive(s).

## Read-only discovery

Identify the desktop/session and actual icon search paths: XDG_DATA_HOME/icons,
XDG_DATA_DIRS/icons and legacy ~/.icons. Resolve overrides, existing same-named
folders, symlinks and managed dotfiles before proposing targets. Do not assume the
user uses default paths. In XFCE, read `/Net/IconThemeName` with `xfconf-query -c
xsettings -p /Net/IconThemeName` in the verified requesting session; record value,
type or absence. Do not guess a session bus or edit XFConf XML directly. If no
session is available, offer file-only installation and manual selection.

Check whether `gtk-update-icon-cache` is available. Cache generation after installation
or updates is recommended, not a prerequisite for SVG loading. Explain any missing
utility and obtain separate approval before installing packages.

This is an independent icon setting, not a GTK/window-theme, cursor, font,
wallpaper or panel-layout change. Do not inventory the user's applications or
collect a real desktop screenshot for public examples. Uncovered names use system
fallback themes; do not install fallback packages without separate approval.

## Propose and apply

Offer Dark or Light, exact download URLs and target paths, conflicts, archive
contents, verification and restore plan. Distinguish approval to write files from
approval to change the live icon selection. Wait for explicit approval before any
installation writes, including backup creation, under the shared procedure.

Create the private restore record, manifest, verified backups and conflict-aware
restoration script **before** writing theme files. Preserve existing destination
folders, symlink targets/links, ownership and the prior selection or absent value.
Validate archive checksums when supplied and require only regular members under
the expected top-level theme directory; reject absolute paths, traversal, links,
special files and unexpected members. Install into the actual user icon path,
never into a shared base theme. The source archive is not an installable icon pack.

Include the exact `gtk-update-icon-cache -f` command for each installed theme in
the approved plan. Record any existing `icon-theme.cache` in backups and journal
the newly generated cache as installation-owned state. Run the tool only on the
approved target folders, not all system icon themes; verify successful generation
and validate the cache when the utility is available. File-only preparation must
not silently select a theme.

Default to manual Settings → Appearance → Icons selection. If live selection was
approved, set only the recorded icon-theme property in the verified session and
read it back. Never reset other appearance settings. For same-name updates,
provide a manual switch-away-and-back instruction or obtain approval for those
selection changes. Do not restart the desktop or kill applications.

## Verification and restoration

Verify expected files, index.theme, local SVG loading, licence and source notices.
Prefer process-local GTK lookup against temporary paths; native rendering and
live application coverage are distinct checks. Check light/dark icons and small
sizes. Some applications use bundled artwork and ignore icon themes. Four original
embedded bitmap images deliberately retain their colours. Do not promise every
individual image was visually reviewed just because all files decode.

For restore, switch to the recorded prior theme before removing files, only if the
selection still matches this installation's value. Stop on later edits. Preserve
an originally absent property by resetting that property only. Remove only
unchanged install-owned files/directories and restore original folders/links from
verified backups; keep conflicts for a merge. Do not remove system fallbacks or unrelated themes. RESTORE.md must give exact paths,
original selection and manual Appearance instructions, including reopening apps
that retain old artwork. Retain the restore record.
