#!/usr/bin/python3
"""Native GTK galleries and full SVG decode checks in a private Xvnc session."""
import hashlib
import os
import select
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]


def child(mode, icons, output=None):
    import gi
    gi.require_version('Gtk','3.0')
    gi.require_version('Gdk','3.0')
    from gi.repository import Gtk,Gdk,GdkPixbuf
    sys.path.insert(0,str(ROOT))
    from palette import build_palette
    p=build_palette(mode)[0];theme=Gtk.IconTheme.new()
    theme.set_search_path([str(icons),'/usr/share/icons'])
    directory=icons/('Miami-Cruise-Candy-'+mode.title())
    theme.set_custom_theme(directory.name)
    unique=set();count=0;blank=[]
    for path in sorted(directory.rglob('*')):
        if not path.is_file() or path.name in ('LICENSE','README.md','CHANGES.md','upstream.json','index.theme'):continue
        count+=1;data=path.read_bytes();digest=hashlib.sha256(data).digest()
        if digest in unique:continue
        unique.add(digest)
        pix=GdkPixbuf.Pixbuf.new_from_file_at_scale(str(path),48,48,True)
        assert pix.get_width()>0 and pix.get_height()>0,path
        pixels=pix.get_pixels();channels=pix.get_n_channels()
        if pix.get_has_alpha() and not any(pixels[3::channels]):blank.append(str(path.relative_to(directory)))
    # Verify the complete discoverable name set, not only the gallery samples.
    names={path.stem for path in directory.rglob('*.svg')}
    for name in names:
        info=theme.lookup_icon(name,48,Gtk.IconLookupFlags.FORCE_SVG)
        assert info and Path(info.get_filename()).is_relative_to(directory),name
    # Preserve upstream transparent entries, but expose any blank output in the report.
    if blank:print(mode,'transparent artwork:',blank,flush=True)
    samples=[('folder','Folder'),('folder-documents','Documents'),('folder-downloads','Downloads'),('folder-pictures','Pictures'),('folder-music','Music'),('folder-favorites','Favourites'),
             ('firefox','Firefox'),('code','VS Code'),('utilities-terminal','Terminal'),('thunar','File manager'),('vlc','VLC'),('gimp','GIMP'),
             ('drive-harddisk','Disk'),('drive-removable-media-usb','USB'),('smartphone','Phone'),('application-pdf','PDF'),('text-x-python','Python file'),('text-x-generic','Text file'),
             ('audio-volume-high','Volume'),('audio-volume-high-warning','Warning'),('zero-trust-error','Error'),('network-wireless-100','Wi-Fi'),('battery','Battery'),('preferences-system','Settings')]
    found=[]
    for name,label in samples:
        info=theme.lookup_icon(name,64,Gtk.IconLookupFlags.FORCE_SVG)
        if not info or not Path(info.get_filename()).is_relative_to(directory):
            print('Unavailable gallery sample:',name,flush=True);continue
        found.append((name,label,info.load_icon()))
    assert len(found)>=20
    for name in ('firefox','code','folder','folder-documents','audio-volume-high-warning','zero-trust-error'):
        for size in (16,22,32,48,64,96,128):
            info=theme.lookup_icon(name,size,Gtk.IconLookupFlags.FORCE_SVG)
            assert info and Path(info.get_filename()).is_relative_to(directory),(name,size)
            pix=info.load_icon();assert max(pix.get_width(),pix.get_height())==size,(name,size)
    print(f'{mode}: {count} names, {len(unique)} distinct native SVG decodes, {len(names)} GTK names; GTK discovery and 16–128px loading passed',flush=True)
    if output is None:return
    Gtk.Settings.get_default().set_property('gtk-theme-name','Adwaita')
    css=Gtk.CssProvider();css.load_from_data(f'''* {{ font-family: Sans; color: {p['text']}; }}
window, box, grid, label, image {{ background-color: transparent; }}
window {{ background-color: {p['bg']}; }}
label.title {{ font-size: 24px; font-weight: bold; }}
label.subtitle {{ font-size: 12px; color: {p['muted']}; }}
label.heading {{ font-size: 14px; font-weight: bold; color: {p['info']}; }}
label.caption {{ font-size: 12px; }}'''.encode())
    Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(),css,600)
    win=Gtk.OffscreenWindow();box=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=18);box.set_border_width(28);win.add(box)
    def label(text,cls):
        item=Gtk.Label(label=text,xalign=0);item.get_style_context().add_class(cls);box.pack_start(item,False,False,0)
    label('Miami Cruise · Candy icons','title')
    label(f'{mode.title()} · native GTK rendering · synthetic gallery','subtitle')
    for start,heading in [(0,'Folders & places'),(6,'Applications'),(12,'Devices & file types'),(18,'Status & preferences')]:
        label(heading,'heading');grid=Gtk.Grid(column_spacing=16,row_spacing=14)
        for i,(name,title,pix) in enumerate(found[start:start+6]):
            cell=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=9);cell.set_size_request(112,-1)
            cell.pack_start(Gtk.Image.new_from_pixbuf(pix),False,False,0)
            caption=Gtk.Label(label=title);caption.get_style_context().add_class('caption');cell.pack_start(caption,False,False,0)
            grid.attach(cell,i,0,1,1)
        box.pack_start(grid,False,False,0)
    label('Candy artwork · Miami Cruise colours · GPL-3.0 · application marks belong to their owners','subtitle')
    win.show_all()
    while Gtk.events_pending():Gtk.main_iteration()
    pix=win.get_pixbuf();assert pix is not None;pix.savev(str(output),'png',[],[]);win.destroy()


