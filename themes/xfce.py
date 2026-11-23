"""Draft GTK3/Xfwm4 desktop port, retaining Greybird's widget geometry."""
import colorsys
import gzip
import io
import re
import tarfile
from pathlib import Path
from palette import rgb
from ._xfce_assets import recolor_png, xpm_to_png, window_button

BASE = Path(__file__).resolve().parents[1] / 'vendor/greybird'


def mapper(p, variant):
    # Preserve the base's tonal hierarchy; chromatic upstream blues become our
    # hero accent, while status colours retain their semantic role. No new hues.
    anchors = ([(0,'panel'),(34,'panel'),(45,'bg'),(59,'row'),(80,'hover'),
                (104,'border'),(140,'disabled'),(185,'muted'),(238,'text'),(255,'text')]
               if variant == 'dark' else
               [(0,'text'),(33,'text'),(60,'muted'),(120,'disabled'),(160,'border'),
                (206,'panel'),(230,'hover'),(252,'bg'),(255,'bg')])
    def convert(c):
        h,l,s = colorsys.rgb_to_hls(*(v/255 for v in c))
        if s > .25 and max(c)-min(c)>24:
            hue = h*360
            role = ('danger' if hue < 20 or hue > 345 else 'warning' if hue < 70
                    else 'success' if hue < 175 else 'accent' if hue < 280 else 'orchid')
            return rgb(p[role])
        level = sum(c)/3
        for (a,x),(b,y) in zip(anchors,anchors[1:]):
            if level <= b:
                t = max(0,(level-a)/(b-a))
                return tuple(round(u+(v-u)*t) for u,v in zip(rgb(p[x]),rgb(p[y])))
        return rgb(p['text'])
    return convert


def recolor_text(text, convert):
    def hexcolor(m):
        h=m[0][1:]
        if len(h)==3: h=''.join(x*2 for x in h)
        return '#%02x%02x%02x' % convert(tuple(bytes.fromhex(h)))
    text = re.sub(r'#[0-9a-fA-F]{6}\b|#[0-9a-fA-F]{3}\b', hexcolor, text)
    def rgba(m):
        c=tuple(int(m[i]) for i in (1,2,3))
        # Preserve translucent white/black lighting and shadows.
        out = c if len(set(c))==1 and c[0] in (0,255) else convert(c)
        return f'rgba({out[0]}, {out[1]}, {out[2]}, {m[4]})'
    return re.sub(r'rgba\(\s*(\d+),\s*(\d+),\s*(\d+),\s*([\d.]+)\)',rgba,text)


