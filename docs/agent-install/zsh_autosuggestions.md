# Agent playbook: zsh-autosuggestions

Follow [INSTALL.md](../../INSTALL.md) and the [human guide](../../dist/zsh_autosuggestions/README.md).

## Discover and propose

Find Zsh, the actual ZDOTDIR/startup files, installed zsh-autosuggestions and its
plugin manager/deferred loading order. Inspect existing highlight-style assignments,
managed files and symlinks. Do not install the plugin or change prompt frameworks.
Propose one permanent style artifact and one source line after plugin initialization
and competing colour assignments. Preserve strategies, history settings, bindings,
widgets, async configuration and unrelated startup contents.

## Apply, verify and restore

After approval, backups and restore scripts, merge the source line without duplicates.
Check syntax, then try history suggestions and acceptance in an approved disposable
interactive shell in the chosen variant. Check both dark/light foregrounds; no
background is set. User visual verification was reported on 2026-11-13; exact versions and
visual-test coverage were not recorded. See the human guide for check limits.

Detach the source line, restore the previous highlight-style assignment and any
replaced artifact with conflict checks, and remove unchanged new files only.
Already-running shells retain the variable: restore its old value explicitly or
unset ZSH_AUTOSUGGEST_HIGHLIGHT_STYLE for the plugin default. Prefer a fresh shell;
do not replace the user's running shell or source their entire startup automatically.
