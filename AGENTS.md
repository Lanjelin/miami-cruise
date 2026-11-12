# Agent instructions

Miami Cruise is a generated dark/light theme collection. Read
[CONTRIBUTING.md](CONTRIBUTING.md) for development, palette, and contribution rules.

## Working practices

- Inspect Git status before editing. Preserve existing changes; do not reset,
  overwrite, or discard work unrelated to the task.
- Keep changes focused and preserve the collection's visual identity. Shared
  palette changes affect every port; follow the palette rules in CONTRIBUTING.md.
- Use repository-relative paths. Inspect actual locations before relying on paths
  from previous sessions or another host.
- Repository work does not authorize installing themes into the user's environment
  or changing shell/system configuration. Obtain specific approval for those actions.

## Installing themes for a user

- For installation or restoration requests, follow [INSTALL.md](INSTALL.md).
  Its host-change approval and restore requirements apply to those tasks; they do
  not turn ordinary repository development into an installation request.
- Keep app detection/merge/restore playbooks in `docs/agent-install/`; native install
  commands, artifact lists and tested versions remain in each theme's GUIDE metadata.

## Source and generated files

- Edit generators and templates, not generated outputs alone. App generators and
  their installation-guide sources live in `themes/`; shared website text lives
  in `website/content.py`.
- `dist/`, `docs/SPEC.md`, and the README apps table are generated and committed.
  Regenerate affected outputs and review the diff. `website/dist/` is generated
  but not committed.
- Build all targets with `python3 -I build.py`, or selected targets with
  `python3 -I build.py zsh` (substitute the relevant target).
- Keep the Python build dependency-free. Do not introduce external Zsh runtime
  dependencies.

## Zsh changes

- Sources: `themes/zsh.py` and `themes/zsh-features.zsh`. The README under
  `dist/zsh/` is generated from the generator's documentation source.
- Support direct sourcing, both colour variants, single-/two-line layouts, and
  transient modes `0`, `1`, and `same-dir`.
- Preserve existing ZLE widgets and hooks; re-sourcing must not duplicate hooks.
  Keep async Git's stale-result protection across directory changes.
- Keep flags, defaults, and documentation consistent. The optional Git-operation
  flag is `MIAMI_CRUISE_SHOW_GIT_OPERATION`, not `MIAMI_CRUISE_SHOW_GIT_STATE`.
- After behavioural changes, regenerate and run:

  ```sh
  python3 -I build.py zsh
  zsh -n dist/zsh/miami-cruise-dark.zsh-theme
  zsh -n dist/zsh/miami-cruise-light.zsh-theme
  python3 tests/zsh-prompt.py
  python3 tests/zsh-context.py
  python3 tests/zsh-polish.py
  ```

  The regression suites require Zsh 5.9+, Git, and tmux and use disposable fixtures.
  Do not modify the user's shell configuration to run them. tmux `scroll-on-clear`
  can retain cleared prompts in scrollback; this alone is not a redraw failure.

## Verification and handoff

- Run checks appropriate to the change and `git diff --check`. For generator or
  palette changes, run the full build before handoff and inspect generated diffs.
- Preview tmux fixtures must use an explicit POSIX launcher shell (for example,
  `SHELL=/bin/sh`) so user Zsh startup cannot override disposable config paths.
  Run app-specific shells explicitly when testing them.
- For visual changes, verify both dark and light variants in the relevant app
  when available; screenshots need not be regenerated for unrelated changes.
- Report what changed, which checks ran, and any checks blocked or not performed.
  Do not present earlier-session test results as newly verified.
