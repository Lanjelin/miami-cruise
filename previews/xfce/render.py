#!/usr/bin/python3
"""Native disposable GTK3/Xfwm4 previews. Requires GI, Xvnc and XFCE tools.
Run /usr/bin/python3 previews/xfce/render.py after building. Never uses the desktop bus.
"""
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import tarfile

ROOT = Path(__file__).resolve().parents[2]


def widget(mode, destination):
    import gi
    gi.require_version('Gtk','3.0')
    gi.require_version('Gdk','3.0')
    from gi.repository import Gtk, Gdk, GLib
    name=f'Miami-Cruise-{mode.title()}'
    Gtk.Settings.get_default().set_property('gtk-theme-name',name)
    Gtk.Settings.get_default().set_property('gtk-application-prefer-dark-theme',mode=='dark')
    # Match xfdesktop 4.20's real CSS node/classes, including its label renderer.
    sys.path.insert(0,str(ROOT))
    from palette import build_palette, rgb
    p = build_palette(mode)[0]
    desktop_path=Gtk.WidgetPath.new()
    index=desktop_path.append_type(Gtk.IconView.__gtype__)
    desktop_path.iter_set_object_name(index,'XfdesktopIconView')
    for cls in ('view','cell','label'): desktop_path.iter_add_class(index,cls)
    desktop_context=Gtk.StyleContext.new()
    desktop_context.set_screen(Gdk.Screen.get_default())
    desktop_context.set_path(desktop_path)
    for classes in (('view',), ('view','cell'), ('view','cell','label')):
        for cls in ('view','cell','label'):
            desktop_path.iter_remove_class(index,cls)
        for cls in classes:
            desktop_path.iter_add_class(index,cls)
        desktop_context.set_path(desktop_path)
        for state in (Gtk.StateFlags.NORMAL,Gtk.StateFlags.PRELIGHT,Gtk.StateFlags.BACKDROP,
                      Gtk.StateFlags.SELECTED,Gtk.StateFlags.SELECTED|Gtk.StateFlags.FOCUSED,
                      Gtk.StateFlags.SELECTED|Gtk.StateFlags.BACKDROP):
            desktop_context.set_state(state)
            actual=desktop_context.get_color(state)
            expected=rgb(p['on-accent' if state & Gtk.StateFlags.SELECTED else 'text'])
            assert tuple(round(c*255) for c in (actual.red,actual.green,actual.blue)) == expected, 'Desktop label foreground regression'
    print(mode+': desktop label CSS states passed')
    # Actual panel/tasklist CSS ancestry, with a nested label in every state.
    panel=Gtk.Box(spacing=12)
    panel.get_style_context().add_class('xfce4-panel')
    panel.get_style_context().add_class('background')
    tasks=Gtk.Box(spacing=8)
    tasks.get_style_context().add_class('tasklist')
    panel.pack_start(tasks,True,True,0)
    states = (Gtk.StateFlags.NORMAL, Gtk.StateFlags.PRELIGHT, Gtk.StateFlags.BACKDROP,
              Gtk.StateFlags.CHECKED, Gtk.StateFlags.ACTIVE,
              Gtk.StateFlags.CHECKED|Gtk.StateFlags.PRELIGHT,
              Gtk.StateFlags.CHECKED|Gtk.StateFlags.BACKDROP,
              Gtk.StateFlags.INSENSITIVE)
    panel_tests=[]
    for state in states:
        button=Gtk.ToggleButton(label='Projects' if state & Gtk.StateFlags.CHECKED else 'Terminal')
        tasks.pack_start(button,True,True,0)
        button.set_state_flags(state,True)
        panel_tests.append((button,state))
    window=Gtk.Window(title=f'Miami Cruise — {mode.title()} · GTK3 + Xfwm4')
    window.set_default_size(900,570)
    window.set_position(Gtk.WindowPosition.CENTER)
    outer=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=16)
    outer.set_border_width(24)
    window.add(outer)
    title=Gtk.Label()
    title.set_markup('<big><b>Miami Cruise</b></big>')
    title.set_xalign(0)
    outer.pack_start(title,False,False,0)
    outer.pack_start(panel,False,False,0)
    desc=Gtk.Label(label='Desktop theme · native GTK3 controls and Xfwm4 decorations',xalign=0)
    outer.pack_start(desc,False,False,0)
    row=Gtk.Box(spacing=12)
    for label,style in [('Default',None),('Continue','suggested-action'),('Remove','destructive-action'),('Unavailable',None)]:
        b=Gtk.Button(label=label)
        if style: b.get_style_context().add_class(style)
        if label=='Unavailable': b.set_sensitive(False)
        row.pack_start(b,False,False,0)
    outer.pack_start(row,False,False,0)
    entry=Gtk.Entry();entry.set_text('Search your workspace');outer.pack_start(entry,False,False,0)
    row=Gtk.Box(spacing=20)
    for label,on in [('Notifications',True),('Compact view',False)]:
        b=Gtk.CheckButton(label=label);b.set_active(on);row.pack_start(b,False,False,0)
    switch=Gtk.Switch();switch.set_active(True);row.pack_end(switch,False,False,0)
    outer.pack_start(row,False,False,0)
    store=Gtk.ListStore(str,str)
    for values in [('Documents','Folder'),('Projects','Folder'),('README.md','Markdown'),('palette.json','JSON')]: store.append(values)
    view=Gtk.TreeView(model=store)
    for index,label in enumerate(('Name','Type')): view.append_column(Gtk.TreeViewColumn(label,Gtk.CellRendererText(),text=index))
    view.get_selection().select_path(Gtk.TreePath.new_from_string('1'))
    scroll=Gtk.ScrolledWindow();scroll.add(view);outer.pack_start(scroll,True,True,0)
    progress=Gtk.ProgressBar();progress.set_fraction(.64);outer.pack_start(progress,False,False,0)
    outer.pack_start(Gtk.Label(label='Synthetic preview · no personal files or accounts',xalign=0),False,False,0)
    window.show_all()
    window.present()
    def capture():
        for button,state in panel_tests:
            role=('disabled' if state & Gtk.StateFlags.INSENSITIVE else
                  'text')
            for target in (button,button.get_child()):
                context=target.get_style_context()
                actual=context.get_color(context.get_state())
                assert tuple(round(c*255) for c in (actual.red,actual.green,actual.blue)) == rgb(p[role]), 'Panel/task label contrast regression'
        root=Gdk.get_default_root_window()
        Gdk.pixbuf_get_from_window(root,0,0,root.get_width(),root.get_height()).savev(str(destination),'png',[],[])
        Gtk.main_quit()
        return False
    if destination is not None:
        GLib.timeout_add(1800,capture)
    else:
        window.resize(900,640)
        window.move(400,120)
    Gtk.main()


