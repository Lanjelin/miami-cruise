# Agent playbook: OpenClaw Control UI

Follow [INSTALL.md](../../INSTALL.md) and the [human guide](../../dist/openclaw/README.md).
This port is a native personal-theme definition, not a Gateway config fragment,
plugin, tweakcn registry document or userstyle. Use the supported `theme` tool;
never edit OpenClaw's profile database or openclaw.json to install it.

## Discover and propose

- Download the native JSON directly from
  https://lanjelin.github.io/miami-cruise/downloads/openclaw/miami-cruise.json.
  Do not ask the user to download or attach a file; no repository clone is needed.

- Confirm that the installed OpenClaw supports theme list/get/import/set and that
  the requester has an authenticated profile. Read list/get for the current ID,
  saved mode and profile override state. Do not guess a requester/account ID.
- Inspect user/miami-cruise with get if it exists. Preserve its complete editable
  definition privately before replacing it. Do not confuse the built-in Miami
  theme with this collection's Miami Cruise theme.
- Read the native JSON and both palettes. Inspect explicit accent/font overrides
  through supported UI/tools when available; explain that these can take precedence.
- Propose the import, whether it will replace an existing personal definition,
  and the separate selection/mode change. Importing with apply=false is still a
  saved profile change and requires approval; preparing the repository artifact
  does not authorize importing or activating it.

## Apply and verify

Before mutation, save the pre-change appearance/definition and concrete supported
API restoration calls privately. A filesystem restoration script is not a substitute
for profile API restoration; never point a generic file restore at the database.
After approval, import the complete file as definition with id=miami-cruise and
apply=false. Select user/miami-cruise with set only when activation was approved,
using the chosen dark/light/system mode. Do not alter other people's profiles,
Gateway defaults, font/accent overrides, branding or unrelated preferences.

The import/set response confirms persistence, not browser rendering. Verify dark
and light in the actual requesting browser when authorized and available: surfaces,
text, dialogs, inputs, primary/destructive buttons, selections and keyboard focus.
Use neutral synthetic content and miami@cruise for demos; never share screenshots
of private conversations, accounts, machine details or network information.
If no requesting browser is available, report live rendering as unverified.

## Restore

Check that the current definition/selection still matches the journaled post-install
state before undoing it; stop on later conflicting edits. Restore the previous
personal definition if it was replaced, using import with apply=false. Restore the
saved theme ID and mode using set. Preserve the difference between explicit values
and null (unset overrides); do not replace inherited defaults with guessed values.
The current tool has no delete action: an unused newly imported definition may
remain in the catalogue. Do not delete profile storage to remove that entry.
