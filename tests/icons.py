#!/usr/bin/env python3
"""Full source coverage, safe archive contents, alias parity and offline rebuild."""
import hashlib
import io
import json
import re
import subprocess
import sys
import tarfile
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from themes.icons import upstream, SVG, XLINK

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def package(path):
    with tarfile.open(path) as tar:
        root=tar.getmembers()[0].name.split('/')[0]+'/'
        files={}
        for m in tar.getmembers():
            assert m.isfile() and not m.name.startswith('/') and '..' not in Path(m.name).parts,m.name
            assert m.uid==m.gid==0 and m.mode==0o644
            files[m.name.removeprefix(root)]=tar.extractfile(m).read()
        return files

def main():
    originals,aliases,index=upstream()
    assert len(originals)==1152 and len(aliases)==2708
    before={p.name:digest(p) for p in (ROOT/'dist/icons').glob('*.tar.gz')}
    assert len(before)==3
    for variant in ('Dark','Light'):
        files=package(ROOT/f'dist/icons/Miami-Cruise-Candy-{variant}.tar.gz')
        assert set(originals)|set(aliases)=={n for n in files if n.split('/')[0] in ('apps','devices','mimetypes','places','preferences','status')}
        assert {'LICENSE','upstream.json','README.md','index.theme','CHANGES.md'}<=files.keys()
        for alias,target in aliases.items():assert files[alias]==files[target],alias
        raster=0
        for name,data in originals.items():
            tree=ET.fromstring(files[name]);source=ET.fromstring(data)
            for attr in ('viewBox','width','height'):
                assert source.get(attr)==tree.get(attr),(name,attr)
            # Colour adaptation must never alter shapes, positions or dimensions.
            for tag in ('path','rect','circle','ellipse','polygon','polyline','line','image','text','tspan'):
                a=list(source.iter('{'+SVG+'}'+tag));b=list(tree.iter('{'+SVG+'}'+tag));assert len(a)==len(b),(name,tag)
                for orig,new in zip(a,b):
                    for attr in ('d','points','x','y','x1','x2','y1','y2','width','height','cx','cy','r','rx','ry','transform'):
                        assert orig.get(attr)==new.get(attr),(name,attr)
            for node in tree.iter():
                assert node.tag.rsplit('}',1)[-1] not in ('script','foreignObject'),name
                for k,v in node.attrib.items():
                    for url in re.findall(r'url\(([^)]+)\)',v):
                        assert url.strip("\"' ").startswith('#'),(name,url)
                    assert not re.fullmatch(r'on(?:load|click|error|mouseover|begin|end)',k,re.I),name
                    if k in ('href','{'+XLINK+'}href'):
                        assert v.startswith(('#','data:image/png;base64,')),(name,k)
            images=[n.get('{'+XLINK+'}href',n.get('href')) for n in tree.iter('{'+SVG+'}image')]
            original_images=[n.get('{'+XLINK+'}href',n.get('href')) for n in source.iter('{'+SVG+'}image')]
            assert images==original_images,name
            raster+=bool(images)
            assert not re.search(rb'/home/|/Users/|192\.168\.|BEGIN .*PRIVATE KEY',files[name]),name
        assert raster==4
        print(f'{variant}: 1,152 shapes preserved, 2,708 aliases matched, 4 embedded bitmaps unchanged')
    subprocess.run([sys.executable,'-I','build.py','icons'],cwd=ROOT,check=True)
    assert before=={p.name:digest(p) for p in (ROOT/'dist/icons').glob('*.tar.gz')}
    with tempfile.TemporaryDirectory(prefix='miami-candy-source-') as tmp:
        # package() already verifies source archive has regular members only.
        source_archive=ROOT/'dist/icons/miami-cruise-candy-source.tar.gz';package(source_archive)
        with tarfile.open(source_archive) as tar:tar.extractall(tmp,filter='data')
        source=Path(tmp)/'miami-cruise-candy-source'
        subprocess.run([sys.executable,'-I','build.py'],cwd=source,check=True)
        assert all(digest(source/'dist/icons'/n)==d for n,d in before.items())
    print('Source provenance, complete coverage, safe archives, privacy, repeatability and offline rebuild passed')
if __name__=='__main__':main()