def overrides(p):
    lines = ['/* Miami Cruise semantic overrides; Greybird geometry retained. */']
    roles = {'theme_bg_color':'bg','theme_fg_color':'text','theme_base_color':'panel',
             'theme_text_color':'text','theme_selected_bg_color':'accent',
             'theme_selected_fg_color':'on-accent','insensitive_fg_color':'disabled',
             'warning_color':'warning','error_color':'danger','success_color':'success',
             'link_color':'info','borders':'border',
             'insensitive_bg_color':'row','insensitive_base_color':'row',
             'theme_unfocused_fg_color':'text','theme_unfocused_text_color':'text',
             'theme_unfocused_bg_color':'bg','theme_unfocused_base_color':'panel',
             'theme_unfocused_selected_bg_color':'accent','theme_unfocused_selected_fg_color':'on-accent',
             'unfocused_borders':'border','content_view_bg':'panel',
             'wm_title':'text','wm_unfocused_title':'muted','wm_bg_a':'panel','wm_bg_b':'panel',
             'wm_button_hover_color_a':'hover','wm_button_hover_color_b':'hover',
             'wm_button_active_color_a':'accent','wm_button_active_color_b':'accent','wm_button_active_color_c':'accent'}
    lines += [f'@define-color {key} {p[val]};' for key,val in roles.items()]
    for selector, styles in [
        ('window, .background', {'background-color':'bg','color':'text'}),
        ('headerbar, .titlebar, .xfce4-panel', {'background-color':'panel','color':'text'}),
        ('entry, textview text, .view', {'background-color':'panel','color':'text'}),
        ('*:disabled', {'color':'disabled'}),
        ('selection, *:selected, *:selected:focus, button.suggested-action, button:checked, check:checked, radio:checked', {'background-color':'accent','color':'on-accent','border-color':'accent'}),
        ('button.destructive-action', {'background-color':'danger','color':'on-accent','border-color':'danger'}),
        ('scale slider, .selection-handle', {'background-color':'accent','border-color':'accent'}),
        ('progressbar progress, scale highlight', {'background-color':'accent','border-color':'accent'}),
        ('*:link', {'color':'info'}),
        ('*:focus', {'outline-color':'focus'}),
    ]:
        lines.append(selector+' { '+ ' '.join(f'{k}: {p[v]};' for k,v in styles.items())+' background-image: none; }')
    lines += [
        'label { color: inherit; }',
        # xfdesktop uses its own CSS node, not GtkIconView's `iconview` node.
        # Keep wallpaper visible and give desktop labels explicit readable ink.
        f'XfdesktopIconView.view {{ background-color: transparent; background-image: none; color: {p["text"]}; }}',
        f'XfdesktopIconView.view.label, XfdesktopIconView.view.label:backdrop, XfdesktopIconView.view.label:hover {{ background-color: alpha({p["panel"]}, 0.90); border-radius: 3px; color: {p["text"]}; text-shadow: 0 1px 2px {p["panel"]}; }}',
        f'XfdesktopIconView.view.label:selected, XfdesktopIconView.view.label:selected:focus, XfdesktopIconView.view.label:selected:backdrop {{ background-color: {p["accent"]}; color: {p["on-accent"]}; text-shadow: none; }}',
        f'window.background:backdrop {{ color: {p["text"]}; }}',
        f'button:backdrop label {{ color: {p["text"]}; }}',
        f'button label, treeview header button label {{ color: {p["text"]}; }}',
        f'button.suggested-action label, button.suggested-action:backdrop label, button.destructive-action label, button.destructive-action:backdrop label, button:checked label {{ color: {p["on-accent"]}; }}',
        f'button:disabled, button:disabled label {{ color: {p["disabled"]}; }}',
        f'.view:selected, .view:selected:focus, .view:selected:backdrop {{ background-color: {p["accent"]}; color: {p["on-accent"]}; }}',
    ]
    # Pin semantic foreground/background pairs through focus transitions. The
    # upstream stylesheet has more-specific backdrop rules than generic labels.
    stable = [
        ('window.background, window.background:backdrop', 'bg', 'text'),
        ('.view, .view:backdrop, .view text, .view text:backdrop, iconview, iconview:backdrop, iconview text, iconview text:backdrop, textview text, textview text:backdrop, entry, entry:backdrop', 'panel', 'text'),
        ('menu, menu:backdrop, menubar, menubar:backdrop, menubar > menuitem, menubar > menuitem:backdrop, popover.background, tooltip.background', 'panel', 'text'),
        ('menu menuitem:hover, menu menuitem:selected, menubar > menuitem:hover', 'accent', 'on-accent'),
        ('.view:selected, .view:selected:focus, .view:selected:backdrop, iconview:selected, iconview:selected:backdrop, textview text selection, entry selection', 'accent', 'on-accent'),
        ('entry:disabled, entry:disabled:backdrop', 'row', 'disabled'),
    ]
    for selectors,bg,fg in stable:
        lines.append(selectors+f' {{ background-color: {p[bg]}; color: {p[fg]}; background-image: none; text-shadow: none; }}')
    lines.append(f'menu menuitem:hover label, menu menuitem:selected label {{ color: {p["on-accent"]}; text-shadow: none; }}')
    lines.append('label:backdrop { color: inherit; }')
    lines.append(f'tooltip, tooltip.background, tooltip label, tooltip label:backdrop {{ color: {p["text"]}; text-shadow: none; }}')
    for kind, bg in (('', 'row'), (':hover','hover'), (':active','accent'), (':checked','accent')):
        fg='on-accent' if kind in (':active',':checked') else 'text'
        selectors=[f'window.background button{kind}{back}' for back in ('',':backdrop')]
        lines.append(', '.join(selectors)+f' {{ background-color: {p[bg]}; color: {p[fg]}; background-image: none; border-color: {p["border"]}; text-shadow: none; }}')
        lines.append(', '.join(x+' label' for x in selectors)+f' {{ color: {p[fg]}; text-shadow: none; }}')
    for cls,bg in (('suggested-action','accent'),('destructive-action','danger')):
        selectors=[f'window.background button.{cls}{state}{back}' for state in ('',':hover',':active') for back in ('',':backdrop')]
        lines.append(', '.join(selectors)+f' {{ background-color: {p[bg]}; color: {p["on-accent"]}; background-image: none; text-shadow: none; }}')
        lines.append(', '.join(x+' label' for x in selectors)+f' {{ color: {p["on-accent"]}; text-shadow: none; }}')
    disabled=['label:disabled', 'label:disabled:backdrop']
    for cls in ('', '.suggested-action', '.destructive-action'):
        for active in ('',':active',':checked'):
            for backdrop in ('',':backdrop'):
                button=f'window.background button{cls}{active}:disabled{backdrop}'
                disabled.extend((button,button+' label'))
    lines.append(', '.join(disabled)+f' {{ color: {p["disabled"]}; text-shadow: none; }}')
    lines.append(f'window.background button:disabled, window.background button:disabled:backdrop {{ background-color: {p["row"]}; background-image: none; border-color: {p["border"]}; }}')

    lines += [
        f'notebook > header > tabs > tab, notebook > header > tabs > tab:backdrop {{ color: {p["muted"]}; background-color: {p["panel"]}; text-shadow: none; }}',
        f'notebook > header > tabs > tab label, notebook > header > tabs > tab:backdrop label {{ color: {p["muted"]}; }}',
        f'notebook > header > tabs > tab:checked, notebook > header > tabs > tab:checked:backdrop, notebook > header > tabs > tab:hover {{ color: {p["text"]}; background-color: {p["row"]}; }}',
        f'notebook > header > tabs > tab:checked label, notebook > header > tabs > tab:checked:backdrop label, notebook > header > tabs > tab:hover label {{ color: {p["text"]}; }}',
        f'scale slider, scale:backdrop slider, scale slider:hover {{ background-color: {p["muted"]}; border-color: {p["border"]}; background-image: none; }}',
        f'scale slider:active {{ background-color: {p["accent"]}; border-color: {p["focus"]}; }}',
    ]
    # Greybird's panel/tasklist assumes a dark panel even in its light theme.
    # Override both button fills and nested labels, including unfocused states.
    lines.append(f'.xfce4-panel.background {{ background-color: {p["panel"]}; background-image: none; color: {p["text"]}; text-shadow: none; -gtk-icon-shadow: none; }}')
    lines.append(f'.xfce4-panel.background label {{ color: {p["text"]}; text-shadow: none; }}')
    scopes = ('.xfce4-panel.background button', '.xfce4-panel.background .tasklist button')
    groups = [(['', ':backdrop'], 'panel', 'text'),
              ([':hover', ':hover:backdrop'], 'hover', 'text'),
              ([a+b+c for a in (':active', ':checked') for b in ('', ':hover') for c in ('', ':backdrop')], 'hover', 'text'),
              ([a+':disabled'+b for a in ('', ':active', ':checked') for b in ('', ':backdrop')], 'panel', 'disabled')]
    for states, bg, fg in groups:
        selectors = [scope+state for scope in scopes for state in states]
        lines.append(', '.join(selectors)+f' {{ background-color: {p[bg]}; background-image: none; color: {p[fg]}; text-shadow: none; box-shadow: none; }}')
        lines.append(', '.join(s+' label' for s in selectors)+f' {{ color: {p[fg]}; text-shadow: none; }}')
        if bg == 'hover' and any(':checked' in state for state in states):
            lines.append(', '.join(selectors)+f' {{ box-shadow: inset 0 -2px {p["accent"]}; }}')
    # Native panels retain their placement and plugins. Restrained rounding and
    # spacing soften the chrome without requiring a replacement dock or icons.
    lines += [
        f'.xfce4-panel.background {{ border: 1px solid {p["border"]}; border-radius: 6px; }}',
        # External plugin GtkPlugs share panel classes but are not panels.
        '#XfcePanelWindowWrapper { border: 0; border-radius: 0; box-shadow: none; }',
        '.xfce4-panel.background button { border-color: transparent; border-radius: 5px; margin: 1px 2px; padding: 2px 5px; }',
        '.xfce4-panel.background .launcher button { border-radius: 8px; padding: 4px; }',
        # The Actions plugin uses a named XfceArrowButton, including when hosted
        # externally without the ordinary panel CSS ancestry.
        f'#actions-button, #actions-button:backdrop {{ border-color: transparent; border-radius: 0; background-color: transparent; background-image: none; box-shadow: none; color: {p["text"]}; }}',
        f'#actions-button:hover, #actions-button:checked, #actions-button:active {{ background-color: {p["hover"]}; color: {p["text"]}; }}',
        f'#actions-button label {{ color: {p["text"]}; text-shadow: none; }}', 
        f'.xfce4-panel.background button:focus {{ outline-color: {p["focus"]}; outline-style: solid; outline-width: 2px; outline-offset: -3px; }}',
    ]
    # Keep hovered ancestor foregrounds out of nested submenus.
    # Popup labels can remain descendants of the panel or an active menu button.
    # Override those foreground rules explicitly, not just the popup container.
    for scope in ('menu', '.menu', '.context-menu', 'menubar'):
        for state, bg, fg in (('', 'panel', 'text'), (':hover', 'accent', 'on-accent'),
                              (':selected', 'accent', 'on-accent'), (':disabled', 'panel', 'disabled')):
            for back in ('', ':backdrop'):
                item = f'{scope} menuitem{state}{back}'
                for prefix in ('', '.xfce4-panel.background ', 'window.background '):
                    node = prefix + item
                    lines.append(node + f' {{ color: {p[fg]}; background-color: {p[bg]}; background-image: none; text-shadow: none; box-shadow: none; }}')
                    lines.append(', '.join(node+' > '+child for child in ('label', 'label:backdrop', 'accelerator', 'arrow', 'box label', 'box accelerator', 'box arrow')) + f' {{ color: {p[fg]}; text-shadow: none; }}')
    # Cover the view/cell itself as well as the label class used by cell renderers.
    # Explicit backdrop selectors must beat inherited .view:backdrop rules.
    for state in ('', ':hover', ':backdrop', ':hover:backdrop'):
        for cls in ('.view', '.view.cell', '.view.label', '.view.cell.label'):
            lines.append(f'XfdesktopIconView{cls}{state} {{ color: {p["text"]}; text-shadow: 0 1px 2px {p["panel"]}; }}')
            for selected in (':selected', ':selected:focus'):
                lines.append(f'XfdesktopIconView{cls}{selected}{state} {{ color: {p["on-accent"]}; text-shadow: none; }}')
    # Greybird's dark slider gradients collapse into the track after mapping.
    # Define both halves explicitly, including backdrop and disabled variants.
    for checked in ('', ':checked'):
        for hover in ('', ':hover'):
            for back in ('', ':backdrop'):
                for disabled in ('', ':disabled'):
                    node = 'switch' + checked + hover + back + disabled
                    active = bool(checked) and not disabled
                    track = 'accent' if active else 'row'
                    thumb = 'disabled' if disabled else 'on-accent' if active else 'muted'
                    lines.append(node + f' {{ background-color: {p[track]}; background-image: none; border-color: {p["muted"]}; box-shadow: none; }}')
                    lines.append(node + f' slider {{ background-color: {p[thumb]}; background-image: none; border-color: {p[thumb]}; box-shadow: none; }}')
    # Keep small interactive targets and keyboard focus visible in either mode.
    lines += [
        f'entry, entry:backdrop {{ border-color: {p["border"]}; }}',
        f'entry:focus, spinbutton:focus {{ border-color: {p["focus"]}; box-shadow: inset 0 0 0 1px {p["focus"]}; }}',
        f'button:focus, checkbutton:focus, radiobutton:focus, switch:focus, notebook tab:focus {{ outline-color: {p["focus"]}; outline-style: solid; outline-width: 2px; outline-offset: -3px; }}',
        f'scrollbar slider, scrollbar slider:backdrop {{ background-color: {p["muted"]}; background-image: none; border-color: transparent; box-shadow: none; }}',
        f'scrollbar slider:hover, scrollbar slider:hover:backdrop, scrollbar slider:active {{ background-color: {p["accent"]}; }}',
        f'scrollbar slider:disabled, scrollbar slider:disabled:backdrop {{ background-color: {p["border"]}; }}',
    ]
    # xfdesktop adds .rubberband to the view itself, not a child node. Keep
    # ordinary view/selection fills from making this drag overlay opaque.
    lines.append(f'XfdesktopIconView.view.rubberband, XfdesktopIconView.view.rubberband:active, XfdesktopIconView.view.rubberband:selected, XfdesktopIconView.view.rubberband:backdrop {{ background-color: alpha({p["accent"]}, 0.20); background-image: none; border: 1px solid {p["accent"]}; border-radius: 0; box-shadow: none; }}')
    return '\n'.join(lines)+'\n'


