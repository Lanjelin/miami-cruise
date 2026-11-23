# Agent playbook: XFCE desktop draft

Follow [INSTALL.md](../../INSTALL.md), the [human guide](../../dist/xfce/README.md)
and [metadata](../../themes/xfce.py). This is a first draft, not a universal GTK theme.

## Inspect without writes

Detect XFCE, GTK3 and Xfwm4 versions. Read the current selections using
`xfconf-query -c xsettings -p /Net/ThemeName` and
`xfconf-query -c xfwm4 -p /general/theme` in the requesting desktop's session.
Record absent properties as absent. If the session bus/display cannot be identified,
prepare files only and use a manual settings handoff; never guess the target session.

Resolve `XDG_DATA_HOME`, `~/.themes`, existing theme folders, symlinks and managed
sources. Inspect GTK_THEME environment overrides and user gtk.css files without
rewriting them. Check custom panel backgrounds and explicit desktop icon-label colour overrides
that can override theme colours. Do not reset these without approval.
Do not inventory or expose personal applications, accounts or unrelated settings.
GTK2, GTK4/libadwaita and Qt are outside this draft's support. No icon pack, cursor,
font, layout, wallpaper, compositor or login-screen changes are required.

## Propose, back up, then apply

Offer dark or light, with exact target directories and archive URLs from the site.
Download only selected archives and inspect members for traversal, links or unexpected
files. Never extract over a pre-existing same-named theme without preserving it.
Explain that GTK and window-decoration selections are independent; live selection
immediately affects the desktop and requires explicit approval, separately from
file-only preparation if that is the chosen scope.

Before any install writes, create the shared restore record and guarded script.
Back up existing destination files and record both XFConf values/types or absence,
the intended post-install values, ownership and directory creation. Do not edit
XFConf XML directly or back up entire live channels in place of targeted restoration.
After approval, install to the actual user theme directory. Prefer a manual selection
handoff; if approved for agent selection, update only those two XFConf properties.
Updating the same theme name does not reload CSS in running processes. Include
a separately approved Appearance switch away and back in a live-update plan,
or provide a manual settings handoff. Record the exact pre/post selections and
verify freshly reloaded apps; matching installed file hashes is not rendering proof.
Do not restart XFCE, kill apps, change GSettings, or force GTK_THEME globally.

## Verify and restore

Verify both packages have native GTK3 CSS, local assets, Xfwm4 pixmaps, index metadata
and licences. Check GTK loading in an isolated display/config first when available.
Then ask the user to check controls, menus, text fields, selected/disabled states,
Thunar, panel menus and active/inactive window borders in their real desktop.
Report blocked checks; loading alone is not visual verification. Never capture a
real desktop with identifying information for public previews.

Restore the two original XFConf selections only if they still match the values
this installation set. Stop on later user edits. If a property was absent originally,
reset just that property rather than writing an invented default. Switch away before
removing unchanged install-owned folders; restore backed-up same-named folders.
Keep changed files for conflict resolution. Manual RESTORE.md must list the original
Appearance and Window Manager choices and exact paths, and explain that existing
app windows may need reopening. Preserve all unrelated appearance settings.

## Panel scope

Panel styling is included in the GTK3 theme. Panel layout, placement, size,
plugins and launchers remain user choices; no layout preset is supplied.
Do not change these settings as part of theme installation.
