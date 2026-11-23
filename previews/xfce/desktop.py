#!/usr/bin/python3
"""Real xfdesktop/panel/settings/WM in a private display, bus and home.
Requires the same native tools as render.py plus xfdesktop, xfce4-panel,
xfsettingsd and libXtst. No personal desktop is captured or configured.
"""
import ctypes
import json
import os
from pathlib import Path
import select
import subprocess
import sys
import tarfile
import tempfile
import time
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[2]


def channel(path,name,properties):
    root=ET.Element('channel',name=name,version='1.0')
    for key,typ,value in properties:
        current=root
        parts=key.strip('/').split('/')
        for part in parts[:-1]:
            found=current.find(f"property[@name='{part}']")
            current=found if found is not None else ET.SubElement(current,'property',name=part,type='empty')
        found=current.find(f"property[@name='{parts[-1]}']")
        if found is None: found=ET.SubElement(current,'property',name=parts[-1])
        found.set('type',typ)
        if typ=='array':
            for itemtype,itemvalue in value: ET.SubElement(found,'value',type=itemtype,value=str(itemvalue))
        else: found.set('value',str(value))
    path.mkdir(parents=True,exist_ok=True)
    ET.ElementTree(root).write(path/f'{name}.xml',encoding='utf-8',xml_declaration=True)


def setup(path,mode):
    sys.path.insert(0,str(ROOT))
    from palette import build_palette,rgb
    p=build_palette(mode)[0]
    cfg=path/'config/xfce4/xfconf/xfce-perchannel-xml'
    name='Miami-Cruise-'+mode.title()
    channel(cfg,'xsettings',[('/Net/ThemeName','string',name),('/Gtk/FontName','string','Sans 10'),('/Net/IconThemeName','string','Adwaita')])
    channel(cfg,'xfwm4',[('/general/theme','string',name),('/general/use_compositing','bool','false')])
    channel(cfg,'xfce4-panel',[
        ('/configver','int',2),('/panels','array',[('int',1),('int',2)]),('/panels/dark-mode','bool','true'),
        ('/panels/panel-1/position','string','p=6;x=0;y=0'),('/panels/panel-1/length','uint',100),
        ('/panels/panel-1/position-locked','bool','true'),('/panels/panel-1/size','uint',38),
        ('/panels/panel-1/plugin-ids','array',[('int',i) for i in (1,2,3,4)]),
        ('/panels/panel-2/position','string','p=10;x=720;y=900'),
        ('/panels/panel-2/position-locked','bool','true'),
        ('/panels/panel-2/length','uint',10),('/panels/panel-2/length-adjust','bool','true'),
        ('/panels/panel-2/size','uint',48),('/panels/panel-2/icon-size','uint',32),
        ('/panels/panel-2/plugin-ids','array',[('int',i) for i in (5,6,7)]),
        *[(f'/plugins/plugin-{i}','string','launcher') for i in (5,6,7)],
        *[(f'/plugins/plugin-{i}/items','array',[('string',str(path/'data/applications'/f'{app}.desktop'))])
          for i,app in zip((5,6,7),('terminal','projects','settings'))],
        ('/plugins/plugin-1','string','applicationsmenu'),('/plugins/plugin-1/button-title','string','Applications'),
        ('/plugins/plugin-2','string','tasklist'),('/plugins/plugin-2/show-handle','bool','false'),
        ('/plugins/plugin-3','string','separator'),('/plugins/plugin-3/expand','bool','true'),
        ('/plugins/plugin-3/style','uint',0),('/plugins/plugin-4','string','clock'),
        ('/plugins/plugin-4/digital-format','string','Miami Cruise'),
    ])
    props=[('/desktop-icons/style','int',2)]
    for icon in ('show-home','show-filesystem','show-trash','show-removable'):
        props.append(('/desktop-icons/file-icons/'+icon,'bool','false'))
    # Xvnc's native monitor name is obtained again within the private display.
    channel(cfg,'xfce4-desktop',props)
    channel(cfg,'thunar',[('/last-side-pane','string','void'),('/last-show-hidden','bool','false'),('/last-statusbar-visible','bool','false'),('/last-location-bar','string','ThunarLocationButtons')])
    menus=path/'config/menus';menus.mkdir(parents=True)
    applications=path/'data/applications';applications.mkdir(parents=True)
    for app,label in (('terminal','Terminal'),('projects','Projects'),('settings','Settings')):
        (applications/(app+'.desktop')).write_text(f'[Desktop Entry]\nType=Application\nName={label}\nExec=false\nIcon=applications-utilities\nCategories=Utility;\n')
    (menus/'xfce-applications.menu').write_text('<?xml version="1.0"?><Menu><Name>Applications</Name><AppDir>'+str(applications)+'</AppDir><Include><Filename>terminal.desktop</Filename><Filename>projects.desktop</Filename><Filename>settings.desktop</Filename></Include></Menu>')
    desktop=path/'Desktop';desktop.mkdir()
    (desktop/'Projects').mkdir();(desktop/'Notes.txt').write_text('Synthetic desktop fixture.\n')
    (desktop/'Projects/README.md').write_text('# Example project\n')
    (desktop/'Projects/palette.json').write_text('{}\n')
    (path/'config/user-dirs.dirs').write_text('XDG_DESKTOP_DIR="$HOME/Desktop"\n')
    return p


