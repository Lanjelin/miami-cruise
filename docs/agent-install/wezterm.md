# Agent playbook: WezTerm

Follow [INSTALL.md](../../INSTALL.md), the [human guide](../../dist/wezterm/README.md)
and [source metadata](../../themes/wezterm.py). This is an executable Lua config
integration, not permission to replace the user's config.

## Discover

- Identify WezTerm/version, target GUI/session and actual config chosen by launcher
  flags or native lookup. Inspect includes, the returned config table, symlinks and
  managed sources without executing the config just to discover its structure.
- Read existing `colors`, scheme, tab-bar and window-frame overrides and any
  `MIAMI_CRUISE` environment selection. Determine whether the user launches from a
  terminal or GUI; shell exports may not reach an already-running GUI process.
- Ask about fixed versus automatic appearance. Linux system switching needs desktop
  portal support; a successful fixed selection does not verify automatic switching.

## Propose and apply after approval

Place the module beside the actual config file as specified in the guide. Show the
minimal `package.path`/apply integration before the existing return, preserving the
user's table construction and return behaviour. Do not paste a second complete
config into an existing file. Explain that the adapter replaces the tab-bar colour
table and merges window-frame colours, while other explicit colour overrides can
win; remove/adjust only the approved conflicting settings.

Choose config-based mode or the loader's environment selector deliberately, noting
that the environment wins. Preserve fonts, keybindings, startup commands, window
layout, opacity and tab-bar style unless a separate change is requested. Back up
both existing module and config/profile objects before writing them. A running
WezTerm may reload automatically on file edits: include that live effect in approval.

## Verify and restore

Configuration evaluation/launch may execute the user's Lua or spawn processes, so
include those checks in the plan. Verify the relevant terminal, tab and frame
colours in the actual viewer when available; report GUI/system-switching checks
not performed. Do not create private-output screenshots or replace a GUI terminal
merely to obtain a preview.

Restore config, module and any environment/profile edits using conflict checking.
Reapply/reload the previous selection only through an approved route. A live process
can retain its original environment; explain a fresh launch rather than silently
terminating windows. Keep unrelated Lua modules and user interface preferences.
