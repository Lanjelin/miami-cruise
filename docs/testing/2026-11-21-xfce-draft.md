# XFCE first-draft validation — 2026-11-21

Scope: generated dark/light GTK3 + Xfwm4 desktop themes based on Greybird revision
`7e4507d7713b2aaf41f8cfef2a1a9e214a4d8b6f`. First draft, not a release certification.

- Full dependency-free build passed.
- GTK 3.24.52 and Xfwm4 4.20.0 rendered both variants in a disposable Xvnc display
  with a private session bus, HOME, theme directory and XFConf configuration.
- Native screenshots were inspected for controls, selection, text, disabled states,
  progress and title-bar decorations. Dark-mode action-label contrast was corrected.
- No GTK theme parsing warnings in either capture. The isolated window manager has
  no session manager; this is not a full XFCE login-session test.
- 252 packaged PNG assets decoded with native GdkPixbuf.
- Package integrity, safe regular-file members, local CSS asset references,
  repeat-build hashes and independent corresponding-source rebuild passed.
- Screenshots use synthetic content only. SVG editor export-path metadata was
  stripped from the vendored source; upstream attribution is retained.
- Existing host GTK and window-manager theme selections were read before/after
  and remained unchanged. No theme was installed on the host desktop.

Commands:

```sh
python3 -I build.py
python3 tests/xfce.py
/usr/bin/python3 previews/xfce/render.py
```

Outstanding: user testing of Thunar, panel/pop-up menus, application-specific
controls, HiDPI, real desktop focus/hover behaviour and installation/restoration.
GTK2, GTK4/libadwaita, Qt, icons/cursors and login greeters are outside this draft.
The website was regenerated, but its new page has not had a browser interaction test.

## Initial desktop label follow-up

User reported black/low-contrast desktop icon text in Dark. Added explicit
`XfdesktopIconView.view.label` normal, hover, backdrop and selected colours,
with transparent desktop fill and a subtle label shadow. Native GTK style-context
checks now verify six label states in each variant using xfdesktop 4.20’s actual
CSS node/classes. The isolated widget previews still pass without GTK warnings.
Confirmation on the user’s live desktop remains pending; no live settings changed.

## Initial panel/taskbar follow-up

User reported barely visible taskbar text in Light. The upstream tasklist rules
assumed a dark panel, independently of the widget palette. Added explicit panel
and task-button foreground/background pairs, with nested-label and text-shadow
handling for normal, hover, active/checked, backdrop and disabled states.
Both variants now have native synthetic panel/tasklist widgets in their previews,
and eight button/label state checks per variant passed. Full build, archive/source
rebuild checks and GTK parsing checks passed. Real-panel confirmation remains
pending; no live configuration was changed.


## Expanded native desktop pass (supersedes the widget-only coverage limits)

Both variants now run real xfdesktop 4.20.2, xfce4-panel 4.20.8, Xfwm4 4.20.0,
xfsettingsd, Thunar 4.20.10 and GTK 3.24.52 inside private Xvnc/session-bus fixtures.
Only synthetic desktop files, applications-menu entries and control content are
captured. The host's existing themes were inspected read-only, not changed.

Found and corrected:

- Too-pale disabled labels on unfocused windows.
- Light tooltips retaining upstream white-on-light text.
- A blanket Thunar backdrop rule overriding readable filename/menu colours.
- Unfocused public GTK colour aliases, low-contrast tabs and slider handles.
- Desktop label readability against either bright or dark wallpaper, using a
  subtle theme-coloured label backing without replacing the wallpaper.

Verification:

- 48 measured native control-state contrast checks per variant (96 total) passed:
  default, suggested, destructive and flat buttons across focus, hover, active,
  checked and disabled states; additional entry, disabled-label and tab checks.
- Enabled text checks require 4.5:1; disabled control checks require 3:1.
- Real desktop normal/selected labels, native task buttons and hover/tooltips,
  applications menus/hover, combo popup, focused/unfocused Thunar and control
  windows, plus opposite-brightness wallpaper captures were visually inspected.
- No GTK theme parsing errors or criticals in the tested desktop, panel, Thunar
  or control processes. Optional thumbnail backends are unavailable on the test
  host; image/video preview support is outside this theme test.
- Public focused/unfocused/selected GTK colour pairs are checked in package tests.

### Same-name update cache reproduction

