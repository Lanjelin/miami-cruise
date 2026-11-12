# Agent playbook: Neovim

Follow [INSTALL.md](../../INSTALL.md), the [human guide](../../dist/nvim/README.md)
and [source metadata](../../themes/nvim.py). Neovim and Vim have distinct artifacts
and startup rules; do not substitute one for the other.

## Discover

- Identify executable/version and the actual config/runtime path, including XDG,
  native Windows locations, `NVIM_APPNAME`, custom startup flags, plugin managers,
  includes and managed sources. Defaults in the human guide are examples only.
- Inspect Lua versus Vimscript startup, current colourscheme/background selection,
  and whether a plugin or autocmd reapplies them later. Do not run arbitrary config
  merely to learn its paths. GUI launch context can differ from the agent's shell.
- Ask about dark/light behaviour, transparent terminal background versus the
  optional opaque fill, and preservation of any existing user highlight overrides.

## Propose and apply after approval

Place the Lua colorscheme on the actual approved runtime path, preserving a
same-named user file. Integrate selection through the user's existing configuration
or plugin-manager mechanism; do not create a competing `init.lua`/`init.vim` or replace
their entire setup. Use language-appropriate syntax and ordering, inspecting the
existing logic before proposing a change.

Set requested background/opaque options before loading the scheme. Explain that
the theme enables true colour and leaves some surfaces intentionally filled. Do
not install Treesitter parsers/plugins, a GUI, or extra fonts as mandatory theme
steps; optional integrations and their dependencies require their own approval.

## Verify and restore

Separate an isolated native-loading test from a test of the user's complete config:
startup can run plugins, install packages, create state or execute commands. Include
those writes in the approval, or report the real setup as awaiting user verification.
Use a disposable sample buffer; do not modify open files or write an editor session.
Test relevant background changes and explicitly retained highlight customizations.

Restore the prior selector, background/opaque options and installed file under the
shared conflict rules. Remove only this run's plugin-manager entry if one was added;
do not clean the user's plugin directory or undo unrelated updates. A running editor
may retain applied highlights/autocmds: use an approved reload of the previous
scheme or explain restarting, preserving unsaved buffers and active work.
