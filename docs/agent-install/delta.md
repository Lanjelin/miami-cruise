# Agent playbook: delta

Follow [INSTALL.md](../../INSTALL.md), the [human guide](../../dist/delta/README.md)
and [source metadata](../../themes/delta.py). Use the [bat playbook](bat.md) for
shared syntax-theme installation; do not maintain a duplicate cache procedure.

## Discover

- Identify delta/version, invocation wrappers and the effective Git configuration
  scopes, includes and conditional includes. Inspect only relevant pager, delta
  feature, colour and syntax settings; do not dump unrelated Git configuration.
- Establish whether the user wants global, repository-local or command-only use.
  An existing pager integration is not authorization to replace it. Inspect
  `DELTA_FEATURES`, `BAT_THEME`, pager variables and explicit options that may affect
  the chosen result, distinguishing syntax colours from the complete diff theme.
- Discover the shared bat syntax cache and both installed theme names. Respect the
  delta guide's `BAT_CACHE_PATH`, XDG and version-compatibility limitations.

## Propose and apply after approval

Store the native `.gitconfig` theme at a permanent approved path, add one include
in the intended scope, and merge the selected feature with unrelated existing
features. Select only one Miami Cruise variant. Show conflicts with explicit
colour settings; do not silently remove them or force layout/line-number choices.

If syntax themes/cache setup is missing, include the bat playbook's files, cache
writes and dependencies in a separate approved subplan. bat is needed to build the
cache, not run delta afterwards. Do not change bat's own default theme unnecessarily.

Making delta the Git pager/diff filter is optional and must be listed separately.
Never replace a user's existing pager command or repository config by default.

## Verify and restore

Check syntax-theme discovery, then render a non-private sample diff in the selected
variant. Verify intended feature/config loading, not only an explicit command-line
trial. Do not stage, commit or change repository contents to test colours.

Restore feature/include/pager edits in reverse order using the recorded scope and
conflict guards; do not remove an include or dependency that predated this run.
Detach the include before removing its newly installed file. Restore shared bat
cache changes through the bat restore record, preserving other consumers and any
subsequent installs. Changes inside an editor or lazygit integration need their own
recorded restoration steps.
