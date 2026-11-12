# Agent playbook: btop

Follow [INSTALL.md](../../INSTALL.md), the [human guide](../../dist/btop/README.md)
and [source metadata](../../themes/btop.py). The shared backup, approval and
conflict-aware restoration rules apply throughout.

## Discover

- Resolve the binary/version, active `btop.conf`, theme search directories and any
  explicit `--config`/`--themes-dir` launcher flags. Distinguish btop from btop4win,
  bashtop and bpytop; the guide's compatibility claims do not cover them all.
- Read current theme, true-colour and background settings; inspect symlinks and
  managed sources. Determine whether btop is running: it can save config on exit.
- Inspect terminal appearance/capabilities without changing them. GPU support,
  hardware monitoring and fonts are not theme-install prerequisites.

## Propose and apply after approval

Copy the native theme files into the discovered theme directory without replacing
`btop.conf`. Select dark/light by updating only the approved existing keys **while
btop is closed**, or agree a user-driven Options selection and saved-config write.
Ask the user to exit a running instance; do not terminate it without authorization.

Offer terminal-background inheritance or the theme's exact fill, explaining the
guide's `truecolor`/`theme_background` choices. Do not alter refresh rates, process
sorting, monitoring boxes or unrelated settings. Custom launcher flags must be
supported by the detected version. List those edits explicitly if needed.

## Verify and restore

A container may reject execution of a capability-bearing btop binary with `EPERM`.
Report this as environment-blocked, not a theme failure or a passed loading check.
Do not remove binary capabilities or relax container security without separate
approval.

Include app launch/state writes in the plan. Prefer a disposable, isolated config
for preliminary testing; verify the intended configuration separately. Avoid
capturing or publishing a personal process list. Confirm both native loading and
the selected variant, and report hardware/OS checks not performed.

Close btop before restoring its config, subject to the user's approval, so a later
exit does not overwrite the restored values. Restore original files or remove only
unchanged files created by this installation. For a UI-driven selection, journal
the actual saved config change and previous settings before claiming it is safely
restorable; merely copying theme files does not capture that selection.
