# Agent-assisted installation: container test, 2026-11-12

## Scope and outcome

Arch Linux Docker container `miami-cruise-test`, non-root `tester`, fixed-dark
selection for all 12 supported terminal apps excluding WezTerm. Source commit:
`d36ae4153df6781404d49fba97aefed8a344bb9c`, with uncommitted installation-documentation
changes present. This is not a test of an exact clean release snapshot.

**11 apps passed native loading/rendering checks and were visually verified by the
user:** Neovim, Vim, tmux, Zsh, eza, fzf, Yazi, delta, lazygit, bat and Glow.
**btop was environment-blocked:** execution returned `EPERM` for its capability-bearing
binary; no capabilities were changed. No btop loading/visual pass is claimed.

The agent inspected and proposed changes, obtained approval, installed themes,
verified native selection and exercised guarded restoration. All journaled
configuration/theme/cache changes were restored. The three original Bash files
matched their original bytes, modes, ownership and modification times. No host or
repository changes were made by the container test.

Unexpected `/home/tester/.git` and `.viminfo` were preserved because their origin
was unconfirmed. Whole-home equality is **not** claimed. No separate deliberate
post-install user-edit conflict test is evidenced by this run.

## Findings and follow-ups

- Glow 3.0.0 `--help` initialized config and cache state during discovery.
- TUI checks needed a controlling terminal, dimensions and terminal-query responses.
- The restore script was created after installation writes: a procedural deviation.
  The guide now explicitly requires the script before theme/config/cache writes.
- A Glow directory classification error initially stopped restoration. After the
  journal classification was corrected, guarded restoration succeeded.
- After restoration, an existing shell retained `LG_CONFIG_FILE` pointing to the
  removed theme. The saved selector was gone and a fresh process had no override.
  Recovery instructions now explicitly cover unsetting/restoring session exports.

These documentation follow-ups have not been rerun as a fresh container exercise.
This test covers a clean Linux configuration, not existing-config merges, symlink
conflicts, GUI apps, light/automatic variants or other operating systems. It also
used a local checkout; the no-clone network-acquisition path was not exercised.

## Evidence

Private record retained inside the container (not committed):
`/home/tester/.local/state/miami-cruise/restores/20261112-guided-test-01/`.
It contains the manifest, backups, restoration scripts, logs, verification report
and restoration evidence. No private backups or home-file contents belong in this
repository.
