# Agent handoff: Brave (manual theme selection)

Follow [INSTALL.md](../../INSTALL.md), the [human guide](../../dist/brave/README.md)
and [source metadata](../../themes/brave.py). This workflow treats browser theme
selection as a **manual user step**, not an unattended profile-file installation.
This is a workflow boundary, not a claim that browser interaction is technically
impossible to automate. Do not advertise verified support for other Chromium
browsers merely because they use a similar manifest format.

## Discover and propose

Ask which desktop Brave profile and dark/light variant the user wants. Explain
that the theme changes browser chrome, not websites, New Tab preferences or automatic
OS appearance switching. The supplied ZIP is a native colour manifest and license,
not a script that configures the browser.

Have the user identify the current theme/default selection and a usable restoration
route **before** replacing it: theme name, reinstall source or an already available
local theme folder. Record only relevant identifiers. If the old theme cannot be
recovered, explain that exact restoration is not guaranteed and require an explicit
choice before proceeding; "reset to default" is not equivalent to restoring it.

Do not launch the user's browser/profile as a discovery shortcut. Do not read or
copy an entire profile, cookies, history, Preferences/Secure Preferences, extension
state or databases to make a generic backup. Never edit those internal files or
install into the profile's extension directories. Do not bypass enterprise policy
or developer-mode restrictions.

## Prepare only what was approved

The plan can authorize the agent to download verified artifacts, inspect archive
contents, extract the chosen ZIP into a permanent private/user-approved location,
and back up any same-named files. Record those file changes normally. Reject unsafe
archive paths/types and do not overwrite an existing extraction silently.

The plan must also list the browser UI changes as manual actions, including the
previous theme and developer-mode state where the user can establish them. Explain
that local loading may show a developer-mode warning, that the extracted folder
must remain available, and that only one browser theme can be active at a time.

Hand the user the existing guide's steps: open `brave://extensions`, enable Developer
mode if necessary, choose **Load unpacked**, and select the folder containing
`manifest.json`. The user performs those actions in the intended profile. A request
to automate that UI requires a separate, explicit interaction plan and supported
browser access; ordinary file-install approval does not authorize it.

## Verify and restore

Record UI actions under `manual_actions` in the restore manifest; use `planned`
until performed and distinguish user confirmation from an agent-observed result.
Do not mark the browser installed merely because extraction succeeded. Report
**awaiting user action/visual confirmation** when no verified UI result is available.

The installation's RESTORE.md must tell the user how to remove Miami Cruise through
`brave://extensions`/`brave://settings/appearance`, then reselect/reinstall the recorded
previous theme (or reset only if the original state was default). Check whether a
newer theme was selected since installation before replacing anything. Explain any
agreed developer-mode reversal separately; do not alter other extensions or their
permissions. Do not claim removal alone restores an arbitrary previous theme.

Only after the browser has been detached from this local theme should the agent
restore/remove staged files using the shared conflict checks. Keep pre-existing
folders and later user edits. Manual UI recovery must remain understandable without
the agent, this repository or a backup of the complete browser profile.
