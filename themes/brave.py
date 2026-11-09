"""Chromium theme packages for Brave's browser chrome (not web pages)."""
import json
import zipfile

from palette import VERSION, contrast, rgb


def manifest(variant, p):
    # Keys are supported by Chromium's BrowserThemePack. Brave's New Tab Page
    # has separate background controls, so do not imply this themes that page.
    roles = {
        'frame': 'panel',
        'frame_inactive': 'panel',
        'background_tab': 'panel',
        'background_tab_inactive': 'panel',
        'toolbar': 'bg',
        'tab_text': 'accent',
        'tab_background_text': 'muted',
        'tab_background_text_inactive': 'muted',
        'bookmark_text': 'text',
        'toolbar_text': 'text',
        'toolbar_button_icon': 'text',
        'omnibox_background': 'hover',
        'omnibox_text': 'text',
    }
    for foreground, background in (
        ('tab_text', 'toolbar'), ('tab_background_text', 'frame'),
        ('bookmark_text', 'toolbar'), ('toolbar_button_icon', 'toolbar'),
        ('omnibox_text', 'omnibox_background'),
    ):
        ratio = contrast(p[roles[foreground]], p[roles[background]])
        if ratio < 4.5:
            raise ValueError(f'Brave {variant}: {foreground} on {background} is {ratio:.2f}:1')
    return {
        'manifest_version': 3,
        'name': f'Miami Cruise {variant.title()} for Brave',
        'version': VERSION,
        'description': f'Miami Cruise {variant} colours for Brave tabs, toolbar and address bar.',
        'theme': {'colors': {key: list(rgb(p[token])) for key, token in roles.items()}},
    }


GUIDE = dict(
    name='Brave', category='Browser', order=70, mono='brv', text_badge=True,
    tags=['Browser', 'Chromium'], aliases='brave chrome chromium browser tabs toolbar address bar',
    status='Local loading verified in Brave 156 on Linux; visible chrome not yet checked',
    tagline='Miami Cruise colours for Brave tabs, toolbar and address bar.',
    files_heading='Choose one variant:',
    files=[(f'brave/miami-cruise-brave-{v}.zip', f'miami-cruise-brave-{v}.zip',
            f'Brave/Chromium theme · {v}') for v in ('dark', 'light')],
    download_intro='Choose Dark or Light and download that ZIP from this page.',
    download_cli=False,
    file_note='Each ZIP contains a native Chromium theme manifest and the MIT licence. There are no scripts, extension permissions or web-page modifications. Keep the extracted folder after installing it.',
    shots=[(f'brave/{v}.svg', f'Illustrative {v} Brave browser-chrome preview; web-page content is unchanged')
           for v in ('dark', 'light')],
    tested='Brave Browser 156.1.98.60 on Linux: both ZIPs extracted and each recorded as the active theme in a separate isolated headless profile. Visible browser chrome, persistence and macOS/Windows installation not verified',
    variants='Separate dark and light theme packages; manual switching',
    covers='Browser frame, active/inactive tabs, toolbar icons and text, bookmarks and address bar',
    glow='No: a flat palette',
    steps=[
        ('Extract your chosen ZIP', [
            ('p', 'Extract the dark or light ZIP to a permanent folder. Open the extracted folder and check that <code>manifest.json</code> is directly inside it. Do not select the ZIP itself or the parent folder.'),
        ]),
        ('Load the theme in Brave', [
            ('p', 'Open <code>brave://extensions</code>, enable <b>Developer mode</b>, choose <b>Load unpacked</b>, and select the folder containing <code>manifest.json</code>. The browser chrome should update immediately. This local-install flow is for desktop Brave.'),
            ('note', 'Brave may show a developer-mode warning for locally loaded themes. The ZIP contains only a colour manifest and a licence file; it does not request permissions or run code.'),
        ]),
        ('Switch or remove', [
            ('p', 'To change between dark and light, load the other extracted folder through <code>brave://extensions</code>. Only one browser theme can be active at a time; switching is manual. To remove Miami Cruise, open <code>brave://extensions</code> and remove its theme, or reset the theme in <code>brave://settings/appearance</code>.'),
            ('note', 'This colours Brave\'s browser chrome, not websites. Brave\'s New Tab background and some built-in UI surfaces have their own controls and may not follow these theme colours. The theme does not automatically follow your OS dark/light setting.'),
        ]),
    ],
)


def export(pals, dist):
    out = dist / 'brave'
    out.mkdir(parents=True, exist_ok=True)
    licence = (out.parent.parent / 'LICENSE').read_bytes()
    for variant in ('dark', 'light'):
        p = pals[variant][0]
        body = (json.dumps(manifest(variant, p), indent=2) + '\n').encode()
        source = out / variant
        source.mkdir(parents=True, exist_ok=True)
        (source / 'manifest.json').write_bytes(body)
        archive = out / f'miami-cruise-brave-{variant}.zip'
        with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
            for name, data in (('manifest.json', body), ('LICENSE', licence)):
                info = zipfile.ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o644 << 16
                z.writestr(info, data)
