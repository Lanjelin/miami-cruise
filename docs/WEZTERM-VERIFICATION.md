# WezTerm desktop verification

Verified 2026-11-09 with upstream stable WezTerm `20240203-110809-5046fc22`
on Arch Linux, XFCE/X11. The upstream AppImage was extracted into a user-local
directory; no system package or desktop appearance settings were changed.

## Results

- Fixed dark and light modes loaded, and switched in the same GUI on reload.
- Effective palettes matched the generated foreground, background, cursor,
  selection, ANSI/brights and copy/quick-select colours.
- Fancy and retro tab bars were inspected in both modes, with multiple tabs.
- Horizontal splits, active/inactive panes, selection, search, copy mode and
  quick select were exercised through the GUI. UTF-8, box drawing, bold,
  italic and underline rendered in the test fixture.
- The existing configuration's fonts, key/mouse bindings and non-theme settings
  were preserved; only the former theme block was replaced after backing it up.
- Starting that normal configuration with `MIAMI_CRUISE=light` overrode its
  fixed dark setting. With no override, dark loaded correctly.
- Terminal OSC queries confirmed the normal configuration's actual colours:

| Query | Dark | Light override |
|---|---|---|
| OSC 10 foreground | `#deebec` | `#142a30` |
| OSC 11 background | `#0d1d22` | `#f1f8f9` |
| OSC 12 cursor | `#ff7fc0` | `#b51c79` |
| OSC 4 index 5 | `#ff7fc0` | `#b51c79` |

## Defects found by running the app

Putting tab colours only in a named scheme populated `resolved_palette` but
left the GUI tabs in their default colours on this stable version. `apply`
now also assigns `config.colors.tab_bar`. Fancy tab-bar background colours
come from `window_frame`; merge those colours while retaining font/size and
border geometry. Theme the inactive tab edge as well.

Existing explicit `config.colors` selection overrides take precedence over
the scheme. The installation guide now tells users to remove conflicting old
theme overrides, without replacing their whole configuration.

## Limits

`auto` selected the light scheme matching `wezterm.gui.get_appearance()`.
However, XFCE had no `org.freedesktop.portal.Settings` appearance service;
WezTerm logged the unavailable portal. Real desktop dark/light transitions
are **not verified**. Use fixed mode on such a desktop. macOS, Windows and
Wayland are also untested. This test does not establish GPU acceleration.

## Repeat safely

1. Back up any existing config and same-named module. Install the generated
   `dist/wezterm/miami-cruise.lua` beside the config.
2. Use `wezterm --config-file /absolute/scratch/test.lua start
   --always-new-process` with a disposable fixture, rather than a personal
   shell or history. Record the version and effective palette from a
   `window-config-reloaded` callback.
3. Exercise the states above, including both tab-bar styles and a real
   `MIAMI_CRUISE` process environment override. Use the GUI process's own
   `WEZTERM_UNIX_SOCKET` for CLI operations, not an unrelated mux server.
4. For an independent palette check, send OSC 10/11/12 and OSC 4 queries from
   a raw terminal, using BEL terminators, then restore terminal attributes.
5. Capture the same real window in both variants with no private output.
   Crop to the terminal UI (including tabs and splits), excluding desktop
   panels, window-manager title bars and desktop overlays. The published
   captures are matched 1880 × 960 crops; uncropped originals are retained
   outside the repository.
   Import using `previews/wezterm/render.sh dark.png light.png`. The old
   `mock.py`/`palette.png` are historical mock assets, not the live previews.
6. Close only test-owned panes/processes, run the full build, verify download
   contents and repeat-build hashes. Do not claim system switching from a
   forced palette reload.
