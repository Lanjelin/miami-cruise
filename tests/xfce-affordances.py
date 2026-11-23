#!/usr/bin/python3
"""Process-local keyboard-focus and overlay-scrollbar checks; no settings writes."""
from pathlib import Path
import sys
import tarfile
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gtk, Gdk
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from palette import contrast


def hx(color):
    return '#%02x%02x%02x' % tuple(round(v*255) for v in (color.red, color.green, color.blue))


for mode in ('Dark', 'Light'):
    name = 'Miami-Cruise-' + mode
    with tarfile.open(ROOT/'dist/xfce'/f'{name}.tar.gz') as archive:
        css = archive.extractfile(f'{name}/gtk-3.0/gtk.css').read()
    provider = Gtk.CssProvider()
    provider.load_from_data(css)
    Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), provider, 600)
    window = Gtk.Window()
    box = Gtk.Box()
    window.add(box)
    entry = Gtk.Entry()
    button = Gtk.Button(label='Keyboard focus')
    bar = Gtk.Scrollbar(orientation=Gtk.Orientation.VERTICAL)
    for widget in (entry, button, bar):
        box.add(widget)
    for widget in (entry, button):
        ctx = widget.get_style_context()
        ctx.set_state(Gtk.StateFlags.FOCUSED)
        if widget is button:
            assert ctx.get_property('outline-width', Gtk.StateFlags.FOCUSED) == 2
        else:
            assert ctx.get_border_color(Gtk.StateFlags.FOCUSED).alpha == 1
    for state in (Gtk.StateFlags.NORMAL, Gtk.StateFlags.BACKDROP,
                  Gtk.StateFlags.PRELIGHT, Gtk.StateFlags.ACTIVE):
        ctx = bar.get_style_context()
        ctx.set_state(state)
        path = bar.get_path().copy()
        parent = ctx
        contexts = []
        for name in ('trough', 'slider'):
            path = path.copy()
            index = path.append_type(Gtk.Widget.__gtype__)
            path.iter_set_object_name(index, name)
            path.iter_set_state(index, state)
            child = Gtk.StyleContext.new()
            child.set_screen(Gdk.Screen.get_default())
            child.set_parent(parent)
            child.set_path(path)
            child.set_state(state)
            contexts.append(child)
            parent = child
        trough, slider = contexts
        bg = trough.get_background_color(state)
        if bg.alpha < .99:
            bg = ctx.get_background_color(state)
        # Overlay troughs are transparent; resolve against their actual window.
        if bg.alpha < .99:
            bg = window.get_style_context().get_background_color(state)
        fg = slider.get_background_color(state)
        assert fg.alpha == 1 and bg.alpha == 1
        assert contrast(hx(fg), hx(bg)) >= 3, (mode, int(state), hx(fg), hx(bg))
    panel = Gtk.Box()
    panel.get_style_context().add_class('xfce4-panel')
    panel.get_style_context().add_class('background')
    actions = Gtk.ToggleButton(label='miami')
    actions.set_name('actions-button')
    panel.add(actions)
    for state in (Gtk.StateFlags.NORMAL, Gtk.StateFlags.BACKDROP):
        actions.set_state_flags(state, True)
        assert actions.get_style_context().get_border_color(state).alpha == 0, (mode, 'boxed panel action')
    panel.destroy()
    wrapper = Gtk.Window()
    wrapper.set_name('XfcePanelWindowWrapper')
    for cls in ('panel', 'xfce4-panel', 'background'):
        wrapper.get_style_context().add_class(cls)
    ctx = wrapper.get_style_context()
    border = ctx.get_border(Gtk.StateFlags.NORMAL)
    assert (border.top, border.right, border.bottom, border.left) == (0, 0, 0, 0)
    wrapper.destroy()
    path = Gtk.WidgetPath.new()
    index = path.append_type(Gtk.IconView.__gtype__)
    path.iter_set_object_name(index, 'XfdesktopIconView')
    for cls in ('view', 'rubberband'):
        path.iter_add_class(index, cls)
    overlay = Gtk.StyleContext.new()
    overlay.set_screen(Gdk.Screen.get_default())
    overlay.set_path(path)
    for state in (Gtk.StateFlags.NORMAL, Gtk.StateFlags.ACTIVE,
                  Gtk.StateFlags.SELECTED, Gtk.StateFlags.BACKDROP):
        overlay.set_state(state)
        assert abs(overlay.get_background_color(state).alpha - .20) < .001, (mode, 'opaque desktop drag')
    window.destroy()
    Gtk.StyleContext.remove_provider_for_screen(Gdk.Screen.get_default(), provider)
    print(mode + ': focus, entry, scrollbar and flat panel-button states passed')