def main():
    if len(sys.argv)>1 and sys.argv[1]=='--show-widget':
        widget(sys.argv[2],None);return
    if len(sys.argv)>1 and sys.argv[1]=='--widget':
        widget(sys.argv[2],Path(sys.argv[3]));return
    out=ROOT/'previews/xfce';out.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='miami-xfce-') as tmp:
        path=Path(tmp)
        (path/'runtime').mkdir(mode=0o700)
        env=dict(os.environ,HOME=tmp,XDG_CONFIG_HOME=str(path/'config'),XDG_DATA_HOME=str(path/'data'),XDG_CACHE_HOME=str(path/'cache'),XDG_STATE_HOME=str(path/'state'),XDG_RUNTIME_DIR=str(path/'runtime'),GSETTINGS_BACKEND='memory',NO_AT_BRIDGE='1')
        env.pop('DBUS_SESSION_BUS_ADDRESS',None)
        env.pop('GTK_THEME',None)
        env.pop('SESSION_MANAGER',None)
        themes=path/'data/themes';themes.mkdir(parents=True)
        for mode in ('Dark','Light'):
            with tarfile.open(ROOT/f'dist/xfce/Miami-Cruise-{mode}.tar.gz') as archive:
                archive.extractall(themes,filter='data')
        # VNC exposes only a private Unix socket; X11 TCP is disabled.
        with (path/'x.log').open('w') as log:
            server=subprocess.Popen(['Xvnc','-displayfd','1','-geometry','1000x700','-depth','24','-rfbport','-1','-rfbunixpath',str(path/'vnc.sock'),'-SecurityTypes','None','-nolisten','tcp','-ac'],env=env,stdout=subprocess.PIPE,stderr=log,text=True)
            try:
                import select
                if not select.select([server.stdout],[],[],15)[0]: raise RuntimeError('Xvnc startup timed out')
                number=server.stdout.readline().strip()
                if not number.isdigit(): raise RuntimeError('Xvnc did not allocate a display')
                env['DISPLAY']=':'+number
                for mode in ('dark','light'):
                    # All XFConf writes target a fresh private session/config, never the host desktop.
                    command='''set -eu
xfconf-query -c xfwm4 -p /general/theme -n -t string -s "$1"
xfwm4 --compositor=off >"$HOME/wm.log" 2>&1 &
wm=$!
trap 'kill "$wm" 2>/dev/null || true; wait "$wm" 2>/dev/null || true' EXIT
i=0
until xprop -root _NET_SUPPORTING_WM_CHECK | grep -q 'window id'; do
  i=$((i+1)); [ "$i" -lt 50 ] || exit 1
  sleep 0.1
done
sleep 0.3
"$2" "$3" --widget "$4" "$5"
'''
                    r=subprocess.run(['dbus-run-session','--','sh','-c',command,'preview',f'Miami-Cruise-{mode.title()}',sys.executable,str(Path(__file__).resolve()),mode,str(out/f'{mode}.png')],env=env,capture_output=True,text=True,timeout=30)
                    if r.returncode: raise RuntimeError(r.stderr)
                    # Ignore service startup chatter, but surface native rendering diagnostics.
                    warnings=[line for line in r.stderr.splitlines() if 'Theme parsing error' in line or 'Gtk-WARNING' in line or 'CRITICAL' in line]
                    print(mode+': '+str(len(warnings))+' GTK warnings')
                    if warnings: print('\n'.join(warnings[:12]))
                    if warnings: raise RuntimeError('Native GTK rendering warnings; inspect the diagnostics above')
            finally:
                server.terminate();server.wait(timeout=10)
    for mode in ('dark','light'):
        (ROOT/f'website/previews/xfce').mkdir(exist_ok=True)
        (ROOT/f'website/previews/xfce/{mode}.png').write_bytes((out/f'{mode}.png').read_bytes())

if __name__=='__main__': main()
