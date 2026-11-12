# Agent playbook: Zsh

Follow [INSTALL.md](../../INSTALL.md), the [human guide](../../dist/zsh/README.md)
and [source metadata](../../themes/zsh.py). Installing a prompt is not authorization
to change the user's shell framework, bindings or plugins.

## Discover

- Establish the actual Zsh/version and startup chain. Account for `ZDOTDIR`, global
  `zshenv` redirects, login/interactive startup files, includes and managed symlinks.
  Do not assume `~/.zshrc` is used or source startup files during discovery.
- Identify direct sourcing versus Oh My Zsh/another framework, existing prompt
  selection and its initialization order. Read relevant MIAMI_CRUISE flags and
  activation-tool prompt settings; inspect their sources rather than executing them.
- Check intended dark/light variant, layout/transient preferences and font support.
  Offer ASCII fallback; Nerd Fonts, Oh My Zsh and Ruby helpers are not mandatory
  runtime dependencies for a directly sourced prompt.

## Propose and apply after approval

For direct sourcing, retain that approach and use the artifact's permanent path;
for Oh My Zsh, use its discovered custom-theme directory and existing theme selection.
Do not install a framework to satisfy an installation example. Propose one effective
prompt initialization route, replacing only the approved previous selection rather
than sourcing competing prompts together. Keep aliases, completions and plugins.

List each requested flag/profile edit separately. For Python environment labels,
explain optional `VIRTUAL_ENV_DISABLE_PROMPT=1` **before** activation; don't globally
change activation behaviour without consent. An inherited usable venv can lack a
shell-local `deactivate` function, so do not infer inactivity from that alone or
clean tmux's environment as a theme-install step.

## Verify and restore

Use syntax checks and an approved disposable interactive shell with synthetic paths
and isolated state. Verify the chosen layout and relevant hooks without entering
commands into the user's active editing buffer. Running their startup files can
execute arbitrary commands; a full live startup test needs its own approved scope.
Report checks that still need a new terminal, actual font or human visual review.

Restore startup/theme/flag edits with the shared conflict guards. Replacing prompt
text does not necessarily unload callbacks from a running shell: recommend a fresh
shell after restoration, not an untested widget/hook purge or killing active shells.
Detach references before removing unchanged new theme files; retain pre-existing
frameworks, widgets, plugins and activation-tool settings.
