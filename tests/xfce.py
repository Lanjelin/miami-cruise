#!/usr/bin/env python3
"""Package integrity, local CSS asset coverage, deterministic build and source rebuild."""
import hashlib
from pathlib import Path
import re
import subprocess
import sys
import tarfile
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from palette import contrast

archives = sorted((ROOT/'dist/xfce').glob('*.tar.gz'))
assert len(archives)==3
before = {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in archives}
subprocess.run([sys.executable,'-I','build.py','xfce'],cwd=ROOT,check=True)
assert before=={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in archives}
for path in archives:
    with tarfile.open(path) as archive:
        assert all(m.isfile() and not m.name.startswith('/') and '..' not in Path(m.name).parts for m in archive)
        if 'source' in path.name: continue
        prefix = path.name.removesuffix('.tar.gz')+'/'
        names = set(archive.getnames())
        assert {prefix+n for n in ('gtk-3.0/gtk.css','gtk-3.0/gtk-dark.css','xfwm4/themerc','xfwm4/close-active.png','index.theme','LICENSE.GPL','README.md')} <= names
        css = archive.extractfile(prefix+'gtk-3.0/gtk.css').read().decode()
        assets = re.findall(r'url\([\'"]?(assets/[^)\'" ]+)',css)
        assert assets and all(prefix+'gtk-3.0/'+asset in names for asset in assets)
        assert 'resource:///' not in css
        # Apps also consume public GTK colour names rather than matching CSS
        # nodes. Audit both focused and unfocused semantic pairs directly.
        colors=dict(re.findall(r'@define-color (\w+) (#[0-9a-fA-F]{6});',css))
        for fg,bg in [('theme_fg_color','theme_bg_color'),('theme_text_color','theme_base_color'),
                      ('theme_unfocused_fg_color','theme_unfocused_bg_color'),
                      ('theme_unfocused_text_color','theme_unfocused_base_color'),
                      ('theme_selected_fg_color','theme_selected_bg_color'),
                      ('theme_unfocused_selected_fg_color','theme_unfocused_selected_bg_color')]:
            assert contrast(colors[fg],colors[bg])>=4.5,(path.name,fg,bg)
        # No build-host identity/paths may enter distributable theme content.
        for member in archive:
            content = archive.extractfile(member).read()
            assert b'/home/' not in content
with tempfile.TemporaryDirectory() as tmp:
    with tarfile.open(ROOT/'dist/xfce/miami-cruise-xfce-source.tar.gz') as archive:
        archive.extractall(tmp,filter='data')
    source=Path(tmp)/'miami-cruise-xfce-source'
    subprocess.run([sys.executable,'-I','build.py'],cwd=source,check=True)
    assert all(hashlib.sha256((source/'dist/xfce'/name).read_bytes()).hexdigest()==digest for name,digest in before.items())
print('XFCE: archive integrity, CSS asset coverage, repeatability, and standalone source rebuild passed')
