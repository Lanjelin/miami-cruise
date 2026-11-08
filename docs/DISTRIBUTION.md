# Distribution

How the themes reach people, and what is planned for package managers.

## Today

| Route | What it is | For |
|---|---|---|
| `dist/<app>/` | The theme files and an install README, committed to the repo | Anyone browsing the repo; raw links; vendoring |
| Website | Downloads with checksums and install pages | Most people |
| GitHub Releases | `miami-cruise-all.zip`, attached when a `v*` tag is pushed | Pinning a version |

`dist/` is generated, and CI fails if it is out of date, so what is committed always matches the palette.

## Planned: standalone repositories for package managers

Plugin managers such as lazy.nvim, vim-plug, and Neovim's built-in package support expect a theme at the root of its own repository (`colors/miami-cruise.lua`). This monorepo keeps it at `dist/nvim/colors/`, so those managers can't install from it directly.

The plan is to keep one source of truth and publish generated output:

1. Create a repository such as `lanjelin/miami-cruise.nvim` (and `miami-cruise.vim` if wanted) containing only a README and the generated `colors/` folder.
2. Add a workflow here that, on a release tag, copies `dist/nvim/` into that repository and tags it with the same version.
3. Authenticate the workflow with a deploy key or fine-grained token limited to that one repository.

Nothing in the mirror is edited by hand, so it can never disagree with the palette. This is **not set up yet**; it needs the extra repositories and a secret, so it is better done once the first release is out and there's demand.
