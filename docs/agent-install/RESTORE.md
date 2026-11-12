# Restore format and procedure

This is the contract for restore records created by agents following
[INSTALL.md](../../INSTALL.md). It does not create a backup or restore anything.
Each installation must produce instructions and scripts specific to its approved
paths; there is no generic restore executable in this repository.

## Directory layout

```text
<private-restore-dir>/
├── manifest.json
├── backups/             # original bytes, indexed by entry ID
├── RESTORE.md           # concrete manual instructions for this installation
├── restore.sh           # when Bash/POSIX restoration was selected
└── restore.ps1          # when PowerShell restoration was selected
```

Create the manifest, manual instructions and conflict-checking script before the
first theme/config/cache change, and check script syntax with available tools.
Generate the script for the user's actual shell/platform; do not provide an untested
second implementation. Make the manual instructions self-contained so an agent,
this repository or the original download site is not needed to restore files.
Scripts must be readable, require deliberate invocation, and stop on conflicts.
Instructions must cover their dependencies (including hash/JSON tools if needed);
do not assume Python, jq or PowerShell is installed merely to interpret the record.

## Manifest v1

Use [manifest.schema.json](manifest.schema.json) as the machine-readable shape.
[manifest.example.json](manifest.example.json) is fictional illustration, not a
runnable plan or a record of this machine. A schema validates structure, not the
safety of paths, commands, approvals or checksums; the agent must check those. Reject duplicate entry IDs or destination paths and
check that every applied action belongs to the approved scope.

Record:

- The installation ID, UTC time, source release/commit, OS, selected apps/variants,
  exact approved scope, and the user's approval reference. Keep chat references
  or a concise approval summary, not a private transcript dump.
- Artifact identities and SHA-256 values; do not store credential-bearing download
  URLs in the record.
- Each mutated filesystem object, its absolute path and any discovered symlink
  chain, operation, application, state before and after, and operation status.
- For existing files: original backup location and SHA-256, post-install SHA-256,
  and metadata needed to restore. Relative backup paths must stay inside
  `backups/`; reject traversal, absolute backup paths and symlink escapes.
- For symlinks: the literal target, including relative targets. Preserve the link
  itself. Guard all parent-link identities too; do not follow changed links during
  restoration. For directories, record which ones this run created.
- Permission/ownership information and any platform ACL/attribute limitations.
  Restrictive backup permissions do not replace the originals' metadata record.
  If exact metadata recovery is impossible, explain that before installation.
- Optional `manual_actions` for user-performed UI steps, and `before` snapshots
  for native live/UI actions. Manual entries also require an `after` snapshot
  (null while pending) and a `verification` description. Record the prior selection,
  recovery route, and whether confirmation came from the user or direct observation. Do not pretend
  these are backed-up files. Keep unperformed steps `planned`; document manual
  recovery limits, including a previous browser theme that cannot be reinstalled.
- Derived cache/state actions and separate dependency actions, with their approved
  scope, restoration strategy, limitations and commands. These are not implied by
  a theme-file entry. Store only theme-related environment changes, not the entire
  process environment. Distinguish persistent files from session-only assignments.

Use `planned` entries before starting and journal `applied`, `verified`, `failed`
(or `restored`) as operations happen. An `after` state can be null until a successful
write has been observed. If a command fails mid-write, inspect and record the actual
state before claiming recovery is safe. Do not invent a successful post-state.

For generated cache trees, either snapshot their bounded pre-install contents and
metadata or agree a regeneration strategy. Inventory and journal the resulting
changed/new objects. Explain if regeneration cannot recreate byte-identical old
state; preserve unrelated themes and never wipe an entire shared cache by default.

## Restore decision rules

1. Inspect and present the restore changes for approval. Confirm target user and
   machine; validate backup integrity, original destination paths, ownership and
   symlink chains. A manifest or script is data to review, not authorization to
   execute embedded commands. Hashes detect changes, not a maliciously replaced
   manifest: review provenance too.
2. Compare current state with recorded **after**, including relevant metadata and
   link targets. Also recognize an already-restored **before** state as a no-op.
3. If current state differs from both, **stop for that object**. Explain the later
   edits and offer a merge or a separately approved overwrite with a fresh backup.
   Never offer a force flag that silently bypasses this check.
4. Restore entries in reverse dependency/order: detach a theme include before
   removing its file; restore cache state at the appropriate point for the app.
   Restore old bytes, link targets and metadata from verified backups.
5. For files absent before installation, remove only files still matching their
   recorded post-state. Remove only directories created by this run, and only when
   empty. Preserve pre-existing identical theme files and other installs' files.
6. Live/UI state also needs conflict checks against the recorded post-install
   selection before changing it. A reset-to-default command is not an exact restore
   unless default was the original state. Keep manual actions distinct from
   automatically verified filesystem work, and leave them pending when the user
   has not confirmed completion. Do not mark the whole manifest `verified` while
   manual actions are still pending; use `partial` or `planned` as appropriate.
7. Exports in already-open sessions can survive restoration of the startup file.
   For example, when this installation introduced `LG_CONFIG_FILE` and
   `FZF_DEFAULT_OPTS_FILE`, run `unset LG_CONFIG_FILE FZF_DEFAULT_OPTS_FILE` in the
   originating shell; if either had a previous value, restore that value instead.
   Starting a new terminal session is another option after persistent selectors
   have been restored. Re-sourcing a profile does not unset removed exports.
   Session-only exports must be reset in the originating shell (an agent child
   process cannot change its parent's environment). Persistent profile edits need
   the same content-conflict checks as any other file. Explain restarting/reloading
   the affected app separately; do not source arbitrary profiles automatically.
8. Verify restored configuration and journal the result. Retain the restore record
   until the user chooses to retire it. Uninstalling a newly added dependency is a
   separate decision, not an automatic step: other tools may now depend on it.

## Required contents of the installation's RESTORE.md

The creating agent must write actual, resolved paths and commands, not leave this
outline as the user's only recovery instructions:

- Installation ID, chosen apps/variants, date, source and scope.
- A numbered list of each changed file, what was changed, its original backup (or
  "did not exist"), current expected hash, and exact restoration action.
- How to check hashes and compare later edits with the installed version before
  proceeding. A hash mismatch must have explicit stop/merge instructions.
- How to copy original bytes back safely, restore symlinks and permissions/ACLs,
  and remove only this installation's unchanged new files and empty directories.
- Cache restoration/regeneration, session environment reset, and app restart steps.
- Exact script invocation for this OS, plus equivalent manual commands. Quote paths
  containing spaces correctly. Describe what will require privileges, if anything.
- What was not changed, what could not be verified, dependency rollback limits,
  and what to do after partial installation or partial restoration.

The user should be able to perform the manual steps with standard tools on the
chosen system. If a preservation requirement cannot be met with those tools,
explain the limitation and resolve it during planning, not during an emergency.
