"""Candy-derived icon theme. All painting is generated; upstream geometry stays intact."""
import colorsys
import gzip
import hashlib
import io
import json
import posixpath
import re
import tarfile
import xml.etree.ElementTree as ET
from pathlib import Path

from palette import build_palette

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'vendor/candy'
CONTEXTS = ('apps', 'devices', 'mimetypes', 'places', 'preferences', 'status')
SVG = 'http://www.w3.org/2000/svg'
XLINK = 'http://www.w3.org/1999/xlink'
ET.register_namespace('', SVG)
ET.register_namespace('xlink', XLINK)
PAINT = re.compile(r'url\([^)]*\)|#[0-9a-fA-F]{6}\b|#[0-9a-fA-F]{3}\b|rgba?\([^)]*\)|\b(?:white|black)\b')


def upstream():
    """Read the pinned archive without extracting any upstream paths or symlinks."""
    metadata = json.loads((BASE/'upstream.json').read_text())
    data = (BASE/'upstream.tar.gz').read_bytes()
    if hashlib.sha256(data).hexdigest() != metadata['sha256']:
        raise ValueError('Candy source checksum mismatch')
    with tarfile.open(fileobj=io.BytesIO(data)) as archive:
        prefix = archive.getmembers()[0].name + '/'
        members = {m.name.removeprefix(prefix): m for m in archive.getmembers()}
        files, links = {}, {}
        for name, m in members.items():
            if name.split('/')[0] not in CONTEXTS or m.isdir():
                continue
            if name.startswith('/') or '..' in Path(name).parts:
                raise ValueError(name)
            if m.isfile():
                files[name] = archive.extractfile(m).read()
            elif m.issym():
                target = posixpath.normpath(posixpath.join(posixpath.dirname(name), m.linkname))
                if target.startswith('/') or '..' in Path(target).parts:
                    raise ValueError(name)
                links[name] = target
            else:
                raise ValueError('Unexpected source member: '+name)
        resolved = {}
        for name in links:
            target, seen = name, set()
            while target in links:
                if target in seen:
                    raise ValueError('Alias cycle: '+name)
                seen.add(target)
                target = links[target]
            if target not in files:
                raise ValueError('Missing alias target: '+name)
            resolved[name] = target
        index = archive.extractfile(prefix+'index.theme').read().decode()
    return files, resolved, index


def icon_role(name):
    """Specific semantic roles override decorative hue mapping."""
    stem = Path(name).stem.lower()
    if any(s in stem for s in ('error', 'danger', 'battery-caution')):
        return 'danger'
    if any(s in stem for s in ('warning', 'battery-low')):
        return 'warning'
    if any(s in stem for s in ('success', 'emblem-default', 'network-transmit-receive')):
        return 'success'
    if name.startswith('places/'):
        if any(s in stem for s in ('favorite', 'favourite', 'important')):
            return 'accent'
        if stem.startswith('folder') or stem in ('user-home', 'user-desktop'):
            return 'info'
    if 'thunar' in stem or stem in ('system-file-manager', 'file-manager'):
        return 'info'
    if stem in ('vlc', 'vlc-xmas'):
        return 'warning'
    if stem in ('application-pdf', 'acroread'):
        return 'danger'
    return None


