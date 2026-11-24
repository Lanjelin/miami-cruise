#!/usr/bin/python3
"""Real Arch/XFCE icon review; private display, session bus, HOME and config only."""
import ctypes
import importlib.util
import json
import os
from pathlib import Path
import re
import select
import subprocess
import sys
import tarfile
import tempfile
import time
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('xfce_fixture',ROOT/'previews/xfce/desktop.py')
fixture=importlib.util.module_from_spec(spec);spec.loader.exec_module(fixture)


def session(mode,out):
    import gi
    gi.require_version('Gtk','3.0');gi.require_version('Gdk','3.0');gi.require_version('GdkX11','3.0')
    from gi.repository import Gtk,Gdk,GdkX11
    sys.path.insert(0,str(ROOT))
    from palette import build_palette,rgb
    p=build_palette(mode)[0];home=Path(os.environ['HOME']);running=[];logs=[]
    def start(args,name):
        log=(home/(name+'.log')).open('w');logs.append(log)
        proc=subprocess.Popen(args,stdout=log,stderr=log);running.append(proc);return proc
    def query(*args):return subprocess.check_output(['xfconf-query',*args],text=True).strip()
    def shot(name):
        while Gtk.events_pending():Gtk.main_iteration_do(False)
        root=Gdk.get_default_root_window()
        pix=Gdk.pixbuf_get_from_window(root,0,0,root.get_width(),root.get_height());assert pix
        pix.savev(str(out/f'{name}-{mode}.png'),'png',[],[])
    try:
        start(['xfsettingsd','--no-daemon'],'settings')
        start(['xfwm4','--compositor=off'],'wm')
        for _ in range(60):
            if 'window id' in subprocess.check_output(['xprop','-root','_NET_SUPPORTING_WM_CHECK'],text=True):break
            time.sleep(.1)
        else:raise RuntimeError('Private WM did not start')
        assert query('-c','xsettings','-p','/Net/IconThemeName')=='Miami-Cruise-Candy-'+mode.title()
        monitor=Gdk.Display.get_default().get_monitor(0).get_model() or 'VNC-0'
        for name in dict.fromkeys((monitor,'VNC-0','0')):
            base=f'/backdrop/screen0/monitor{name}/workspace0/'
            for key,typ,value in [('image-style','int','0'),('color-style','int','0'),('last-image','string','')]:
                query('-c','xfce4-desktop','-p',base+key,'-n','-t',typ,'-s',value)
            query('-c','xfce4-desktop','-p',base+'rgba1','-n',*sum((['-t','double','-s',str(c/255)] for c in rgb(p['bg'])),[]),'-t','double','-s','1')
        start(['thunar','--daemon'],'thunar-service');time.sleep(.7)
        start(['xfdesktop','--disable-wm-check'],'desktop')
        start(['xfce4-panel','--disable-wm-check'],'panel');time.sleep(2)
        # Real desktop and panel at native 48px and 32px icon sizes.
        shot('desktop')
        xlib=ctypes.CDLL('libX11.so.6');xtst=ctypes.CDLL('libXtst.so.6')
        xlib.XOpenDisplay.restype=ctypes.c_void_p;xlib.XOpenDisplay.argtypes=[ctypes.c_char_p]
        xd=xlib.XOpenDisplay(os.environ['DISPLAY'].encode());assert xd
        xlib.XFlush.argtypes=[ctypes.c_void_p];xlib.XCloseDisplay.argtypes=[ctypes.c_void_p]
        xtst.XTestFakeMotionEvent.argtypes=[ctypes.c_void_p,ctypes.c_int,ctypes.c_int,ctypes.c_int,ctypes.c_ulong]
        xtst.XTestFakeButtonEvent.argtypes=[ctypes.c_void_p,ctypes.c_uint,ctypes.c_int,ctypes.c_ulong]
        def pointer(x,y,button=None):
            xtst.XTestFakeMotionEvent(xd,-1,x,y,0)
            if button:
                xtst.XTestFakeButtonEvent(xd,button,1,0);xtst.XTestFakeButtonEvent(xd,button,0,0)
            xlib.XFlush(xd);time.sleep(.5)
        pointer(55,18,1);shot('menu');pointer(1150,750,1)
        start(['thunar',str(home/'Showcase')],'thunar');time.sleep(2)
        theme=Gtk.IconTheme.get_default()
        checks={}
        for name in ('folder','folder-documents','firefox','code','utilities-terminal','thunar','application-pdf','text-x-python','preferences-system'):
            info=theme.lookup_icon(name,48,Gtk.IconLookupFlags.FORCE_SVG)
            assert info and 'Miami-Cruise-Candy-'+mode.title() in info.get_filename(),name
            info.load_icon();checks[name]='Candy-derived pack'
        # Set predictable window geometry through the real WM using EWMH messages.
        raw=subprocess.check_output(['xprop','-root','_NET_CLIENT_LIST'],text=True)
        for wid in re.findall(r'0x[0-9a-f]+',raw):
            props=subprocess.check_output(['xprop','-id',wid,'WM_CLASS'],text=True)
            if 'thunar' not in props.lower():continue
            win=GdkX11.X11Window.foreign_new_for_display(Gdk.Display.get_default(),int(wid,16))
            if win:win.move_resize(260,130,980,640)
        Gdk.Display.get_default().flush();time.sleep(1);shot('thunar')
        pointer(330,270,1);shot('selection')
        xlib.XStringToKeysym.argtypes=[ctypes.c_char_p];xlib.XStringToKeysym.restype=ctypes.c_ulong
        xlib.XKeysymToKeycode.argtypes=[ctypes.c_void_p,ctypes.c_ulong];xlib.XKeysymToKeycode.restype=ctypes.c_uint
        xtst.XTestFakeKeyEvent.argtypes=[ctypes.c_void_p,ctypes.c_uint,ctypes.c_int,ctypes.c_ulong]
        def key(name,on):
            code=xlib.XKeysymToKeycode(xd,xlib.XStringToKeysym(name.encode()));assert code,name
            xtst.XTestFakeKeyEvent(xd,code,on,0);xlib.XFlush(xd)
        def shortcut(name,shift=False):
            key('Control_L',1)
            if shift:key('Shift_L',1)
            key(name,1);key(name,0)
            if shift:key('Shift_L',0)
            key('Control_L',0);time.sleep(.25)
        # Use the actual view shortcuts; changing its saved default does not zoom
        # an already-open Thunar view.
        baseline=query('-c','thunar','-p','/last-icon-view-zoom-level')
        for _ in range(3):shortcut('minus')
        time.sleep(.4);shot('thunar-small')
        small=query('-c','thunar','-p','/last-icon-view-zoom-level')
        assert small!=baseline,('Thunar did not zoom out',small)
        for _ in range(5):shortcut('equal',shift=True)
        time.sleep(.4);shot('thunar-large')
        large=query('-c','thunar','-p','/last-icon-view-zoom-level')
        assert large!=small,('Thunar did not zoom in',large)
        shortcut('a');shot('selected-files')
        print(mode+': real Thunar zoom '+small+' → '+large,flush=True)
        # Desktop context menu at its real icon sizes, while file-manager is open.
        pointer(110,380,3);shot('context-menu');pointer(1380,780,1)
        xlib.XCloseDisplay(xd)
        (out/f'report-{mode}.json').write_text(json.dumps({'mode':mode,'host_os':'Arch Linux','session':'isolated XFCE','icon_lookup':checks,'captures':['desktop','menu','thunar','selection','thunar-small','thunar-large','selected-files','context-menu'],'thunar_zoom':{'small':small,'large':large}},indent=2)+'\n')
        print(mode+': real XFCE desktop/panel/menu/Thunar captures and native session icon lookup passed',flush=True)
    finally:
        for proc in reversed(running):
            if proc.poll() is None:proc.terminate()
        for proc in running:
            try:proc.wait(timeout=3)
            except subprocess.TimeoutExpired:proc.kill();proc.wait()
        for log in logs:log.close()
        issues=[]
        for path in home.glob('*.log'):
            for line in path.read_text(errors='replace').splitlines():
                if 'Theme parsing error' in line or 'CRITICAL' in line or 'Failed to load image' in line:
                    issues.append(path.name+': '+line)
        if issues:raise RuntimeError('\n'.join(issues))