In both variants, deliberately old desktop/panel rules were loaded first, then
replaced with current CSS on disk. The running desktop pixels did not change.
Changing Appearance to Adwaita and back to Miami Cruise refreshed the styling.
This demonstrates why re-extraction alone is not sufficient to verify an update;
it does not prove the user's exact process state. The installed files matched the
previous packages when inspected, but the running user session was not restarted.

Reproduce the expanded pass:

```sh
python3 -I build.py
python3 tests/xfce.py
/usr/bin/python3 previews/xfce/render.py
/usr/bin/python3 previews/xfce/desktop.py
# Optional cache-reload experiment (same private environment only):
MIAMI_STALE_TEST=1 /usr/bin/python3 previews/xfce/desktop.py
```

Diagnostic frames and JSON checks live in ignored `previews/xfce/review/`.
Selected generic desktop/control frames are published to the gallery by the
preview runner. The website is generated but browser interaction is unverified.
Remaining coverage limits: user-session retest after reload, HiDPI, custom panel
backgrounds/label overrides, broader applications and complete install/restoration.
GTK2, GTK4/libadwaita and Qt remain outside this draft.

## Further user-reported menu and desktop failures

The user still reports unreadable menu items in both variants and dark desktop
labels in Dark. Earlier native checks did not establish correctness in that live
session; the cache experiment is not a diagnosis of these reports.

Added explicit normal/hover/selected/disabled/backdrop menu-item and nested label,
accelerator and arrow colours, including panel and window ancestry. Added explicit
view/cell/label foreground rules for desktop hover and backdrop states rather than
relying on inherited colours. Expanded native audits to 73 checks per variant,
including 25 menu-label checks each. Both passed, and current synthetic native
menu and desktop frames were inspected. Desktop style-context tests now exercise
view-only and cell-only paths too, not only the combined label path.

These are repository package fixes only. Live user-session confirmation is still
pending; do not describe the reported issue as definitively resolved there.

### Nested-menu regression found on the live desktop

The Applications menu was readable, but opening Accessories showed unreadable
submenu labels. Highlighted parent menu-item descendant selectors leaked their
foreground into the submenu. This was a stylesheet defect, not evidence of stale
installed archives. Restrict foreground selectors to the item's own children.

`/usr/bin/python3 tests/xfce-menus.py` exercises a real Gtk.Menu submenu with
a highlighted parent, without showing windows or changing desktop settings.
The installed pre-fix CSS fails this check (`--installed`); rebuilt dark and
light CSS pass. Updated packages still require live user confirmation.

### Switch visibility

The live dark Appearance off-switch blended into its track. Replaced inherited
slider gradients with explicit track/thumb pairs. Checked switches retain the
accent track; off switches use a contrasting muted thumb. Hover, backdrop and
disabled states are explicit. `/usr/bin/python3 tests/xfce-switches.py` checks
16 native GTK CSS states per variant for at least 3:1 thumb/track contrast.
Both native previews regenerated without GTK warnings; dark preview inspected.
Installed files are not updated by these development checks.

## Raised dark surfaces and approved live check

The dark desktop port now maps panel surfaces to the existing `row` colour,
neutral controls to `hover`, and hovered surfaces to `border`. Main background,
text, accents and the shared palette are unchanged; Light is unchanged.

Both native previews rendered without GTK warnings. All 146 native control
contrast checks, 32 switch states, nested-menu checks, full build and standalone
source/package reproducibility checks passed. Updated synthetic previews.

With explicit user approval, installed both rebuilt archives with verified
backups and changed the live GTK selection from Light to Dark. The live panel,
applications menu/submenu and Appearance controls were visually inspected.
Window-manager selection and unrelated settings were preserved. Private restore
records include the previous selection; no real desktop capture is published.

## Final small-control review

Reviewed both native desktop variants, focused/unfocused controls, menus,
Thunar, dropdowns and window decorations. Added restrained keyboard-focus
outlines, explicit entry borders and visible overlay scrollbar thumbs (including
backdrop); kept the shared palette and widget geometry unchanged.

- 81 native control contrast checks per variant (162 total) passed, including
  keyboard-focused button states.
- 32 switch states and both nested-menu regression tests passed.
- `tests/xfce-affordances.py` verifies focus-outline width, entry-border opacity
  and four enabled scrollbar states per variant at >=3:1 thumb/background contrast.
  Transparent overlay troughs are resolved against the actual containing window.
