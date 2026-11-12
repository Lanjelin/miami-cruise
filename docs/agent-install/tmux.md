# Agent playbook: tmux

Follow [INSTALL.md](../../INSTALL.md), the [human guide](../../dist/tmux/README.md)
and [source metadata](../../themes/tmux.py). Filesystem and live-server changes are
separate parts of the plan.

## Discover

- Identify tmux/version, target server/socket, active config/includes, plugin/theme
  initialization and managed files. Multiple servers can have different settings.
- Read existing status/window format strings, inline colour directives, local
  session/window overrides and plugin colours. Inspect RGB capability settings,
  but do not change terminal capabilities just to force the theme.
- Determine fixed variant and whether changes should affect future servers only
  or an existing server too. Do not attach to or alter another user's server.

## Propose and apply after approval

Store the theme files permanently and add one source line after the appropriate
existing initialization. Preserve status layouts, powerline separators, bindings,
plugins and terminal options. The theme changes base colours, not status formats;
explain inline/plugin overrides that will still win. Recolouring those is a separate
key-level diff and approval, not permission to replace the bar design.

Loading the file into a running server needs explicit scope and approval. Before
loading, snapshot the relevant effective options **and whether each was locally
set or inherited** at every scope the theme changes, using the detected version's
native option inspection. Journal this live state separately from file backups.
Never kill/restart a working tmux server as an installation shortcut. Use a truly
isolated server/socket and POSIX launcher shell for disposable tests; obtain approval
for its state writes and do not confuse that test with delivery to the target server.

## Verify and restore

Confirm the intended server loaded the file and unrelated format strings/bindings
were preserved. Test RGB visually where possible and report overrides/quantization.
Reloading the entire user config can execute arbitrary plugin commands: it is not
an implied safe verification step.

Restore the source line/config file and theme artifacts under conflict guards.
Deleting the file does not undo colours already loaded in a live server. Propose
restoring recorded live option values and inheritance, or an approved reload of
the prior theme; compare current options with recorded post-install values first.
Never reset unrecorded overrides or destroy sessions to return to defaults. Record
native live-state actions in the manifest's generated actions with a snapshot and
an explicit restoration strategy, not as a fictional filesystem backup.
