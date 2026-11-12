# Agent playbook: Glow

Follow [INSTALL.md](../../INSTALL.md), the [human guide](../../dist/glow/README.md)
and [source metadata](../../themes/glow.py). These artifacts style Markdown output,
not the entire TUI or terminal.

## Discover

- Identify Glow/version, the actual `glow.yml`, launcher `--config`/`-s` flags,
  wrappers, and relevant style environment settings. Use safe read-only inspection;
  `glow config` opens an editor and is not a discovery-only operation. Glow 3.0.0
  also created config/cache files on `glow --help` in the container test; do not
  assume help is read-only.
- Read the existing style, pager, width and other settings. Confirm the directory
  for permanent custom JSON files, symlinks and any managed config source.
- Establish dark/light preference and whether use is direct terminal rendering,
  redirected output or the TUI. Do not assume those contexts select styles alike.
  Follow the detected version's documented precedence rather than inventing a
  universal environment-variable fallback.

## Propose and apply after approval

Copy the native JSON styles without overwriting unrelated files. Choose a fixed
variant; Glow's built-in automatic style does not switch between our custom files.
For persistence, merge only the approved `style` key in the existing config, or
agree a launcher override. Preserve pager/width/mouse and other choices. Replacing
a different custom stylesheet is an explicit selection, not a stylesheet merge.

No bat cache, patched Glow binary or extra syntax-highlighting dependency is needed.
Do not change the terminal background or attempt to theme browser/help chrome as
part of installing these Markdown styles.

## Verify and restore

Render a small local, synthetic Markdown document. Do not fetch remote documents
or automatically launch a configured pager. Compare direct terminal/TUI use with
redirected output when relevant; explicit `-s` may be necessary, as described by
the version's native behaviour. Fenced-code colours can be quantized to 256 colours:
that alone is not a failed palette install. Include any state/config writes from
launches in the approved verification scope.

Restore the former style key/launcher/environment edit with conflict checking;
remove it only if it was absent before this run. Preserve other Glow settings.
Detach style references before removing unchanged new JSON files. Explain any
restart/reload still required; do not reset the whole config to defaults.