def main():
    if len(sys.argv)>1 and sys.argv[1]=='--session':
        session(sys.argv[2],Path(sys.argv[3]));return
    out=ROOT/'previews/icons/review';out.mkdir(parents=True,exist_ok=True)
    modes=(sys.argv[sys.argv.index('--mode')+1],) if '--mode' in sys.argv else ('dark','light')
    assert all(mode in ('dark','light') for mode in modes)
    for mode in modes:
        with tempfile.TemporaryDirectory(prefix='miami-icon-desktop-') as tmp:
            home=Path(tmp);(home/'runtime').mkdir(mode=0o700)
            env={**os.environ,'HOME':tmp,'XDG_CONFIG_HOME':str(home/'config'),'XDG_DATA_HOME':str(home/'data'),'XDG_CACHE_HOME':str(home/'cache'),'XDG_STATE_HOME':str(home/'state'),'XDG_RUNTIME_DIR':str(home/'runtime'),'GSETTINGS_BACKEND':'memory','NO_AT_BRIDGE':'1'}
            for key in ('DBUS_SESSION_BUS_ADDRESS','GTK_THEME','SESSION_MANAGER','DESKTOP_STARTUP_ID'):env.pop(key,None)
            fixture.setup(home,mode)
            cfg=home/'config/xfce4/xfconf/xfce-perchannel-xml'
            fixture.channel(cfg,'xsettings',[('/Net/ThemeName','string','Miami-Cruise-'+mode.title()),('/Gtk/FontName','string','Sans 10'),('/Net/IconThemeName','string','Miami-Cruise-Candy-'+mode.title())])
            fixture.channel(cfg,'thunar',[('/last-side-pane','string','void'),('/last-location-bar','string','ThunarLocationButtons'),('/last-view','string','ThunarIconView'),('/last-icon-view-zoom-level','string','THUNAR_ZOOM_LEVEL_100_PERCENT'),('/last-show-hidden','bool','false'),('/misc-thumbnail-mode','string','THUNAR_THUMBNAIL_MODE_NEVER')])
            for dirname,label,icon in [('terminal','Terminal','utilities-terminal'),('projects','Projects','thunar'),('settings','Settings','preferences-system')]:
                (home/f'data/applications/{dirname}.desktop').write_text(f'[Desktop Entry]\nType=Application\nName={label}\nExec=false\nIcon={icon}\nCategories=Utility;\n')
            showcase=home/'Showcase';showcase.mkdir()
            for name in ('Documents','Downloads','Pictures','Music','Projects','Favourites'):(showcase/name).mkdir()
            for name,body in [('Notes.txt','Synthetic note\n'),('palette.py','PALETTE = "Miami Cruise"\n'),('Guide.pdf','%PDF-1.4\n%%EOF\n'),('README.md','# Miami Cruise\n')]:
                (showcase/name).write_text(body)
            # Synthetic application entries exercise branded artwork in a real file view.
            for name,icon in [('Firefox','firefox'),('VS Code','code'),('Terminal','utilities-terminal'),('Settings','preferences-system')]:
                path=showcase/(name+'.desktop');path.write_text(f'[Desktop Entry]\nType=Application\nName={name}\nExec=false\nIcon={icon}\n');path.chmod(0o755)
            for name in ('Documents','Pictures'):(home/'Desktop'/name).mkdir()
            (home/'Desktop/Preview.py').write_text('# Synthetic file\n')
            for kind,archive in [('themes',f'xfce/Miami-Cruise-{mode.title()}.tar.gz'),('icons',f'icons/Miami-Cruise-Candy-{mode.title()}.tar.gz')]:
                directory=home/'data'/kind;directory.mkdir(parents=True,exist_ok=True)
                with tarfile.open(ROOT/'dist'/archive) as tar:tar.extractall(directory,filter='data')
            with (home/'x.log').open('w') as log:
                server=subprocess.Popen(['Xvnc','-displayfd','1','-geometry','1440x900','-depth','24','-rfbport','-1','-rfbunixpath',str(home/'vnc.sock'),'-SecurityTypes','None','-nolisten','tcp','-ac'],env=env,stdout=subprocess.PIPE,stderr=log,text=True)
                try:
                    assert select.select([server.stdout],[],[],15)[0],'Private Xvnc startup timeout'
                    number=server.stdout.readline().strip();assert number.isdigit();env['DISPLAY']=':'+number
                    result=subprocess.run(['dbus-run-session','--',sys.executable,str(Path(__file__).resolve()),'--session',mode,str(out)],env=env,capture_output=True,text=True,timeout=60)
                    if result.returncode:raise RuntimeError(result.stdout+'\n'+result.stderr)
                    print(result.stdout.strip())
                finally:server.terminate();server.wait(timeout=10)

if __name__=='__main__':main()
