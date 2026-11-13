"""Colour-only style for the existing zsh-autosuggestions plugin."""


def render(p, variant):
    return (f'# Miami Cruise {variant}. Generated; colours only.\n'
            '# Source after your plugin manager and other suggestion colour settings.\n'
            f"ZSH_AUTOSUGGEST_HIGHLIGHT_STYLE='fg={p['muted']}'\n")


GUIDE = dict(
    name='zsh-autosuggestions', category='Terminal & shell', mono='zsa',
    tags=['Plugin', 'Suggestions', 'Colour only'], aliases='zsh autosuggestions ghost text history completion',
    status='User visually verified; see testing details',
    tagline='Readable, muted suggestions that leave your prompt in charge.',
    files=[(f'zsh_autosuggestions/miami-cruise-{v}.zsh', f'miami-cruise-{v}.zsh', f'Suggestion highlight style · {v}') for v in ('dark', 'light')],
    shots=[("zsh_autosuggestions/dark.png", "Dark palette: native Zsh history suggestions with muted completion text"),
           ("zsh_autosuggestions/light.png", "Light palette: native Zsh history suggestions with muted completion text")],
    tested='Zsh syntax and style assignment checks passed; user visual verification reported on 2026-11-13. Plugin version, OS and exact visual-test coverage not recorded',
    covers='Suggestion foreground only; inherited terminal background', glow='No: the flat palette',
    file_note='Requires zsh-autosuggestions, not bundled. Works with any prompt, including Miami Cruise Zsh. Does not install the plugin or change history, strategies, bindings, hooks or widgets.',
    steps=[('Save the style files', [
        ('p', 'Install zsh-autosuggestions with your existing plugin manager first. Save these downloads in a permanent directory; back up existing same-named files.'),
        ('code', [('Linux / macOS', 'sh', 'mkdir -p ~/.config/zsh/themes\ncp miami-cruise-dark.zsh miami-cruise-light.zsh ~/.config/zsh/themes/')]),
    ]), ('Source your chosen variant', [
        ('p', 'Add this line once to your existing .zshrc (or $ZDOTDIR/.zshrc), after plugin initialization and other suggestion styles. Use your actual path if XDG_CONFIG_HOME differs. For deferred plugin loading, apply it after the deferred initialization.'),
        ('code', [(None, 'zsh', 'source ~/.config/zsh/themes/miami-cruise-dark.zsh')]),
        ('p', 'Use miami-cruise-light.zsh for light mode. Source the file in the current shell to try it, then type a prefix from your history. Requires true-colour ZLE support for exact colours. No automatic appearance switching.'),
    ]), ('Restore', [
        ('p', 'Remove the source line and restore any previous ZSH_AUTOSUGGEST_HIGHLIGHT_STYLE assignment and replaced files. Start a fresh shell. In a running shell, restore the old value explicitly, or unset ZSH_AUTOSUGGEST_HIGHLIGHT_STYLE to use the plugin default; deleting files alone cannot reset shell variables.'),
        ('note', 'Native style reference: https://github.com/zsh-users/zsh-autosuggestions#suggestion-highlight-style'),
    ])],
)


def export(pals, dist):
    out = dist / 'zsh_autosuggestions'
    out.mkdir(parents=True, exist_ok=True)
    for variant, (p, _) in pals.items():
        (out / f'miami-cruise-{variant}.zsh').write_text(render(p, variant))