def recolor(data, name, p):
    tree = ET.fromstring(data)
    # Strip editor state (which can contain workstation paths), not drawing geometry.
    # Full originals, metadata and licensing are retained in corresponding source.
    for parent in list(tree.iter()):
        for child in list(parent):
            if not child.tag.startswith('{'+SVG+'}') or child.tag == '{'+SVG+'}metadata':
                parent.remove(child)
        for attr in list(parent.attrib):
            if attr.startswith('{') and not attr.startswith('{'+XLINK+'}'):
                del parent.attrib[attr]
    dark = build_palette('dark')[0]
    light = build_palette('light')[0]
    override = icon_role(name)

    def paint(match):
        value = match[0]
        if value.startswith('url('):
            return value
        if value in ('black', 'white'):
            value = '#000000' if value == 'black' else '#ffffff'
        if value.startswith('rgb'):
            channels = value[value.index('(')+1:-1].split(',')
            if len(channels) not in (3, 4):
                return value
            rgb = [float(c.strip().rstrip('%')) / (100 if '%' in c else 255) for c in channels[:3]]
            alpha = channels[3].strip() if len(channels) == 4 else None
        else:
            raw = value[1:]
            if len(raw) == 3:
                raw = ''.join(c*2 for c in raw)
            rgb = [int(raw[i:i+2], 16)/255 for i in (0, 2, 4)]
            alpha = None
        h, l, s = colorsys.rgb_to_hls(*rgb)
        if s < .14:
            # Preserve light/dark structure, including neutral details and shadows.
            if p['bg'] == dark['bg']:
                color = p['text' if l > .8 else 'muted' if l > .48 else 'border' if l > .23 else 'bg']
            else:
                color = p['bg' if l > .8 else 'disabled' if l > .48 else 'muted' if l > .23 else 'text']
        else:
            hue = h*360
            role = override or ('danger' if name.startswith('status/') and (hue < 20 or hue > 345) else 'accent' if hue < 20 or hue > 280 else 'warning' if hue < 70 else 'success' if hue < 170 else 'info')
            # Dark retains the approved pastel study. Light needs darker strokes.
            color = (dark if l >= .48 else light)[role]
            if p['bg'] != dark['bg'] and not name.startswith('places/48/'):
                # A restrained ink blend preserves gradient variation while keeping
                # every endpoint at least as dark as the light palette role.
                weight = max(0, min(.30, (.80-l)*.55))
                color = '#' + ''.join(f'{round(int(light[role][i:i+2],16)*(1-weight)+int(light["text"][i:i+2],16)*weight):02x}' for i in (1,3,5))
        if alpha is not None:
            r, g, b = (int(color[i:i+2], 16) for i in (1, 3, 5))
            return f'rgba({r},{g},{b},{alpha})'
        return color

    for node in tree.iter():
        for attr, value in list(node.attrib.items()):
            if attr in ('style', 'fill', 'stroke', 'stop-color', 'color', 'flood-color', 'lighting-color'):
                node.set(attr, PAINT.sub(paint, value))
        if node.tag == '{'+SVG+'}style' and node.text:
            node.text = PAINT.sub(paint, node.text)
    # Candy's solid generic folder uses a transparent highlight. Give its body the
    # same role gradient as other folders, with dark ink on the pastel face.
    if override and name.startswith('places/') and '/48/' in name:
        for node in tree.iter('{'+SVG+'}path'):
            if node.get('id') == 'path4':
                defs = ET.SubElement(tree, '{'+SVG+'}defs')
                grad = ET.SubElement(defs, '{'+SVG+'}linearGradient', id='miami-body', x1='0', y1='0', x2='1', y2='1')
                ET.SubElement(grad, '{'+SVG+'}stop', offset='0', attrib={'stop-color':light[override]})
                ET.SubElement(grad, '{'+SVG+'}stop', offset='1', attrib={'stop-color':dark[override]})
                node.set('style', re.sub(r'fill:[^;]+', 'fill:url(#miami-body)', node.get('style', '')))
        # White emblems stay readable against the shared pastel folder gradient.
        for node in tree.iter('{'+SVG+'}path'):
            for attr in ('style', 'fill'):
                if attr in node.attrib:
                    node.set(attr, node.attrib[attr].replace(p['text'] if p['bg'] == dark['bg'] else p['bg'], dark['on-accent']))
    return b'<!-- Miami Cruise colour adaptation of Candy; GPL-3.0; shapes retained. -->\n'+ET.tostring(tree, encoding='utf-8')+b'\n'


def package_files(p, variant):
    originals, aliases, index = upstream()
    name = 'Miami-Cruise-Candy-'+variant.title()
    files = {path: recolor(data, path, p) for path, data in originals.items()}
    # Materialise aliases as regular files: portable archives, no unsafe extraction links.
    files.update({path: files[target] for path, target in aliases.items()})
    index = re.sub(r'^Name=.*$', 'Name='+name, index, flags=re.M)
    index = re.sub(r'^Comment=.*$', 'Comment=Miami Cruise palette; Candy artwork and gradients', index, flags=re.M)
    index = re.sub(r'^Inherits=.*$', 'Inherits='+('Adwaita,hicolor' if variant=='light' else 'breeze-dark,Adwaita,hicolor'), index, flags=re.M)
    files['index.theme'] = index.encode()
    for path in ('LICENSE', 'README.md', 'upstream.json'):
        files[path] = (BASE/path).read_bytes()
    files['CHANGES.md'] = (
        '# Miami Cruise changes\n\nCandy artwork by EliverLara and contributors. '
        'Colour adaptation by Miami Cruise, 2026-11-24, GPL-3.0.\n\n'
        'SVG geometry, aliases and embedded raster artwork preserved. Paint uses '
        'Miami Cruise tokens; gradients/transparency introduce intermediate colours. '
        'Editor metadata removed. Aliases materialised as regular SVG files. '
        'Dark/light variants adjust neutral paint and fallback inheritance; '
        'Dark chromatic gradients follow the approved colour study; Light uses darker palette-derived strokes. '
        'Four embedded bitmap images remain unchanged. No endorsement by app vendors implied.\n'
    ).encode()
    return name, files


def source_files():
    files = {str(p.relative_to(ROOT)):p.read_bytes() for p in BASE.iterdir() if p.is_file()}
    for name in ('LICENSE', 'palette.py', 'themes/icons.py'):
        files[name] = (ROOT/name).read_bytes()
    files['themes/__init__.py'] = b''
    files['build.py'] = b"from pathlib import Path\nimport sys\nsys.path.insert(0,str(Path(__file__).resolve().parent))\nfrom palette import PALETTES, build_palette\nfrom themes.icons import export\nexport({v:build_palette(v) for v in PALETTES},Path(__file__).resolve().parent/'dist')\n"
    return files


