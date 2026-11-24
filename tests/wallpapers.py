#!/usr/bin/env python3
"""Approved fixed PNG integrity, safe metadata, byte-exact exports and downloads."""
from pathlib import Path
import hashlib
import json
import struct
import zlib
import zipfile
ROOT=Path(__file__).resolve().parents[1]


def png(path,size):
    data=path.read_bytes();assert data.startswith(b'\x89PNG\r\n\x1a\n'),path
    pos=8;compressed=[];header=None;seen=[]
    while pos<len(data):
        length=struct.unpack('>I',data[pos:pos+4])[0];kind=data[pos+4:pos+8];chunk=data[pos+8:pos+8+length]
        crc=struct.unpack('>I',data[pos+8+length:pos+12+length])[0]
        assert zlib.crc32(kind+chunk)&0xffffffff==crc,path
        seen.append(kind)
        assert kind not in (b'tEXt',b'iTXt',b'zTXt',b'eXIf'),(path,'unexpected identifying metadata')
        if kind==b'IHDR':header=struct.unpack('>IIBBBBB',chunk)
        if kind==b'IDAT':compressed.append(chunk)
        pos+=12+length
    assert pos==len(data) and seen[-1]==b'IEND',path
    assert header[:2]==size and header[2:]==(8,2,0,0,0),(path,header)
    rows=zlib.decompress(b''.join(compressed));stride=1+size[0]*3
    assert len(rows)==stride*size[1] and all(rows[i*stride]<=4 for i in range(size[1])),path
    return data


def main():
    metadata=json.loads((ROOT/'wallpapers/provenance.json').read_text())
    assert metadata['license']=='MIT'
    with zipfile.ZipFile(ROOT/'website/dist/downloads/miami-cruise-all.zip') as bundle:
        for mode in ('dark','light'):
            name=f'miami-coast-{mode}-4k.png'
            data=png(ROOT/'wallpapers'/name,(3840,2160))
            assert hashlib.sha256(data).hexdigest()==metadata['assets'][name]['sha256']
            assert data==(ROOT/'dist/wallpapers'/name).read_bytes()
            assert data==(ROOT/'website/dist/downloads/wallpapers'/name).read_bytes()
            assert data==bundle.read('miami-cruise/wallpapers/'+name)
            thumb=png(ROOT/f'previews/wallpapers/{mode}.png',(960,540))
            assert thumb==(ROOT/f'website/dist/previews/wallpapers/{mode}.png').read_bytes()
        assert bundle.read('miami-cruise/wallpapers/LICENSE.txt')==(ROOT/'LICENSE').read_bytes()
    page=(ROOT/'website/dist/apps/wallpapers.html').read_text()
    for word in ('AI-generated','super-resolution','3840','MIT'):
        assert word in page,word
    assert 'apps/wallpapers.html' in (ROOT/'website/dist/apps/xfce.html').read_text()
    # Artwork packaging must not introduce image/model dependencies into builds.
    assert not any(p.name in ('venv','models','uv-cache') for p in (ROOT/'wallpapers').rglob('*'))
    print('Wallpapers: approved image hashes, PNG CRC/decode/metadata, exact 4K exports, thumbnails, website and all-themes download passed')

if __name__=='__main__':main()
