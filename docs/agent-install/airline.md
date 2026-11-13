# Agent playbook: vim-airline

Follow [INSTALL.md](../../INSTALL.md) and the [human guide](../../dist/airline/README.md).

## Discover and propose

Detect Vim/Neovim, actual runtime/config paths, vim-airline installation and plugin
manager. Read existing airline_theme, background and true-colour settings, overrides,
symlinks and managed config sources. Do not install a plugin as a side effect.
Propose the native autoload file and a minimal selection diff, preserving the
editor colorscheme, sections, separators, extensions and all unrelated settings.
This theme uses the editor background option; explain any proposed background change.

## Apply, verify and restore

After approval and private backups/restore scripts, copy the artifact into the
chosen runtime path and merge the selector. Test both backgrounds and theme reload,
normal/insert/visual/replace/inactive modes, modified buffers and diagnostic accents
in a disposable editor. Full user startup executes plugins and may write state;
include it in the approved scope. User visual verification was reported on 2026-11-13; exact versions and
visual-test coverage were not recorded. See the human guide for check limits.

Restore the previous selector/background/true-colour settings and replaced file,
checking post-install hashes for conflicts. Detach references before deleting only
unchanged installation-owned files. Reload the old airline theme or request a safe
restart; never force-close unsaved buffers. Do not remove the plugin.