def package_files(p, variant):
    if variant == 'dark':
        # Desktop chrome needs raised surfaces, unlike recessed terminal panels.
        # Reuse existing spec colours locally; never change the shared palette.
        p = dict(p, panel=p['row'], row=p['hover'], hover=p['border'])
    convert = mapper(p,variant)
    files = {}
    css = recolor_text((BASE/f'gtk-3.0/base-{variant}.css').read_text(),convert)
    # Upstream blanket-dims every descendant in an unfocused Thunar window,
    # overriding view/menu semantics and making light-mode filenames unreadable.
    css = re.sub(r'\.thunar grid :backdrop\s*\{[^}]*\}', '', css)
    # A single package is a fixed variant, even when an app requests dark CSS.
    files['gtk-3.0/gtk-dark.css'] = b'@import url("gtk.css");\n'
    files['gtk-3.0/settings.ini'] = b'[Settings]\ngtk-button-images=0\ngtk-menu-images=0\n'
    for source in sorted((BASE/'gtk-3.0/assets').iterdir()):
        if source.suffix == '.png': data = recolor_png(source.read_bytes(),convert)
        elif source.suffix == '.svg': data = recolor_text(source.read_text(),convert).encode()
        else: continue
        files['gtk-3.0/assets/'+source.name] = data
    # Some historical Greybird rules refer to assets absent from its own
    # snapshot. Use real 1x artwork where possible and native CSS for handles.
    css = css.replace('checkbox-checked-selectionmode', 'checkbox-checked-active-selectionmode')
    def scaled(m):
        urls = re.findall(r'url\([\'"]?(assets/[^)\'" ]+)',m[0])
        if all('gtk-3.0/'+u in files for u in urls): return m[0]
        available = [u for u in urls if 'gtk-3.0/'+u in files]
        return 'url("'+available[0]+'")' if available else 'none'
    css = re.sub(r'-gtk-scaled\((?:[^()]|\([^()]*\))*\)',scaled,css)
    css = re.sub(r'url\([\'"]?(assets/[^)\'" ]+)[\'"]?\)',
                 lambda m: m[0] if 'gtk-3.0/'+m[1] in files else 'none',css)
    files['gtk-3.0/gtk.css'] = ('/* Miami Cruise draft; Greybird derivative, GPL-2.0-or-later. */\n'+css+'\n'+overrides(p)).encode()
    # Recolour both native formats, including the PNG-only base artwork.
    def wmconvert(c):
        level = sum(c)/3
        # High-contrast title glyphs, quiet borders, flat panel-coloured fill.
        return rgb(p['text' if level < 146 else 'border' if level < 180 else 'panel'])
    # The vendored XPMs are light-source artwork: map their light surfaces to
    # the target panel and their dark details to target text in either variant.
    for source in sorted((BASE/'xfwm4').glob('*.xpm')):
        text = recolor_text(source.read_text(),wmconvert)
        text = re.sub(r' s (?:active|inactive)_color_\d+', '',text)
        text = re.sub(r'(?<=c )black\b', p['text'], text, flags=re.I)
        text = re.sub(r'(?<=c )white\b', p['panel'], text, flags=re.I)
        files['xfwm4/'+source.stem+'.png'] = xpm_to_png(text)
    for source in sorted((BASE/'xfwm4').glob('*.png')):
        if not source.with_suffix('.xpm').exists():
            files['xfwm4/'+source.name] = recolor_png(source.read_bytes(),wmconvert)
    # Replace inherited shaded symbols, retaining the native tile dimensions.
    for button in ('close','hide','maximize','maximize-toggled','menu','shade',
                   'shade-toggled','stick','stick-toggled'):
        for state in ('active','inactive','prelight','pressed'):
            files[f'xfwm4/{button}-{state}.png'] = window_button(p,button,state)
    themerc = (BASE/'xfwm4/themerc').read_text()
    themerc = re.sub(r'^(?:active|inactive)_text(?:_shadow)?_color=.*\n','',themerc,flags=re.M)
    themerc = re.sub(r'^title_shadow_(active|inactive)=true',r'title_shadow_\1=false',themerc,flags=re.M)
    themerc += f'\nactive_text_color={p["text"]}\ninactive_text_color={p["muted"]}\n'
    files['xfwm4/themerc'] = themerc.encode()
    name = f'Miami-Cruise-{variant.title()}'
    files['index.theme'] = f'[Desktop Entry]\nType=X-GNOME-Metatheme\nName={name}\nComment=Miami Cruise GTK3 and Xfwm4 draft\n\n[X-GNOME-Metatheme]\nGtkTheme={name}\n'.encode()
    for license in ('LICENSE.GPL','LICENSE.CC','README.md'):
        files[license] = (BASE/license).read_bytes()
    return name,files


