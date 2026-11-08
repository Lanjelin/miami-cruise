# Miami Cruise for WezTerm

Colour schemes and tab bar that follow your system's dark or light setting.

![WezTerm window in the dark and light variants (mock-up)](../../previews/wezterm/palette.png)

## Install

The theme files:

- [`miami-cruise.lua`](miami-cruise.lua): WezTerm module

Run the commands below from this folder, or from wherever you saved the file.

### 1. Put it next to your wezterm.lua

**macOS / Linux**

```bash
mkdir -p ~/.config/wezterm
cp miami-cruise.lua ~/.config/wezterm/
```

**Windows (PowerShell)**

```powershell
New-Item -ItemType Directory -Force "$HOME\.config\wezterm" | Out-Null
Copy-Item miami-cruise.lua "$HOME\.config\wezterm\"
```

> [!NOTE]
> It must sit in the same folder as your config file. If you use a single `~/.wezterm.lua`, put it in your home folder.

### 2. Load it in your config

```lua
local wezterm = require("wezterm")
local config = wezterm.config_builder()

package.path = wezterm.config_dir .. "/?.lua;" .. package.path
require("miami-cruise").apply(config)

return config
```

That is all. The theme follows the system dark/light setting, and WezTerm reloads your config when the system switches.

### 3. Force dark or light (optional)

Set `MIAMI_CRUISE` to `dark`, `light` or `auto` (the default) in the environment WezTerm starts from:

**macOS / Linux**

```bash
MIAMI_CRUISE=light wezterm
```

**Windows (PowerShell)**

```powershell
$env:MIAMI_CRUISE = "light"; wezterm
```

Or pin it in the config file. The environment variable still wins over this:

```lua
require("miami-cruise").apply(config, { mode = "light" })
```

> [!WARNING]
> **Launched from the Dock or Start menu?** Those don't see variables you set in a shell, so pin it in the config with `mode`.

> [!NOTE]
> The schemes are registered as `Miami Cruise` and `Miami Cruise Day`, so `config.color_scheme = "Miami Cruise Day"` also works.

## Details

- **Variants:** dark and light
- **Covers:** Foreground, background, cursor, selection, 16 ANSI colours, tab bar, copy mode, quick select
- **Glow:** No: a flat palette
- **Tested:** Logic tested against a stand-in for WezTerm's Lua API; colour fields checked against WezTerm's docs and source

## More

- [Website page for WezTerm](https://lanjelin.github.io/miami-cruise/apps/wezterm.html)
- [Palette and specification](../../docs/SPEC.md)
- [Report a problem](https://github.com/lanjelin/miami-cruise/issues/new/choose)
- [MIT licence](../../LICENSE)
