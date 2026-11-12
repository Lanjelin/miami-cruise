# Agent playbook: fzf

Follow [INSTALL.md](../../INSTALL.md), the [human guide](../../dist/fzf/README.md)
and [source metadata](../../themes/fzf.py). Preserve the user's picker behaviour.

## Discover

- Identify fzf/version and the actual shell or editor integration. Inspect relevant
  `FZF_DEFAULT_OPTS`, `FZF_DEFAULT_OPTS_FILE`, wrappers and integration-specific
  colour overrides in their source files without evaluating arbitrary shell code.
- Locate the existing options file and startup assignments, including symlinks or
  managed sources. Treat settings from another session as potentially stale.
- Establish terminal appearance and fixed variant. bat/rg preview tools and Nerd
  Fonts are optional integrations, not requirements of the fzf palette itself.

## Propose and apply after approval

Keep the chosen `.opts` artifact in a permanent directory. Use the guide's append
method to preserve current options, or use `FZF_DEFAULT_OPTS_FILE` only when it will
not discard an existing options file. Show the final assignment/file diff and its
ordering relative to other initialization. Do not repeatedly append theme options
on each reload or source, and do not remove existing bindings/layout/preview flags.

A temporary process/session test is an alternative to persistent startup changes.
If an editor integration overrides colours, inspect that integration and propose
its specific change rather than layering competing global overrides blindly.

## Verify and restore

Use an isolated picker with a small synthetic input list, not personal file names
or command history. Verify colours and preservation of search, selection and
bindings in the intended context; do not invoke user-defined preview commands on
private files as a test. Any app/editor launch writes need prior approval.

Restore the exact prior assignment/options file under the shared conflict rules.
Remove only the theme options added by this run; never unset the whole defaults
variable if other options remain. Reset session-only values in their originating
shell or explain opening a new session. Delete unchanged new theme files only after
detaching their references. Keep any pre-existing options file and optional tools.