def export(pals, dist):
    out = dist/'icons'
    out.mkdir(parents=True, exist_ok=True)
    packages = [package_files(p, v) for v, (p, _) in pals.items()]
    packages.append(('miami-cruise-candy-source', source_files()))
    for name, files in packages:
        with (out/f'{name}.tar.gz').open('wb') as raw:
            with gzip.GzipFile(filename='', mode='wb', fileobj=raw, mtime=0) as gz:
                with tarfile.open(fileobj=gz, mode='w', format=tarfile.PAX_FORMAT) as archive:
                    for path, data in sorted(files.items()):
                        info = tarfile.TarInfo(name+'/'+path)
                        info.mode = 0o644
                        info.size = len(data)
                        info.mtime = 1767225600
                        archive.addfile(info, io.BytesIO(data))


GUIDE = dict(
    name='Candy icons', category='Desktop', mono='IC', tags=['SVG','Candy','Icons'],
    aliases='candy icons folders desktop xfce linux',
    status='Native rendering and isolated XFCE desktop checks passed; user testing pending',
    tagline='Candy’s expressive shapes and gradients, recoloured with the Miami Cruise palette.',
    files=[(f'icons/Miami-Cruise-Candy-{v}.tar.gz',f'Miami-Cruise-Candy-{v}.tar.gz',f'{v} icon theme') for v in ('Dark','Light')]+[('icons/miami-cruise-candy-source.tar.gz','miami-cruise-candy-source.tar.gz','Corresponding source · GPL-3.0')],
    shots=[(f'icons/{v}.png',f'Candy-derived Miami Cruise icon gallery · {v} · synthetic content') for v in ('dark','light')],
    file_note='Choose Dark or Light to match your desktop, or download both. The source archive is optional and only needed for rebuilding the themes.',
    tested='Both styles reviewed on an isolated Arch Linux/XFCE 4.20 desktop, including Thunar, panel/menu icons, selections and small/large sizes. Native SVG loading and reproducible packages checked; HiDPI and other desktops not yet verified',
    covers='3,860 application, device, file-type, folder, settings and status icon names. Four embedded bitmap images retain their original colours',
    glow='Original gradients and transparency, with palette-derived endpoints; Light strokes use a restrained ink blend for readability',
    license_label='Candy licence and attribution', license_path='vendor/candy/README.md',
    steps=[('Install the icon theme',[
        ('p','Extract your chosen download into your user icon directory. Back up any existing same-named folder first, including its target if it is a symlink. No root access is needed.'),
        ('code',[(None,'bash','icon_dir="${XDG_DATA_HOME:-$HOME/.local/share}/icons"\nmkdir -p "$icon_dir"\ntar -xzf Miami-Cruise-Candy-Dark.tar.gz -C "$icon_dir"\ntar -xzf Miami-Cruise-Candy-Light.tar.gz -C "$icon_dir"')]),
        ('note','Run only the command for each variant you downloaded. Icon selection is separate from your desktop style; fonts, wallpaper, cursors and panel layout stay unchanged.'),
    ]),('Update the icon cache',[
        ('p','After installing or updating the theme, refresh its icon cache. This is recommended for GTK applications, though they can load icons without it. Run the command for each variant you installed.'),
        ('code',[(None,'bash','gtk-update-icon-cache -f "$icon_dir/Miami-Cruise-Candy-Dark"\ngtk-update-icon-cache -f "$icon_dir/Miami-Cruise-Candy-Light"')]),
        ('note','Use the same icon_dir as in the extraction step. If gtk-update-icon-cache is unavailable, your distribution’s GTK icon-cache utility provides it. You do not need sudo for themes in your user icon directory.'),
    ]),('Select your icons',[
        ('p','In XFCE, open Settings → Appearance → Icons. Record your previous icon theme, then select Miami-Cruise-Candy-Dark or Miami-Cruise-Candy-Light. On other Linux desktops, use the icon-theme setting in your appearance preferences.'),
        ('note','If the theme is missing, reopen Appearance. After an update, refresh the cache, switch to another icon theme and back, and reopen apps that still show old icons. Some apps use their own artwork; missing icons use your system’s fallback themes.'),
    ]),('Restore your previous icons',[
        ('p','Select your recorded previous icon theme before removing Miami Cruise. Remove only unchanged installation-owned folders, or restore backed-up same-named folders. Preserve later edits, existing symlinks and unrelated themes. No change to GTK or window-decoration settings is required.'),
        ('note','Based on Candy by EliverLara and contributors: https://github.com/EliverLara/candy-icons. Modified artwork, licence and corresponding source are supplied under GPL-3.0. Brand names and marks belong to their respective owners; inclusion does not imply endorsement.'),
    ])],
)
