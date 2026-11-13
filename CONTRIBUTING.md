# Contributing to Miami Cruise

Thanks for helping. This project is small on purpose: one palette, one tiny module per app. Please read the [code of conduct](CODE_OF_CONDUCT.md) first.

## Ways to contribute

- **Report a bug.** Use the bug report form. Include the app and its version, your OS, and a screenshot if a colour looks wrong.
- **Request a port.** Use the port request form to ask for support in another app.
- **Write a port.** Follow the [porting guide](docs/PORTING.md). A port is usually a single file of about a hundred lines.
- **Fix or improve a port.** Contrast, a missing highlight group, a platform quirk: all welcome.
- **Improve the install guides, the docs or the website.** An app's install guide lives in its module, `themes/<app>.py`; the site's shared text in `website/content.py`.

## Agent installation documentation

[INSTALL.md](INSTALL.md) defines the shared consent and restoration procedure.
App-specific discovery, merge and recovery guidance lives in `docs/agent-install/`;
keep native commands and tested versions in the existing `themes/<app>.py` GUIDE.
Changes to installation behaviour must also update its restore guidance. These are
agent instructions, not an installer implementation or proof of cross-platform tests.

## Changing the palette

The palette in `palette.py` feeds every port, so a change there changes all of them. Open an issue first and explain the reason (a contrast problem, a clash between two colours, a missing role). Palette changes need a version bump and a changelog entry.

## Development

You need Python 3 (tested on 3.12) and nothing else; there are no dependencies.

```sh
python3 -I build.py            # build every theme, the docs and the website
python3 -I build.py nvim vim   # build only some targets
python3 -I build.py -v         # also print the token table and contrast ratios
```

- `dist/`, `docs/SPEC.md` and the apps table in the README are generated and committed. **Run the build and commit the result**, or CI fails saying they are out of date. Don't edit them by hand.
- `website/dist/` is generated and not committed.
- Use `miami@cruise` for preview/demo user-and-host identities. For native Miami Cruise Zsh captures, source `previews/identity.zsh` after the prompt theme; it sets display text only, without changing accounts or installed theme behaviour.
- Screenshots live in `previews/<app>/` and `website/previews/`. `previews/render.sh` re-renders them all, or run one app's `previews/<app>/render.sh`; they need Python 3, Node 22+ (native WebSocket, no npm packages), a headless Chromium browser (`BRAVE=/path/to/browser`, default `brave-origin`) and, for Neovim, a Neovim binary. Set `CDP_URL=http://127.0.0.1:PORT` to reuse an existing headless browser. Generators retain merged contact sheets and also capture individual dark/light DOM panels for the galleries. The eza preview needs eza 0.23.5+ on Linux (`EZA=/path/to/eza` to override). Re-rendering is optional for most changes.
- Zsh prompt regression checks: after building, run `python3 tests/zsh-prompt.py`, `python3 tests/zsh-context.py` and `python3 tests/zsh-polish.py` (requires Zsh 5.9+, Git and tmux). The standard-library-only suite uses disposable shells and tmux servers, not your shell configuration. It covers both palettes and all layout/transient combinations, context flags, existing hooks/widgets, delayed async Git results, pipeline/signal details, Git operations/worktrees, smart context, directory permissions, shell nesting, same-directory transient tracking, rightmost submission timestamps, path-lock placement and ASCII symbols.
- Plugin screenshots use native disposable tmux sessions and the shared Chromium capture tool. Set `AIRLINE=/path/to/vim-airline` for `sh previews/airline/render.sh`, or `ZSH_AUTOSUGGESTIONS=/path/to/zsh-autosuggestions` for `sh previews/zsh_autosuggestions/render.sh`. These must be existing upstream checkouts; preview scripts do not download or install plugins. Requires Vim/Zsh respectively, plus tmux. They produce dark/light panels and a merged contact sheet without touching user configuration.
- Test a change in the real app, in both dark and light, and say in your pull request what you tested.
- The tmux preview needs tmux 3.4 and uses two isolated servers to capture the real client chrome, with disposable layout fixtures. It never attaches to personal sessions.

## Pull requests

1. Fork, then branch from `main`.
2. Make a focused change. One port or one fix per pull request.
3. Run `python3 -I build.py` and commit what it generated.
4. Update `CHANGELOG.md` under `[Unreleased]`.
5. Fill in the pull request template.

Commit messages should say what changed and why in a short imperative sentence, for example `Add Ghostty theme` or `Raise light-mode warning contrast`.

## Versioning and releases

The version lives in `palette.py` (`VERSION`) and follows [Semantic Versioning](https://semver.org/): a palette or behaviour change that alters how existing users' setups look is a minor or major bump, a fix is a patch. After changing the version, run the full build; it refreshes the README version badge, specification, website and versioned packages. Pushing a tag such as `v0.2.0` that matches `VERSION` builds a GitHub release with the theme files attached.

## Licence

By contributing you agree that your work is released under the [MIT licence](LICENSE).