- Both GTK/Xfwm4 previews rendered without GTK warnings; package/source rebuild,
  full build and diff-whitespace checks passed.
- Both installed archives were updated with verified private backups. The user
  was actively switching themes during testing, so no agent-driven selection
  change or reload was made in this pass. Installed nested-menu checks passed.

This is native draft coverage, not a claim to test every GTK application, HiDPI
or non-GTK3 toolkits. Public previews remain synthetic; live desktop screenshots
were used only privately for inspection.

## Native panel styling — 2026-11-23

Panel styling now ships inside the existing dark/light GTK3 CSS: small corner
radii, comfortable button spacing, neutral active surfaces and a magenta inset
indicator instead of solid accent blocks. Normal text remains readable on active
buttons; disabled states and popup-menu overrides remain independent. No new
runtime dependencies, global GTK overrides or shared palette changes.

Panel layout remains entirely user-managed. No layout guide or preset is shipped.
Native private preview fixtures include top and bottom panels with synthetic
launchers solely to verify styling, not to prescribe a user layout.

Validation: full build, deterministic archive/corresponding-source rebuild,
162 native control contrast checks, 32 switch states, nested-menu regressions,
keyboard-focus/scrollbar checks and warning-free widget previews passed. Both
private desktop captures include the native bottom launcher panel and were
visually inspected. Rounded panels have an opaque-corner limitation without
compositing; no compositor changes are made automatically. Both installed themes
were backed up and updated; installed nested-menu checks passed. Live selection
and panel configuration were not changed. Reload via Appearance away and back.

### Flat plugin buttons

The live username Actions button inherited the base theme's ordinary button
border. Rounded corners emphasized it as a separate container. Resting panel
buttons now use transparent borders; hover fills, keyboard focus and active
accent indicators remain. No panel or plugin configuration changes are needed.

The follow-up live check isolated the remaining outer box to XFCE's external
`XfcePanelWindowWrapper` GtkPlug, which shares the panel style classes. Explicitly
remove its border and corner radius while keeping the actual panel's styling.
A native wrapper-name/class regression now verifies zero native border width. Corner shape is checked visually.

Live Dark was reloaded with its original selection preserved. Inspection confirmed
the Actions username no longer has a separate rounded outer box. Installed files
were backed up and hashes verified; no panel/plugin properties were changed.
The layout guide and generated download were removed at user request.

### Desktop drag-selection transparency

xfdesktop adds `.rubberband` to the view's own style context, rather than a
child CSS node. Explicit same-node overrides now use a 20%-opaque accent fill
and an opaque 1 px border, without changing selected icon labels. The native
regression checks alpha in normal, active, selected and backdrop states for both
variants. Real desktop drag captures in both private sessions were inspected;
icons remain visible through the rectangle. Installed files were backed up,
updated and Dark reloaded with the final selection preserved.

### Native window-button artwork

Replaced the inherited shaded button glyphs with dependency-free, 4x-coverage
antialiased symbols in the same 20×24 native tiles. Added explicit maximized
restore artwork; close uses a danger hover fill and pressed glyphs shift by one
pixel. Optional shade/stick/menu functions remain supported. Button ordering,
window geometry and unrelated window-manager settings are unchanged.

`tests/xfce-buttons.py` decodes all 72 assets, checks dimensions, nonblank glyphs,
opaque pixels and four distinct states per function, and generates an ignored
review atlas. The atlas and native previews were visually inspected. Native
dark/light desktop checks passed (162 contrast checks), as did corresponding
source/archive rebuild checks. Installed files were backed up and updated; the
live window-manager style was reloaded with its selection preserved. Active,
inactive and close-hover buttons were inspected on the live desktop. Real
desktop captures remain private; public previews contain synthetic content only.

## Pre-commit verification — 2026-11-23

Final pass reran all XFCE package/source rebuild, 72 window-button asset, nested
menu, 32 switch-state, focus/scrollbar/plugin-wrapper/drag-overlay checks and
162 native desktop control contrast checks. Both widget previews rendered
without GTK warnings. Archive scan covered 505 members with no personal or host
identifiers; 447 generated local website links/assets resolved.

Corrected the generated desktop guide's licence footer to use its GPL attribution
link instead of the default MIT link, and updated stale user-testing status.
HiDPI and non-GTK3 coverage remain explicitly outside verified draft coverage.
Personal desktop installation and restore backups were left untouched during
this audit. No commit or publication was performed.
