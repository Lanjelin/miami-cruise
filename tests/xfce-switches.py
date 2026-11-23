#!/usr/bin/python3
"""Process-local GTK switch track/thumb contrast, no desktop setting changes."""
from pathlib import Path
import sys
import tarfile
import itertools
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from palette import contrast

def hex_color(c):
    return '#%02x%02x%02x' % tuple(round(x*255) for x in (c.red,c.green,c.blue))

for variant in ('Dark','Light'):
    name='Miami-Cruise-'+variant
    with tarfile.open(ROOT/'dist/xfce'/f'{name}.tar.gz') as archive:
        css=archive.extractfile(f'{name}/gtk-3.0/gtk.css').read()
    provider=Gtk.CssProvider();provider.load_from_data(css)
    Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(),provider,600)
    count=0
    for checked,hover,back,disabled in itertools.product((False,True),repeat=4):
        state=Gtk.StateFlags.NORMAL
        for enabled,flag in ((checked,Gtk.StateFlags.CHECKED),(hover,Gtk.StateFlags.PRELIGHT),
                             (back,Gtk.StateFlags.BACKDROP),(disabled,Gtk.StateFlags.INSENSITIVE)):
            if enabled: state |= flag
        switch=Gtk.Switch()
        switch.set_state_flags(state,True)
        context=switch.get_style_context()
        path=switch.get_path().copy()
        i=path.append_type(Gtk.Widget.__gtype__)
        path.iter_set_object_name(i,'slider')
        path.iter_set_state(i,state)
        slider=Gtk.StyleContext.new();slider.set_screen(Gdk.Screen.get_default())
        slider.set_parent(context);slider.set_path(path);slider.set_state(state)
        track=context.get_background_color(state)
        thumb=slider.get_background_color(state)
        assert track.alpha==1 and thumb.alpha==1
        ratio=contrast(hex_color(track),hex_color(thumb))
        assert ratio>=3,(variant,checked,hover,back,disabled,ratio)
        count+=1
    Gtk.StyleContext.remove_provider_for_screen(Gdk.Screen.get_default(),provider)
    print(variant+': '+str(count)+' switch thumb/track contrast states passed')