def main():
    if len(sys.argv)>1 and sys.argv[1]=='--child':
        child(sys.argv[2],Path(sys.argv[3]),Path(sys.argv[4]) if len(sys.argv)>4 else None);return
    with tempfile.TemporaryDirectory(prefix='miami-candy-native-') as tmp:
        work=Path(tmp);icons=work/'icons';icons.mkdir();runtime=work/'runtime';runtime.mkdir(mode=0o700)
        for mode in ('Dark','Light'):
            with tarfile.open(ROOT/f'dist/icons/Miami-Cruise-Candy-{mode}.tar.gz') as tar:
                assert all(m.isfile() and '..' not in Path(m.name).parts and not m.name.startswith('/') for m in tar.getmembers())
                tar.extractall(icons,filter='data')
        read,write=os.pipe()
        with (work/'xvnc.log').open('wb') as log:
            server=subprocess.Popen(['Xvnc','-displayfd',str(write),'-geometry','1280x1000','-depth','24','-SecurityTypes','None','-localhost','yes','-nolisten','tcp'],pass_fds=(write,),stdout=log,stderr=log)
            os.close(write)
            try:
                assert select.select([read],[],[],15)[0],'Private display startup timed out'
                display=os.read(read,32).decode().strip();assert display.isdigit()
                env={**os.environ,'DISPLAY':':'+display,'HOME':str(work),'XDG_CONFIG_HOME':str(work/'config'),'XDG_CACHE_HOME':str(work/'cache'),'XDG_DATA_HOME':str(work/'data'),'XDG_RUNTIME_DIR':str(runtime),'NO_AT_BRIDGE':'1'}
                for mode in ('dark','light'):
                    args=[sys.executable,str(Path(__file__).resolve()),'--child',mode,str(icons)]
                    if '--test-only' not in sys.argv:args.append(str(ROOT/f'previews/icons/{mode}.png'))
                    subprocess.run(args,env=env,check=True,timeout=120)
            finally:
                os.close(read);server.terminate();server.wait(timeout=10)
    if '--test-only' not in sys.argv:
        import shutil
        dest=ROOT/'website/previews/icons';dest.mkdir(parents=True,exist_ok=True)
        for mode in ('dark','light'):shutil.copy2(ROOT/f'previews/icons/{mode}.png',dest/f'{mode}.png')

if __name__=='__main__':main()
