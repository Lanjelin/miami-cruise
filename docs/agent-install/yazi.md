# Agent playbook: Yazi

Follow [INSTALL.md](../../INSTALL.md), the [human guide](../../dist/yazi/README.md)
and [source metadata](../../themes/yazi.py). Use the current `.yazi.tar.gz` artifacts,
not older ZIP filenames from another release.

## Discover

- Identify Yazi/version and the effective config directory, respecting
  `YAZI_CONFIG_HOME`, platform defaults, wrappers, symlinks and managed files.
  Read `theme.toml` and existing flavor directories; do not replace the whole config.
- Inspect the current `[flavor]` section and both selections. A config directory
  override selects all configuration, not just a theme; do not switch directories
  to bypass a user's existing setup.
- Establish terminal dark/light appearance reporting and the desired fallback.
  Font icons and external previewers are optional and not installed automatically.

## Propose and apply after approval

Verify artifact hashes and inspect archive member names/types before extraction.
Require the expected single flavor root and documented files; reject absolute paths,
traversal, links or unexpected entries. Extract into an approved staging directory,
then back up and install into the discovered `flavors/` directory. Never use tar as
an excuse to overwrite an existing flavor tree without first inventorying it.

For a same-named flavor, show file-level replacement/merge decisions, preserve
unrelated files and record each mutation. Do not recursively delete the existing
folder or assume it contains only files from a previous Miami Cruise release.
Merge the selected `dark`/`light` keys in the existing `[flavor]` section, avoiding
new duplicate headers and preserving other TOML settings. When appearance reporting
is unavailable, offer the same fixed flavor for both keys rather than claiming
automatic desktop switching works.

## Verify and restore

Check TOML parsing and actual packaged flavor loading in an isolated, approved
fixture. A direct-theme fixture alone does not verify runtime flavor selection;
report terminal appearance and real-session checks separately. Avoid opening private
files, triggering external previewers or starting Yazi integrations without approval.

Restore the prior flavor keys before removing this run's artifacts, following
content/metadata conflict guards for each file. Restore overwritten files from
backups; remove only unchanged new files and empty new directories. Keep unrelated
flavors, plugins, previews and config. Explain restarting Yazi to reload its former
selection. A newly installed archive tool is not automatically uninstalled.
