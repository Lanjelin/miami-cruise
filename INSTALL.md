# Agent-assisted theme installation

Use this guide when a user asks an agent to install or restore Miami Cruise.
It is an instruction set, not an executable installer. Reading it, approving its
contents, or working on this repository does **not** authorize changes to the
user's installed applications or configuration.

## Start without cloning

No clone, build, agent installation or manual theme download is required. Give an
agent with web access and access to the target machine this prompt:

> Help me install Miami Cruise. Read
> https://raw.githubusercontent.com/lanjelin/miami-cruise/main/INSTALL.md
> and follow its linked playbooks. Discover supported apps, let me choose apps and
> variants, then propose exact changes and wait for my approval. Download the
> selected files yourself from the project website or GitHub; do not ask me to
> clone or build the repository. Include private backups and conflict-aware
> restoration instructions and scripts before applying changes.

For one app, replace the discovery request with its name. If the agent cannot
access the target machine, it can provide tailored commands instead of applying
changes. Never claim local discovery from a remote browsing environment.

### Obtain documentation and artifacts

- The entry URL tracks `main` for discovery. Resolve the selected release/ref to
  one full Git commit SHA, then read `INSTALL.md`, linked playbooks, human guides
  and metadata from that same revision. Resolve relative links against each
  document's URL, not the user's working directory.
