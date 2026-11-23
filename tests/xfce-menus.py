#!/usr/bin/python3
"""Regression: highlighted parent items must not recolour nested submenu labels.
Uses process-local GTK CSS only; does not show windows or change desktop settings.
"""
from pathlib import Path
import tarfile
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(ROOT))
from palette import build_palette, rgb
for variant in ('dark', 'light'):
    name = f'Miami-Cruise-{variant.title()}'
    with tarfile.open(ROOT / 'dist/xfce' / f'{name}.tar.gz') as archive:
        css = archive.extractfile(f'{name}/gtk-3.0/gtk.css').read()
    if '--installed' in sys.argv:
        css = (Path.home() / '.local/share/themes' / name / 'gtk-3.0/gtk.css').read_bytes()
    # These checks need semantic CSS rules, not image assets.
    provider = Gtk.CssProvider()
    provider.load_from_data(css)
    Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), provider, 600)
    menu = Gtk.Menu()
    parent = Gtk.MenuItem(label='Accessories')
    menu.append(parent)
    submenu = Gtk.Menu()
    parent.set_submenu(submenu)
    child = Gtk.MenuItem(label='Text editor')
    submenu.append(child)
    menu.show_all()
    parent.set_state_flags(Gtk.StateFlags.PRELIGHT, False)
    expected = rgb(build_palette(variant)[0]['text'])
    c = child.get_child().get_style_context().get_color(Gtk.StateFlags.NORMAL)
    actual = tuple(round(v * 255) for v in (c.red, c.green, c.blue))
    assert actual == expected, (variant, actual, expected)
    menu.destroy()
    Gtk.StyleContext.remove_provider_for_screen(Gdk.Screen.get_default(), provider)
    print(variant + ': nested submenu foreground passed')
