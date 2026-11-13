# Miami Cruise for zsh-autosuggestions

Readable, muted suggestions that leave your prompt in charge.

![Dark palette: native Zsh history suggestions with muted completion text](../../previews/zsh_autosuggestions/dark.png)
![Light palette: native Zsh history suggestions with muted completion text](../../previews/zsh_autosuggestions/light.png)

## Install

The theme files:

- [`miami-cruise-dark.zsh`](miami-cruise-dark.zsh): Suggestion highlight style · dark
- [`miami-cruise-light.zsh`](miami-cruise-light.zsh): Suggestion highlight style · light

Requires zsh-autosuggestions, not bundled. Works with any prompt, including Miami Cruise Zsh. Does not install the plugin or change history, strategies, bindings, hooks or widgets.

Run the commands below from this folder, or from wherever you saved the file.

### 1. Save the style files

Install zsh-autosuggestions with your existing plugin manager first. Save these downloads in a permanent directory; back up existing same-named files.

**Linux / macOS**

```sh
mkdir -p ~/.config/zsh/themes
cp miami-cruise-dark.zsh miami-cruise-light.zsh ~/.config/zsh/themes/
```

### 2. Source your chosen variant

Add this line once to your existing .zshrc (or $ZDOTDIR/.zshrc), after plugin initialization and other suggestion styles. Use your actual path if XDG_CONFIG_HOME differs. For deferred plugin loading, apply it after the deferred initialization.

```zsh
source ~/.config/zsh/themes/miami-cruise-dark.zsh
```

Use miami-cruise-light.zsh for light mode. Source the file in the current shell to try it, then type a prefix from your history. Requires true-colour ZLE support for exact colours. No automatic appearance switching.

### 3. Restore

Remove the source line and restore any previous ZSH_AUTOSUGGEST_HIGHLIGHT_STYLE assignment and replaced files. Start a fresh shell. In a running shell, restore the old value explicitly, or unset ZSH_AUTOSUGGEST_HIGHLIGHT_STYLE to use the plugin default; deleting files alone cannot reset shell variables.

> [!NOTE]
> Native style reference: https://github.com/zsh-users/zsh-autosuggestions#suggestion-highlight-style

## Details

- **Variants:** dark and light
- **Covers:** Suggestion foreground only; inherited terminal background
- **Glow:** No: the flat palette
- **Tested:** Zsh syntax and style assignment checks passed; user visual verification reported on 2026-11-13. Plugin version, OS and exact visual-test coverage not recorded

## More

- [Website page for zsh-autosuggestions](https://lanjelin.github.io/miami-cruise/apps/zsh_autosuggestions.html)
- [Palette and specification](../../docs/SPEC.md)
- [Report a problem](https://github.com/lanjelin/miami-cruise/issues/new/choose)
- [MIT licence](../../LICENSE)
