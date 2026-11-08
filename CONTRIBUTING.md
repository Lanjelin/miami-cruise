# Contributing to Miami Cruise

Thanks for helping. This project is small on purpose: one palette, one tiny module per app. Please read the [code of conduct](CODE_OF_CONDUCT.md) first.

## Ways to contribute

- **Report a bug.** Use the bug report form. Include the app and its version, your OS, and a screenshot if a colour looks wrong.
- **Request a port.** Use the port request form to ask for support in another app.
- **Write a port.** Follow the [porting guide](docs/PORTING.md). A port is usually a single file of about a hundred lines.
- **Fix or improve a port.** Contrast, a missing highlight group, a platform quirk: all welcome.
- **Improve the docs or the website.**

## Changing the palette

The palette in `palette.py` feeds every port, so a change there changes all of them. Open an issue first and explain the reason (a contrast problem, a clash between two colours, a missing role). Palette changes need a version bump and a changelog entry.

## Development

You need Python 3 and nothing else; there are no dependencies.

```sh
python3 -I build.py            # build every theme, the logo and the website
python3 -I build.py nvim vim   # build only some targets
python3 -I docs/gen_spec.py    # regenerate docs/SPEC.md
```

- `dist/` holds generated, committed files. **Run the build and commit the result**, or CI will fail with a message that `dist/` is out of date. Don't edit files in `dist/` by hand.
- `website/dist/` is generated and not committed.
- Screenshots live in `previews/` and `website/previews/`. `previews/render.sh` and `website/render.sh` re-render them (they need a headless Brave and, for Neovim, a Neovim binary). Re-rendering is optional for most changes.
- Test a change in the real app, in both dark and light, and say in your pull request what you tested.

## Pull requests

1. Fork, then branch from `main`.
2. Make a focused change. One port or one fix per pull request.
3. Run `python3 -I build.py` and commit `dist/`.
4. Update `CHANGELOG.md` under `[Unreleased]`.
5. Fill in the pull request template.

Commit messages should say what changed and why in a short imperative sentence, for example `Add Ghostty theme` or `Raise light-mode warning contrast`.

## Versioning and releases

The version lives in `palette.py` (`VERSION`) and follows [Semantic Versioning](https://semver.org/): a palette or behaviour change that alters how existing users' setups look is a minor or major bump, a fix is a patch. Pushing a tag such as `v0.2.0` that matches `VERSION` builds a GitHub release with the theme files attached.

## Licence

By contributing you agree that your work is released under the [MIT licence](LICENSE).