def source_files():
    root = BASE.parents[1]
    files = {str(p.relative_to(root)): p.read_bytes() for p in BASE.rglob('*') if p.is_file()}
    for name in ('LICENSE','palette.py','themes/xfce.py','themes/_xfce_assets.py'):
        files[name] = (root/name).read_bytes()
    files['themes/__init__.py'] = b''
    files['build.py'] = b"from pathlib import Path\nimport sys\nsys.path.insert(0,str(Path(__file__).resolve().parent))\nfrom palette import PALETTES, build_palette\nfrom themes.xfce import export\nexport({v: build_palette(v) for v in PALETTES}, Path(__file__).resolve().parent / 'dist')\n"
    return files


def export(pals,dist):
    out=dist/'xfce'
    out.mkdir(parents=True,exist_ok=True)
    packages = [package_files(p,variant) for variant,(p,_) in pals.items()]
    packages.append(('miami-cruise-xfce-source',source_files()))
    for name,files in packages:
        with (out/f'{name}.tar.gz').open('wb') as raw:
            with gzip.GzipFile(filename='',mode='wb',fileobj=raw,mtime=0) as gz:
                with tarfile.open(fileobj=gz,mode='w',format=tarfile.USTAR_FORMAT) as archive:
                    for path,data in sorted(files.items()):
                        info=tarfile.TarInfo(f'{name}/{path}')
                        info.mode=0o644
                        info.size=len(data)
                        info.mtime=1767225600
                        archive.addfile(info,io.BytesIO(data))


