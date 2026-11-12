# Miami Cruise for delta

A Miami Cruise diff on your terminal background, with clear inline changes.

![delta output with the dark theme, including inline changes](../../previews/delta/dark.png)
![delta output with the light theme, including inline changes](../../previews/delta/light.png)

## Install

Delta configuration:

- [`miami-cruise.gitconfig`](miami-cruise.gitconfig): Native delta theme (both variants)

`miami-cruise.gitconfig` defines the dark/light delta features and diff styles. Code-syntax colours use the shared Miami Cruise bat themes; see the <a href="https://lanjelin.github.io/miami-cruise/apps/bat.html#install">bat install guide</a> for those files and cache setup.

Run the commands below from this folder, or from wherever you saved the file.

### 1. Configure delta's native theme

Install delta. Save `miami-cruise.gitconfig` somewhere permanent. Add the following to your Git config (usually `~/.gitconfig`), using the actual absolute path. On Windows, forward slashes work in the path, for example `C:/Users/you/.config/delta/miami-cruise.gitconfig`.

```gitconfig
[include]
    path = /absolute/path/to/miami-cruise.gitconfig

[delta]
    features = miami-cruise-dark
```

> [!NOTE]
> Merge these sections with your existing config. Keep other feature names you want, but select only one Miami Cruise variant. Explicit colour settings in your main delta config can override the feature. The theme does not force side-by-side view, paging or line-number preferences.

Choose `miami-cruise-light` instead for light mode. The next step links to the shared code-syntax setup. Ordinary diff lines and hunk headers inherit the terminal background; inline changes and whitespace errors retain intentional fills. Use a true-colour terminal with a matching dark/light background.

### 2. Use the shared bat syntax themes

delta uses bat's syntax-highlighting engine and reads its compiled syntax cache; it does not run the bat executable when displaying diffs. Follow the <a href="https://lanjelin.github.io/miami-cruise/apps/bat.html#install">Miami Cruise bat install guide</a> to download both syntax themes and build the cache. If you already completed that setup, do not install duplicate copies. Selecting `BAT_THEME` for bat itself is optional here: delta's selected Miami Cruise feature sets its own syntax-theme name.

After completing the bat setup, confirm that delta discovers `miami-cruise-dark` and `miami-cruise-light`:

```bash
delta --no-gitconfig --list-syntax-themes
```

> [!WARNING]
> delta 0.20.1 does not honour `BAT_CACHE_PATH`. If you use that override, rebuild bat's cache in the default location for delta, or set the same absolute `XDG_CACHE_HOME` for both tools on macOS/Linux (cache: `$XDG_CACHE_HOME/bat`). Use compatible bat versions; these themes were verified with bat 0.26.1.

### 3. Try it, then optionally make it your Git pager

```bash
git diff --no-ext-diff --no-color | delta --features=miami-cruise-dark --paging=never
```

If you want delta as your pager, merge the following settings into Git config. Skip this if your pager is already configured.

```gitconfig
[core]
    pager = delta

[interactive]
    diffFilter = delta --color-only
```

To uninstall, remove the include and Miami Cruise feature name, and undo the pager settings only if you added them. Use the matching terminal background and a true-colour terminal; variant switching is manual.

## Details

- **Variants:** dark and light
- **Covers:** Syntax, diff lines, inline emphasis, file/hunk/commit headers and line numbers
- **Glow:** No: terminal output uses the flat palette
- **Tested:** delta 0.20.1 with bat 0.26.1 on Linux: both features, syntax cache, unified and side-by-side diffs, additions, removals and inline changes; macOS and Windows not tested

## More

- [Website page for delta](https://lanjelin.github.io/miami-cruise/apps/delta.html)
- [Palette and specification](../../docs/SPEC.md)
- [Report a problem](https://github.com/lanjelin/miami-cruise/issues/new/choose)
- [MIT licence](../../LICENSE)
