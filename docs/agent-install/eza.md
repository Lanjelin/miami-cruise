# Agent playbook: eza

Read [INSTALL.md](../../INSTALL.md), the [human guide](../../dist/eza/README.md)
and [source metadata](../../themes/eza.py). Never treat a sample directory as proof
of the user's active location.

## Discover

- Identify executable/version, wrappers and the launch context. Resolve
  `EZA_CONFIG_DIR` first; inspect applicable native/XDG defaults if absent. It is
  a directory selector, not a theme name. Inspect symlinks and managed sources.
- Read the active `theme.yml`, including existing filename, extension and icon
  customizations. Report what the generated theme would replace versus preserve.
- Inspect relevant `EZA_COLORS`, `LS_COLORS` and legacy `EXA_COLORS` overrides and
  aliases with colour flags. These can mask theme colours. Do not unset persistent
  values globally: other commands may use them too.
- Check the terminal's dark/light appearance where observable; otherwise ask. eza
  colours listings, not the terminal background; icons are optional, not a required
  dependency on a particular font.

## Propose and apply after approval

1. Propose the chosen variant as the discovered directory's `theme.yml`. If a file
   exists, show a key-level merge diff preserving unrelated rules and comments.
   When colours conflict, explain the choice rather than treating a user's custom
   theme as disposable. Avoid parser round-tripping that drops comments or changes
   unrelated formatting. If a reliable merge is unclear, ask or provide commands
   rather than overwrite the whole configuration.
2. Keep the existing directory selection unless there is an agreed reason to
   change it. If using a custom/non-native path, include its `EZA_CONFIG_DIR`
   assignment and exact profile file in the plan. Do not duplicate an assignment
   already supplied by another startup file or environment manager.
3. Offer a one-process trial without conflicting colour overrides, as described
   in the guide. Making that permanent is a separate, explicit config change.
4. Back up the original theme/profile bytes and metadata into this installation's
   restore record. Do not rely on or overwrite the guide's convenience
   `theme.yml.bak`: it may predate this installation.

## Verify and restore

Use a non-private sample listing, including several file types, to check loading
and colour output. Test the user's normal invocation separately from any trial
with overrides removed. Inspect the resulting config to confirm custom rules and
unrelated shell settings were retained. No compiled theme cache needs rebuilding.

Restore the backed-up theme and any approved profile edit, subject to post-install
hash/conflict checks. If this run created `theme.yml`, remove it only if unchanged.
Revert only environment/alias changes actually made by this run; keep unrelated
colour configuration and any pre-existing backup files.