def session(mode,out):
    import gi
    gi.require_version('Gtk','3.0');gi.require_version('Gdk','3.0')
    from gi.repository import Gtk,Gdk
    sys.path.insert(0,str(ROOT))
    from palette import build_palette,rgb
    p=build_palette(mode)[0]
    theme_css=Path(os.environ['XDG_DATA_HOME'])/'themes'/('Miami-Cruise-'+mode.title())/'gtk-3.0/gtk.css'
    correct_css=theme_css.read_text()
    stale_test=os.environ.get('MIAMI_STALE_TEST')=='1'
    if stale_test:
        base,custom=correct_css.split('/* Miami Cruise semantic overrides; Greybird geometry retained. */',1)
        theme_css.write_text(base+'\n'+'\n'.join(line for line in custom.splitlines() if 'XfdesktopIconView' not in line and not line.startswith('.xfce4-panel'))+'\n')
    running=[]
    logs=[]
    def start(command,label):
        log=open(Path(os.environ['HOME'])/(label+'.log'),'w')
        logs.append(log)
        proc=subprocess.Popen(command,stdout=log,stderr=log)
        running.append(proc)
        return proc
    def query(args): subprocess.run(['xfconf-query']+args,check=True,capture_output=True)
    try:
        start(['xfsettingsd','--no-daemon'],'settings')
        start(['xfwm4','--compositor=off'],'wm')
        for _ in range(60):
            if 'window id' in subprocess.check_output(['xprop','-root','_NET_SUPPORTING_WM_CHECK'],text=True): break
            time.sleep(.1)
        else: raise RuntimeError('Isolated WM startup failed')
        display=Gdk.Display.get_default()
        monitor=display.get_monitor(0).get_model() or 'VNC-0'
        # xfdesktop 4.20 uses connector names; Xvnc exposes screen as VNC-0.
        for monitor_name in dict.fromkeys((monitor,'VNC-0','0')):
            base=f'/backdrop/screen0/monitor{monitor_name}/workspace0/'
            for key,typ,value in [('image-style','int','0'),('color-style','int','0'),('last-image','string','')]:
                query(['-c','xfce4-desktop','-p',base+key,'-n','-t',typ,'-s',value])
            query(['-c','xfce4-desktop','-p',base+'rgba1','-n']+sum((['-t','double','-s',str(c/255)] for c in rgb(p['bg'])),[])+['-t','double','-s','1'])
        start(['thunar','--daemon'],'file-manager-service')
        for _ in range(50):
            names=subprocess.check_output(['gdbus','call','--session','--dest','org.freedesktop.DBus','--object-path','/org/freedesktop/DBus','--method','org.freedesktop.DBus.ListNames'],text=True)
            if 'org.xfce.Thunar' in names: break
            time.sleep(.1)
        start(['xfdesktop','--disable-wm-check'],'desktop')
        start(['xfce4-panel','--disable-wm-check'],'panel')
        time.sleep(2)
        window=start([sys.executable,str(ROOT/'previews/xfce/render.py'),'--show-widget',mode],'widgets')
        time.sleep(2)
        root=Gdk.get_default_root_window()
        def shot(name):
            while Gtk.events_pending(): Gtk.main_iteration_do(False)
            pix=Gdk.pixbuf_get_from_window(root,0,0,root.get_width(),root.get_height())
            assert pix is not None
            pix.savev(str(out/name),'png',[],[])
        shot(('stale-initial-' if stale_test else 'desktop-')+mode+'.png')
        if stale_test:
            before=Gdk.pixbuf_get_from_window(root,0,0,root.get_width(),root.get_height()).get_pixels()
            theme_css.write_text(correct_css)
            time.sleep(.8)
            shot('installed-no-reload-'+mode+'.png')
            after=Gdk.pixbuf_get_from_window(root,0,0,root.get_width(),root.get_height()).get_pixels()
            print(mode+': writing updated CSS changed desktop pixels: '+str(before!=after))
            query(['-c','xsettings','-p','/Net/ThemeName','-s','Adwaita'])
            time.sleep(.7)
            query(['-c','xsettings','-p','/Net/ThemeName','-s','Miami-Cruise-'+mode.title()])
            time.sleep(1)
            shot('reselected-'+mode+'.png')
            reselected=Gdk.pixbuf_get_from_window(root,0,0,root.get_width(),root.get_height()).get_pixels()
            print(mode+': reselecting theme changed desktop pixels: '+str(after!=reselected))
        # Real panel menu, hovered task, then selected desktop icon via XTest.
        xlib=ctypes.CDLL('libX11.so.6');xtst=ctypes.CDLL('libXtst.so.6')
        xlib.XOpenDisplay.restype=ctypes.c_void_p
        xlib.XOpenDisplay.argtypes=[ctypes.c_char_p]
        xd=xlib.XOpenDisplay(os.environ['DISPLAY'].encode())
        xlib.XFlush.argtypes=[ctypes.c_void_p]
        xtst.XTestFakeMotionEvent.argtypes=[ctypes.c_void_p,ctypes.c_int,ctypes.c_int,ctypes.c_int,ctypes.c_ulong]
        xtst.XTestFakeButtonEvent.argtypes=[ctypes.c_void_p,ctypes.c_uint,ctypes.c_int,ctypes.c_ulong]
        def pointer(x,y,click=False):
            xtst.XTestFakeMotionEvent(xd,-1,x,y,0)
            if click:
                xtst.XTestFakeButtonEvent(xd,1,1,0);xtst.XTestFakeButtonEvent(xd,1,0,0)
            xlib.XFlush(xd);time.sleep(.5)
        # Hold a real xfdesktop rubber-band selection over fixture icons.
        pointer(20,45)
        xtst.XTestFakeButtonEvent(xd,1,1,0);xlib.XFlush(xd)
        try:
            pointer(300,350)
            shot('desktop-drag-'+mode+'.png')
        finally:
            xtst.XTestFakeButtonEvent(xd,1,0,0);xlib.XFlush(xd)
        pointer(55,18,True);shot('menu-'+mode+'.png')
        pointer(80,53);shot('menu-hover-'+mode+'.png')
        pointer(1400,840,True)
        pointer(220,18);shot('task-hover-'+mode+'.png')
        pointer(65,90,True);shot('desktop-selected-'+mode+'.png')
        # Real file-manager rendering, using a fixture-only location/side pane.
        fm=start(['thunar',str(Path(os.environ['HOME'])/'Desktop/Projects')],'thunar')
        import re
        def clients():
            raw=subprocess.check_output(['xprop','-root','_NET_CLIENT_LIST'],text=True)
            result=[]
            for wid in re.findall(r'0x[0-9a-f]+',raw):
                title=subprocess.run(['xprop','-id',wid,'_NET_WM_NAME','WM_CLASS'],capture_output=True,text=True).stdout
                result.append((wid,title))
            return result
        for _ in range(60):
            if any('Thunar' in title or 'thunar' in title for _,title in clients()):break
            time.sleep(.1)
        else:
            print('Thunar did not expose a window; exit:',fm.poll())
            print((Path(os.environ['HOME'])/'thunar.log').read_text())
            print('Client summaries:',clients())
            raise RuntimeError('Thunar verification blocked')
        time.sleep(.5);shot('thunar-'+mode+'.png')
        controls=start([sys.executable,str(ROOT/'previews/xfce/controls.py'),mode,str(out/('contrast-'+mode+'.json'))],'controls')
        time.sleep(1.5);shot('controls-'+mode+'.png')
        pointer(500,365,True);shot('combo-'+mode+'.png')
        pointer(1380,820,True)
        pointer(390,165,True);pointer(420,193);shot('control-menu-'+mode+'.png')
        pointer(1400,840,True);shot('controls-unfocused-'+mode+'.png')
        # Pointer hover over a task after multiple application windows exist.
        pointer(220,18);shot('task-hover-'+mode+'.png')
        other=build_palette('light' if mode=='dark' else 'dark')[0]
        for monitor_name in dict.fromkeys((monitor,'VNC-0','0')):
            args=['-c','xfce4-desktop','-p',f'/backdrop/screen0/monitor{monitor_name}/workspace0/rgba1']
            query(args+sum((['-t','double','-s',str(c/255)] for c in rgb(other['bg'])),[])+['-t','double','-s','1'])
        time.sleep(.5);shot('opposite-wallpaper-'+mode+'.png')
        print(mode+': real desktop, panel, menus, task states, Thunar and controls captured')
    finally:
        for proc in reversed(running):
            if proc.poll() is None: proc.terminate()
        for proc in running:
            try: proc.wait(timeout=5)
            except subprocess.TimeoutExpired: proc.kill();proc.wait()
        for log in logs: log.close()
        for name in ('desktop','panel','widgets','thunar','controls'):
            logpath=Path(os.environ['HOME'])/(name+'.log')
            if logpath.exists():
                text=logpath.read_text()
                issues=[line for line in text.splitlines() if 'Theme parsing error' in line or 'CRITICAL' in line]
                if issues: raise RuntimeError(name+': '+str(issues))


