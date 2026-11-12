# Agent playbook: Vim

Follow [INSTALL.md](../../INSTALL.md), the [human guide](../../dist/vim/README.md)
and [source metadata](../../themes/vim.py). Use the Vim artifact, not Neovim's Lua file.

## Discover

- Identify Vim/version, terminal versus GUI launch, the actual vimrc/runtime paths,
  startup flags, packages/plugins, symlinks and managed configuration sources. Do
  not assume the example `~/.vim` directory applies on every platform.
- Inspect current colourscheme, syntax/background/true-colour settings and later
  overrides. Read relevant config; do not source it automatically to discover values.
- Determine the matching terminal background and whether the user wants inherited
  or opaque editor background. Explain the guide's true-colour versus 256-colour
  behaviour without changing terminal or font configuration as a side effect.

## Propose and apply after approval

Place the Vimscript colorscheme on the discovered runtime path and show the small
selection/background diff in the existing configuration. Preserve a same-named
file, plugin-manager setup, key mappings and custom highlight commands. Order the
optional opaque setting before scheme loading, as documented in the guide.

Keep a temporary `:colorscheme` trial separate from persistent vimrc edits. Do not
create competing startup files, add duplicate selection/autocmd entries, or replace
an existing config with the guide's short example.

## Verify and restore

Use an approved disposable buffer/config for basic loading. A full startup can
execute plugins, commands and state writes: include that in the plan rather than
claiming an isolated test verified the user's integration. Check the chosen
background and reloading behaviour; preserve unsaved buffers and sessions.

Restore the previous selection, background/opaque settings and original theme
file with post-install conflict checks. Detach new references before removing an
unchanged new artifact. Applied highlights may persist in a running editor; offer
an approved reload of the prior scheme or a safe user restart, never a forced quit
or blanket removal of unrelated highlight/autocmd definitions.
