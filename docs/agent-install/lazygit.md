# Agent playbook: lazygit

Read [INSTALL.md](../../INSTALL.md), the [human guide](../../dist/lazygit/README.md)
and [source metadata](../../themes/lazygit.py). Prefer separate config layers over
merging a palette into a large user config.

## Discover

- Identify the binary/version and actual launch route: terminal, alias/function,
  editor integration, wrapper or GUI launcher. A shell-only setting may not reach
  an editor that was already running.
- Find the effective config directory and ordered layers from invocation flags,
  `LG_CONFIG_FILE`, `CONFIG_DIR`/native defaults and wrappers. Read only the relevant
  files. Do not assume that `config.yml` is the only layer or automatically add it
  when the user's existing list intentionally omits it.
- Inspect repository/worktree-specific overrides in the target repository when
  relevant. Never modify those merely to enforce a global theme.
- Identify existing appearance overrides and whether terminal appearance detection
  works. Offer automatic or a fixed variant; do not infer OS appearance support
  from a successful fixed-theme test.

## Propose and apply after approval

1. Choose a permanent, user-approved location for the separate theme file(s), using
   the guide's artifacts and the selected automatic/fixed behaviour. Back up a
   same-named file before replacing it.
2. Preserve the existing layer list in order and append the chosen theme exactly
   once. Show the effective resulting list, including the existing base config
   only when appropriate. Keep repository overrides. An explicit argument and
   `LG_CONFIG_FILE` are alternatives; do not introduce conflicting mechanisms.
3. If persistence requires editing a profile, wrapper or editor configuration,
   name that file and show its diff. Do not change global Git settings to select
   this UI theme. Do not create duplicate `gui` keys if a user specifically chooses
   an in-place merge instead of layers.
4. Treat a delta renderer as a separate optional integration. It needs its own
   installation and syntax-cache scope; the plain lazygit theme does not require
   bat/delta, and this playbook does not authorize their installation automatically.

## Verify and restore

Confirm native loading in the intended launch context, preserving keybindings,
Git options, pager choices and other layers. Prefer a disposable repository and
isolated state/config directories for a launch test; include those writes in the
approved plan and reproduce the relevant layer order. Do not stage, commit, fetch
or modify a user's repository to test a colour scheme. A disposable test cannot
prove an already-running editor inherited a new environment: report that limitation.

Restore the former layer selection/profile/wrapper first, then restore or remove
this run's theme files using the shared conflict rules. Keep the user's base config,
other layers, editor settings and repository overrides. List any app state written
by the approved verification launch; do not wipe shared lazygit state as cleanup.