def main():
    if len(sys.argv)>1 and sys.argv[1]=='--session':
        session(sys.argv[2],Path(sys.argv[3]));return
    out=ROOT/'previews/xfce/review';out.mkdir(parents=True,exist_ok=True)
    for mode in ('dark','light'):
        with tempfile.TemporaryDirectory(prefix='miami-desktop-') as tmp:
            path=Path(tmp);(path/'runtime').mkdir(mode=0o700)
            env=dict(os.environ,HOME=tmp,XDG_CONFIG_HOME=str(path/'config'),XDG_DATA_HOME=str(path/'data'),XDG_CACHE_HOME=str(path/'cache'),XDG_STATE_HOME=str(path/'state'),XDG_RUNTIME_DIR=str(path/'runtime'),GSETTINGS_BACKEND='memory',NO_AT_BRIDGE='1')
            for key in ('DBUS_SESSION_BUS_ADDRESS','GTK_THEME','SESSION_MANAGER'):env.pop(key,None)
            setup(path,mode)
            theme_dir=path/'data/themes';theme_dir.mkdir(parents=True)
            with tarfile.open(ROOT/f'dist/xfce/Miami-Cruise-{mode.title()}.tar.gz') as a:a.extractall(theme_dir,filter='data')
            with (path/'x.log').open('w') as log:
                x=subprocess.Popen(['Xvnc','-displayfd','1','-geometry','1440x900','-depth','24','-rfbport','-1','-rfbunixpath',str(path/'vnc.sock'),'-SecurityTypes','None','-nolisten','tcp','-ac'],env=env,stdout=subprocess.PIPE,stderr=log,text=True)
                try:
                    if not select.select([x.stdout],[],[],15)[0]:raise RuntimeError('Xvnc timeout')
                    number=x.stdout.readline().strip();assert number.isdigit()
                    env['DISPLAY']=':'+number
                    r=subprocess.run(['dbus-run-session','--',sys.executable,str(Path(__file__).resolve()),'--session',mode,str(out)],env=env,capture_output=True,text=True,timeout=45)
                    if r.returncode:raise RuntimeError(r.stdout+'\n'+r.stderr)
                    print(r.stdout.strip())
                    report=json.loads((out/('contrast-'+mode+'.json')).read_text())
                    failures=[c for c in report['checks'] if not c['passed']]
                    if failures: raise RuntimeError('Contrast failures: '+str(failures))
                    print(mode+': '+str(len(report['checks']))+' native control contrast checks passed')
                finally:x.terminate();x.wait(timeout=10)
        if os.environ.get('MIAMI_STALE_TEST')!='1':
            for kind in ('desktop','controls'):
                data=(out/f'{kind}-{mode}.png').read_bytes()
                (out.parent/f'{kind}-{mode}.png').write_bytes(data)
                site=ROOT/f'website/previews/xfce/{kind}-{mode}.png'
                site.parent.mkdir(exist_ok=True)
                site.write_bytes(data)

if __name__=='__main__':main()