- Prefer downloading only selected artifacts. The [website](https://lanjelin.github.io/miami-cruise)
  provides per-app downloads and SHA-256 checksums, for example
  `https://lanjelin.github.io/miami-cruise/downloads/eza/miami-cruise-dark.yml`.
  Use its actual file list; archives and supporting files differ between apps.
- For reproducible GitHub downloads, use
  `https://raw.githubusercontent.com/lanjelin/miami-cruise/<full-commit-sha>/dist/<app>/<filename>`.
  Documentation uses the same base and its repository-relative path. No Git
  checkout or Git executable is needed for this route.
- Website downloads can change independently of the chosen revision. Verify
  downloaded bytes against the pinned GitHub artifact; if they differ, use the
  pinned artifact instead. Record exact source URLs, commit and SHA-256 values.
  A locally calculated hash identifies bytes; it is not a publisher signature.
- Public project documentation/artifact reads are part of this requested flow;
  do not upload local configuration or backups. During planning, retrieve/hash
  bytes without writing to the target. If disk staging is required, list its
  exact private path in the proposal and wait for approval before creating it.
  Include downloaded files and staging cleanup in the journal after approval.
- Inspect archive paths/types before extraction; reject traversal and unexpected
  links. Never pipe downloaded content into a shell or run a repository build as
  part of theme installation. Existing native app/plugin-manager integrations
  remain available when appropriate to the inspected configuration.

## Choose an entry point

- **One app:** inspect and propose an installation for the named app only.
- **Guided selection:** discover supported apps, report what was found, then ask
  which apps and variants the user wants. Do not select everything automatically.
  Allow manual selection when an app is not discoverable in the agent's environment.
- **Restore:** follow the installation's own `RESTORE.md`, manifest and scripts,
  together with the [restoration rules](docs/agent-install/RESTORE.md).

Use the app-specific playbook together with the common procedure below. Coverage
means the installation/restore approach is documented, **not** that every OS or app
version has been tested. Keep each human guide's compatibility limits visible.

| App | Installation pattern | Agent playbook | Human install guide |
|---|---|---|---|
| Neovim | Runtime file and existing startup/plugin selection | [Neovim](docs/agent-install/nvim.md) | [Neovim guide](dist/nvim/README.md) |
| Vim | Runtime file and existing vimrc selection | [Vim](docs/agent-install/vim.md) | [Vim guide](dist/vim/README.md) |
| vim-airline | Existing runtime path and airline theme selection | [vim-airline](docs/agent-install/airline.md) | [vim-airline guide](dist/airline/README.md) |
| zsh-autosuggestions | Colour-only style sourced after plugin initialization | [zsh-autosuggestions](docs/agent-install/zsh_autosuggestions.md) | [Suggestion style guide](dist/zsh_autosuggestions/README.md) |
| tmux | Theme include plus separately approved live-server options | [tmux](docs/agent-install/tmux.md) | [tmux guide](dist/tmux/README.md) |
| WezTerm | Lua module merged into the actual config | [WezTerm](docs/agent-install/wezterm.md) | [WezTerm guide](dist/wezterm/README.md) |
| Zsh | Direct sourcing or existing framework integration | [Zsh](docs/agent-install/zsh.md) | [Zsh guide](dist/zsh/README.md) |
| eza | Selected config directory and `theme.yml` merge | [eza](docs/agent-install/eza.md) | [eza guide](dist/eza/README.md) |
| fzf | Existing options/environment integration | [fzf](docs/agent-install/fzf.md) | [fzf guide](dist/fzf/README.md) |
| Yazi | Flavor archives and existing TOML selection | [Yazi](docs/agent-install/yazi.md) | [Yazi guide](dist/yazi/README.md) |
| delta | Native Git-config layers and shared bat cache | [delta](docs/agent-install/delta.md) | [delta guide](dist/delta/README.md) |
| lazygit | Separate theme file and existing config layers | [lazygit](docs/agent-install/lazygit.md) | [lazygit guide](dist/lazygit/README.md) |
| bat | Syntax themes, compiled cache, default selection | [bat](docs/agent-install/bat.md) | [bat guide](dist/bat/README.md) |
| btop | Native theme files and saved selection | [btop](docs/agent-install/btop.md) | [btop guide](dist/btop/README.md) |
| Glow | Markdown stylesheet and existing style selection | [Glow](docs/agent-install/glow.md) | [Glow guide](dist/glow/README.md) |
| Brave | File preparation, then manual browser-profile handoff | [Brave handoff](docs/agent-install/brave.md) | [Brave guide](dist/brave/README.md) |

The [supported-app catalogue](README.md#supported-apps) and `themes/<app>.py`
GUIDE metadata are the source of available artifacts, examples and tested versions.
The website and `dist/<app>/README.md` are generated from that metadata. Do not
maintain another copy of their installation commands here. Web/CSS and design tokens
are project-integration assets, not a terminal-app installation: inspect the target
project's integration/build conventions and obtain a separate change plan rather
than applying a shell or desktop-config playbook.

Brave is a manual handoff by default. Do not edit browser profile internals, silently
enable Developer mode or declare success after file extraction. Follow the handoff
playbook for prior-theme recovery, user confirmation and restoration limitations.

## 1. Inspect first — no target changes

Record findings as **detected**, **inferred** or **unknown**. Establish:

- Target OS, user, home directory, shell, application versions and actual binaries.
  The agent's shell/session may differ from the user's terminal, GUI launcher,
  remote host, container or tmux server. Ask where the app runs if this is unclear.
- Active config and cache paths: explicit flags, wrappers/aliases, application
  overrides, XDG/native defaults and included files. Defaults are candidates, not
  proof. Inspect only relevant environment values; do not dump the full environment.
- Existing theme selection, other layers, symlinks (including parent directories),
  permissions, and whether a dotfile manager or package manager owns a file.
- Relevant existing config and its syntax, preserving unrelated settings and
  comments. Do not source shell startup files to discover their values.
- Available dependencies, their versions and the existing package manager, if any.
  Separate prerequisites from optional integrations, fonts and visual conveniences.

Read files before using commands that might initialize them. Do not launch an app,
run a cache builder, install a dependency, create a backup directory or write a
configuration file during discovery. A query/help/version command is suitable only
when its behaviour is known to be read-only; otherwise inspect documentation or
ask the user. Do not inspect unrelated private files or contact external services
on the user's behalf. Repository guides may be consulted as documentation, not
executed blindly.

## 2. Propose a reviewable change set

Present the selection and a concrete plan before **any target writes**, including
backups. Include:

1. Apps, variants, fixed versus automatic selection, and source release/commit.
   Record artifact SHA-256 values; identify the source of any downloaded artifact.
2. Exact files/directories to create, edit or replace; resolved symlink targets;
   ownership/permissions; before/after config diffs; settings/layers preserved.
3. Environment changes and their scope: one process, current shell or persistent
   startup/profile configuration. Name the actual profile being edited. A GUI
   launcher or existing tmux server may not inherit a newly exported variable.
4. Dependency commands, source, privileges and consequences, separately from theme
   changes. Do not upgrade unrelated software or assume administrator access.
   If installation would write beyond the inspected scope, inspect first and seek
   approval for the revised scope. Package installation is not a reversible theme
   file copy; explain its separate rollback limits.
5. Cache generation, app launches, verification and restarts, including expected
   config/state writes. Specify a bounded generated-state directory when filenames
   depend on the app version; include its inventory in the backup/restore plan.
6. A private restore-directory path outside repositories, what will be backed up,
   how each action will be undone, and any metadata that cannot be preserved.
7. Copy-pastable commands or scripts with paths tailored to this system, quoting
   filenames safely and preserving existing configuration. Do not use `eval` or
   shell interpolation to load a manifest, parse config or execute path values.

Offer **apply the plan**, **commands/scripts only**, or **cancel**. In commands-only
mode, generating approved script files is itself a listed write; alternatively
present them in chat without executing them. Scripts must perform the same state
checks and backup steps as the agent, and must not hide dependency installation or
privileged actions. Do not treat elapsed time or silence as approval.

Stop for a revised plan if the target state changes, a dependency needs a different
installation method, a symlink resolves elsewhere, or an additional file must be
modified. Approval for one app is not approval for all detected apps.

## 3. Back up, apply and journal

Only after approval:

- Create a unique restore directory such as `<chosen-state-dir>/miami-cruise/restores/
  <UTC-timestamp>-<unique-id>/`. Resolve this path during planning; do not assume a
  particular host's home/XDG paths. On POSIX, restrict the directory to the user
  (`0700`, backup files `0600`); on Windows, use equivalent restrictive ACLs.
  Refuse to put backups in this repository or another version-controlled directory.
  Backups can contain credentials: keep them local and never commit or upload them.
- Follow the [restore format](docs/agent-install/RESTORE.md). Save original bytes
  and metadata, record paths that were absent, and verify backup hashes before
  changing originals. Back up symlinks as links, not accidentally as their targets;
  a target modified intentionally needs its own entry.
- Write the manifest, user-readable restoration instructions and platform-specific
  conflict-checking restore script **before** applying theme/config/cache changes.
  Check script syntax with available tools before the first such change. Update
  the journal after each operation, including partial failures.
  Recheck preconditions immediately before writes. A failed backup stops installation.
- Prefer separate theme files and native includes/layers. Merge only intended keys;
  preserve unrelated configuration. For managed dotfiles, modify the approved source
  using its established workflow, not a generated/deployed file behind the manager.
- Apply file edits atomically where supported while preserving approved metadata.
  Record the resulting hashes and generated-state inventory. Do not keep going
  after a failure; report completed and pending actions and propose recovery.
- A repeated install must not duplicate includes, append theme paths repeatedly,
  replace the original restore point, or treat pre-existing files as newly owned.
  Each new approved change set gets a new restore record referencing the previous
  one where relevant. Restores run in reverse installation order.

## 4. Verify and hand over

Use the app playbook and the existing guide's tested-version limits. Check native
syntax/loading and preservation of unrelated settings. Verify the chosen theme is
actually selected, not merely present on disk. App launches that create config or
state must have been included in the approved plan.

Report **verified**, **awaiting user action/restart/visual confirmation**, **blocked**, or
**partially applied**, per app. Do not claim an untested OS, GUI session or automatic
appearance transition was verified. Give the user the restore path, exact manual
restoration steps and generated restore commands/scripts. Restoring configuration
also requires an approved change set; do not automatically roll back later user
edits. No rollback should uninstall shared dependencies by default.

A [container test record](docs/testing/2026-11-12-agent-install.md) documents the
fixed-dark Linux install/restore exercise and its coverage limits.