GUIDE = dict(
    name='XFCE', category='Desktop', mono='XF', tags=['GTK3','Xfwm4','Draft'],
    aliases='xfce desktop gtk thunar window manager greybird',
    status='Draft · native checks and user desktop testing passed',
    tagline='Teal-ink widgets, magenta selection and matching window decorations for your existing XFCE desktop.',
    files=[(f'xfce/Miami-Cruise-{v}.tar.gz',f'Miami-Cruise-{v}.tar.gz',f'GTK3 + Xfwm4 · {v.lower()} draft') for v in ('Dark','Light')] + [('xfce/miami-cruise-xfce-source.tar.gz','miami-cruise-xfce-source.tar.gz','Corresponding source · GPL-2.0-or-later')],
    shots=[(f'xfce/{kind}-{v}.png', f'Native {label} · {v} draft · synthetic content') for kind,label in [('desktop','XFCE desktop and panel'),('controls','GTK3 controls and window decorations')] for v in ('dark','light')],
    file_note='Each variant archive is a complete fixed-variant theme based on Greybird. The source archive is optional for rebuilding; do not extract it into your theme directory. No separate base theme installation required. Desktop theme files are GPL-2.0-or-later, not the collection’s MIT licence; attribution and licence texts are included.',
    tested='Draft: GTK 3.24.52, Xfwm4 4.20.0, xfdesktop 4.20.2, xfce4-panel 4.20.8 and Thunar 4.20.10 in private Xvnc sessions: both variants and native desktop/panel/menu/widget states inspected; 162 measured control contrast checks passed. User desktop testing confirmed readability; HiDPI testing remains pending. No GTK2, GTK4/libadwaita or Qt coverage promised',
    covers='GTK3 controls, menus, Thunar, GTK-styled panel surfaces and Xfwm4 window decorations. Custom panel backgrounds may override theme colours',
    glow='No; restrained focus outlines and the base theme’s shadows',
    license_label='Desktop theme licence and base attribution',license_path='vendor/greybird/README.md',
    steps=[('Install the theme folders',[
        ('p','Download either variant or both. Before extracting, preserve any existing same-named theme folders. Install locally; no root access is needed.'),
        ('code',[(None,'bash','theme_dir="${XDG_DATA_HOME:-$HOME/.local/share}/themes"\nmkdir -p "$theme_dir"\ntar -xzf Miami-Cruise-Dark.tar.gz -C "$theme_dir"\ntar -xzf Miami-Cruise-Light.tar.gz -C "$theme_dir"')]),
        ('note','If you downloaded only one variant, run only its extraction command. This draft targets GTK3 on XFCE; existing icons, cursors, fonts, wallpaper and panel layout stay unchanged.'),
    ]),('Select the theme',[
        ('p','First note your current choices in Settings → Appearance → Style and Settings → Window Manager → Style. Choose Miami-Cruise-Dark or Miami-Cruise-Light in both places. These are two independent settings; no automatic dark/light switching is configured.'),
        ('note','If the theme is not listed immediately, reopen the settings window. When updating an installed theme, select a different style in Appearance, then select Miami Cruise again. Copying updated files alone does not refresh running XFCE apps. Reopen any application that still retains the old styling; if needed, log out and back in. Reselect a different Window Manager style and back when updating decorations. GTK4/libadwaita, Qt and independently styled apps may not follow it. Do not copy theme CSS into global GTK configuration.'),
    ]),('Restore your previous appearance',[
        ('p','Select your recorded previous styles in both settings windows. After switching away, remove only the Miami Cruise theme folders you installed, or restore backed-up same-named folders. Leave icons, cursors, fonts and all other settings alone.'),
        ('note','Based on Greybird: https://github.com/shimmerproject/Greybird · XFCE appearance: https://docs.xfce.org/xfce/xfce4-settings/appearance'),
    ])],
)
