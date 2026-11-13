"""OpenClaw native personal theme definition, not CSS injection or a plugin."""
import json

from palette import contrast

# OpenClaw's native 19 semantic colours. Both modes use the shared palette.
ROLES = {
    'background': 'bg', 'foreground': 'text',
    'card': 'panel', 'card-foreground': 'text',
    'popover': 'panel', 'popover-foreground': 'text',
    'primary': 'accent', 'primary-foreground': 'on-accent',
    'secondary': 'hover', 'secondary-foreground': 'text',
    'muted': 'panel', 'muted-foreground': 'muted',
    'accent': 'accent', 'accent-foreground': 'on-accent',
    'destructive': 'danger', 'destructive-foreground': 'on-accent',
    'border': 'border', 'input': 'border', 'ring': 'focus',
}


def definition(pals):
    result = {
        'name': 'Miami Cruise',
        'description': 'Teal-ink surfaces, one magenta hero and clear semantic colours. The Miami Cruise collection palette, in dark and light.',
    }
    for variant, (p, _) in pals.items():
        colors = {key: p[token] for key, token in ROLES.items()}
        for fg, bg in [('foreground', 'background'), ('card-foreground', 'card'),
                       ('popover-foreground', 'popover'), ('primary-foreground', 'primary'),
                       ('secondary-foreground', 'secondary'), ('muted-foreground', 'muted'),
                       ('accent-foreground', 'accent'), ('destructive-foreground', 'destructive')]:
            if contrast(colors[fg], colors[bg]) < 4.5:
                raise ValueError(f'OpenClaw {variant}: {fg} on {bg} is below 4.5:1')
        result[variant] = colors
    if len(json.dumps(result, separators=(',', ':')).encode()) > 4096:
        raise ValueError('OpenClaw theme exceeds the native definition size limit')
    return result


GUIDE = dict(
    name='OpenClaw', category='Browser & web', mono='OC',
    tags=['Web UI', 'Native JSON'], aliases='openclaw control ui webgui dashboard personal theme',
    status='User import verified; illustrative previews',
    tagline='Miami Cruise for the OpenClaw Control UI, with native dark and light palettes.',
    files=[('openclaw/miami-cruise.json', 'miami-cruise.json', 'Native personal theme · dark and light')],
    shots=[(f'openclaw/{mode}.png', f'Illustrative {mode} OpenClaw UI with native theme colours and synthetic content; not a live-session capture') for mode in ('dark', 'light')],
    tested='OpenClaw 2026.11.3 native theme parser, complete dark/light semantic palettes and text contrast checks. User reported successful agent import on 2026-11-13; exact runtime version and mode coverage not recorded. Previews are offline illustrations, not native component captures or proof of live rendering',
    covers='Native page, card, popover, primary/secondary controls, muted text, accent, destructive actions, borders, inputs and focus ring tokens',
    glow='OpenClaw derives its own hover, selection and focus effects from the native colours; no custom glow stylesheet',
    file_note='Both dark and light palettes are included. Miami Cruise changes the interface colours and is separate from OpenClaw’s built-in Miami theme.',
    download_first=False,
    steps=[('Add Miami Cruise', [
        ('p', 'Paste this prompt into your OpenClaw chat. Your agent will download and add the theme for you.'),
        ('code', [(None, 'text', 'Download this native OpenClaw theme definition from the website and import it as a personal theme with id miami-cruise:\nhttps://lanjelin.github.io/miami-cruise/downloads/openclaw/miami-cruise.json\nRead my current theme and mode first. Preserve any existing user/miami-cruise definition before replacing it. Save the new definition with apply=false; do not change my appearance yet.')]),
        ('p', 'Your current appearance stays unchanged until you select the theme.'),
    ]), ('Select dark, light or system mode', [
        ('p', 'Open Settings → Appearance and select Miami Cruise, then choose Dark, Light or System. You can also ask your agent to select the theme and your preferred mode.'),
        ('note', 'System mode follows your device’s appearance. Any custom accent colour you have set may override the theme’s accent.'),
    ]), ('Restore your previous appearance', [
        ('p', 'Choose your previous theme in Settings → Appearance, or ask your agent to restore your previous appearance.'),
        ('note', 'More about appearance settings: https://docs.openclaw.ai/web/control-ui/settings#appearance-themes'),
    ])],
)


def export(pals, dist):
    out = dist / 'openclaw'
    out.mkdir(parents=True, exist_ok=True)
    (out / 'miami-cruise.json').write_text(json.dumps(definition(pals), indent=2) + '\n')
