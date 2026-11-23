#!/usr/bin/python3
"""Decode every native title-button state; produce an enlarged review atlas."""
from pathlib import Path
import tarfile
import gi
gi.require_version('GdkPixbuf','2.0')
from gi.repository import GdkPixbuf
ROOT=Path(__file__).resolve().parents[1]
kinds=('menu','hide','maximize','maximize-toggled','close','shade','shade-toggled','stick','stick-toggled')
states=('active','inactive','prelight','pressed')
atlas=GdkPixbuf.Pixbuf.new(GdkPixbuf.Colorspace.RGB,True,8,len(kinds)*44,8*52)
atlas.fill(0x444444ff)
for v,mode in enumerate(('Dark','Light')):
    with tarfile.open(ROOT/'dist/xfce'/f'Miami-Cruise-{mode}.tar.gz') as archive:
        count=0
        for x,kind in enumerate(kinds):
            images=[]
            for y,state in enumerate(states):
                data=archive.extractfile(f'Miami-Cruise-{mode}/xfwm4/{kind}-{state}.png').read()
                loader=GdkPixbuf.PixbufLoader.new_with_type('png')
                loader.write(data);loader.close();pix=loader.get_pixbuf()
                assert (pix.get_width(),pix.get_height())==(20,24)
                pixels=pix.get_pixels();stride=pix.get_rowstride()
                colours={tuple(pixels[j*stride+i*4:j*stride+i*4+3]) for j in range(4,23) for i in range(20)}
                assert len(colours)>2, (mode,kind,state,'blank or broken symbol')
                assert all(pixels[j*stride+i*4+3]==255 for j in range(24) for i in range(20))
                pix.scale_simple(40,48,GdkPixbuf.InterpType.NEAREST).copy_area(0,0,40,48,atlas,x*44,(v*4+y)*52)
                images.append(data);count+=1
            assert len(set(images))==4,(mode,kind,'missing state distinction')
        assert archive.extractfile(f'Miami-Cruise-{mode}/xfwm4/maximize-active.png').read()!=archive.extractfile(f'Miami-Cruise-{mode}/xfwm4/maximize-toggled-active.png').read()
        print(mode+': '+str(count)+' native window-button assets decoded; distinct states verified')
out=ROOT/'previews/xfce/review';out.mkdir(exist_ok=True)
atlas.savev(str(out/'window-buttons.png'),'png',[],[])
