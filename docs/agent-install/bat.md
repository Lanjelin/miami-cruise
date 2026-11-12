# Agent playbook: bat

Read [INSTALL.md](../../INSTALL.md), the [human guide](../../dist/bat/README.md)
and [source metadata](../../themes/bat.py). Follow the shared approval and restore
procedure; this page supplies bat-specific decisions, not an alternate installer.

## Discover

- Identify the actual executable (`bat` or distro-packaged `batcat`), version and
  wrappers. Respect the guide's tested versions; do not silently upgrade it.
- Locate config, `themes/` and cache directories using the app's native queries
  only when safe, plus relevant `BAT_CONFIG_DIR`, `BAT_CONFIG_PATH`,
  `BAT_CACHE_PATH`, XDG/native overrides and invocation flags. Treat query results
  from the agent's context separately from the user's interactive context.
- Inspect existing Miami Cruise `.tmTheme` files, default-theme options in the
  config, `BAT_THEME` and any shell/profile assignments. Preserve unrelated theme
  files and options. Discover cache location before proposing `cache --build`.
- Check whether delta shares this cache. Its compatibility/cache-path limitations
  remain in the [delta guide](../../dist/delta/README.md); do not install delta or
  modify Git settings merely because it is present.

## Propose and apply after approval

1. Propose copying the two artifacts listed by the bat guide into the discovered
   `themes/` directory. Show same-named file conflicts; do not overwrite custom
   files or assume an old `.bak` file is the correct restore point.
2. Let the user choose a fixed dark/light default. Prefer one default-selection
   method: bat config **or** `BAT_THEME` in the actual user-selected shell profile.
   A one-process trial is an alternative to a persistent default. Explain existing
   conflicting flags/exports instead of deleting them without approval.
3. Include rebuilding the compiled cache explicitly in the change set. Inventory
   its files and choose snapshot/restore or approved regeneration, including any
   effect on delta or other consumers. Do not remove unrelated syntax/theme caches.
4. Back up changed theme files, config/profile files and the agreed cache state;
   record newly created directories. Apply the guide's native installation steps
   with the discovered paths and preserve original metadata.

## Verify and restore

Confirm both names are discoverable and the selected theme renders a small,
non-private sample without an unknown-theme warning. A trial using explicit
`--theme` proves loading, **not** that a persistent config/profile default works:
verify that separately in the intended launch context when authorized. Do not
source arbitrary profiles automatically. Record visual/restart checks still needed.

Restore the former default and old theme files (or remove unchanged files created
by this run), then restore/regenerate the cache using the recorded strategy.
Retain unrelated themes and later cache changes. A newly installed bat package is
not automatically removed, especially when delta or other tools now use it.
