"""Dependency-free recolouring of Greybird's 8-bit PNG assets."""
import struct
import zlib


def recolor_png(data, color):
    chunks, offset, compressed = [], 8, b''
    while offset < len(data):
        size = struct.unpack('>I', data[offset:offset+4])[0]
        kind, body = data[offset+4:offset+8], data[offset+8:offset+8+size]
        offset += size + 12
        if kind == b'IDAT':
            compressed += body
        else:
            chunks.append((kind, body))
    width, height, bits, typ, comp, filt, interlace = struct.unpack('>IIBBBBB', chunks[0][1])
    if (bits != 8 and typ != 3) or interlace:
        raise ValueError('Unsupported upstream PNG; review asset before updating vendor snapshot')
    if typ == 3:
        chunks = [(k, bytes(v for i in range(0,len(b),3) for v in color(tuple(b[i:i+3])))) if k == b'PLTE' else (k,b) for k,b in chunks]
        pixels = compressed
    else:
        channels = {2:3, 6:4, 0:1, 4:2}.get(typ)
        if channels is None:
            raise ValueError(f'Unsupported upstream PNG colour type {typ}')
        raw = zlib.decompress(compressed)
        stride = width * channels
        prev = bytearray(stride)
        output = bytearray()
        pos = 0
        for _ in range(height):
            f = raw[pos]
            row = bytearray(raw[pos+1:pos+1+stride])
            pos += 1 + stride
            for i in range(stride):
                a, b = (row[i-channels] if i >= channels else 0), prev[i]
                c = prev[i-channels] if i >= channels else 0
                if f == 0: predictor = 0
                elif f == 1: predictor = a
                elif f == 2: predictor = b
                elif f == 3: predictor = (a+b)//2
                elif f == 4:
                    p = a+b-c
                    distances = (abs(p-a), abs(p-b), abs(p-c))
                    predictor = (a,b,c)[distances.index(min(distances))]
                else: raise ValueError('Unknown PNG filter')
                row[i] = (row[i] + predictor) % 256
            prev = row[:]
            colored = bytearray()
            for i in range(0,stride,channels):
                if typ in (0,4):
                    colored.extend(color((row[i],)*3))
                    if typ == 4: colored.append(row[i+1])
                else:
                    colored.extend(color(tuple(row[i:i+3])))
                    if typ == 6: colored.append(row[i+3])
            output.append(0)
            output.extend(colored)
        pixels = zlib.compress(output, 9)
        if typ in (0,4):
            chunks[0] = (b'IHDR',struct.pack('>IIBBBBB',width,height,8,6 if typ==4 else 2,comp,filt,interlace))
    result = bytearray(b'\x89PNG\r\n\x1a\n')
    for kind, body in chunks:
        if kind == b'IEND':
            blocks = [(b'IDAT',pixels), (kind,body)]
        else: blocks = [(kind,body)]
        for k,b in blocks:
            result.extend(struct.pack('>I',len(b))+k+b+struct.pack('>I',zlib.crc32(k+b)))
    return bytes(result)


def xpm_to_png(text):
    """Rasterize the vendored single-character XPMs without external tooling."""
    import ast
    import re
    strings = [ast.literal_eval(s) for s in re.findall(r'"(?:[^"\\]|\\.)*"',text)]
    w,h,n,cpp = map(int,strings[0].split())
    palette = {}
    for line in strings[1:n+1]:
        key, spec = line[:cpp], line[cpp:].strip().split()
        if spec[0] != 'c': raise ValueError('Unexpected XPM color syntax')
        palette[key] = (b'\0\0\0\0' if spec[1]=='None' else bytes.fromhex(spec[1][1:])+b'\xff')
    raw = b''.join(b'\0'+b''.join(palette[row[i:i+cpp]] for i in range(0,w*cpp,cpp)) for row in strings[n+1:n+1+h])
    result = b'\x89PNG\r\n\x1a\n'
    for kind,body in [(b'IHDR',struct.pack('>IIBBBBB',w,h,8,6,0,0,0)),(b'IDAT',zlib.compress(raw,9)),(b'IEND',b'')]:
        result += struct.pack('>I',len(body))+kind+body+struct.pack('>I',zlib.crc32(kind+body))
    return result


def window_button(p, kind, state):
    """Draw clean native 20x24 Xfwm buttons; 4x coverage, no shaded base glyphs."""
    from palette import rgb
    import math
    glyphs = {
        'close': [(6,9,14,17),(14,9,6,17)],
        'hide': [(6,16,14,16)],
        'maximize': [(6,9,14,9),(14,9,14,17),(14,17,6,17),(6,17,6,9)],
        'maximize-toggled': [(6,11,12,11),(12,11,12,17),(12,17,6,17),(6,17,6,11),
                             (8,9,14,9),(14,9,14,15)],
        'menu': [(6,10,14,10),(6,13,14,13),(6,16,14,16)],
        'shade': [(6,14,10,10),(10,10,14,14)],
        'shade-toggled': [(6,11,10,15),(10,15,14,11)],
        'stick': [(10,9,14,13),(14,13,10,17),(10,17,6,13),(6,13,10,9)],
        'stick-toggled': [(10,9,14,13),(14,13,10,17),(10,17,6,13),(6,13,10,9),
                          (10,11,10,15),(8,13,12,13)],
    }
    ink = rgb(p['muted' if state == 'inactive' else 'text'])
    surface = rgb(p['panel'])
    fill = surface
    if state in ('prelight','pressed'):
        role = 'danger' if kind == 'close' else 'accent' if state == 'pressed' else 'hover'
        fill = rgb(p[role])
        ink = rgb(p['on-accent' if role in ('danger','accent') else 'text'])
    def distance(x,y,line):
        a,b,c,d = line
        t = max(0,min(1,((x-a)*(c-a)+(y-b)*(d-b))/((c-a)**2+(d-b)**2)))
        return math.hypot(x-a-t*(c-a),y-b-t*(d-b))
    raw = bytearray()
    for y in range(24):
        raw.append(0)
        for x in range(20):
            total = [0,0,0]
            for sy in range(4):
                for sx in range(4):
                    px,py=x+(sx+.5)/4,y+(sy+.5)/4
                    # Rounded highlight inside a flat, title-matched tile.
                    dx,dy=max(abs(px-10)-5,0),max(abs(py-13)-6,0)
                    inside=math.hypot(dx,dy)<=3
                    color=fill if inside else surface
                    if min(distance(px,py-(1 if state=='pressed' else 0),line) for line in glyphs[kind]) <= .65:
                        color=ink
                    if y==0: color=rgb(p['border'])
                    for i,c in enumerate(color):total[i]+=c
            raw.extend(round(c/16) for c in total)
            raw.append(255)
    result=bytearray(b'\x89PNG\r\n\x1a\n')
    for kind,body in [(b'IHDR',struct.pack('>IIBBBBB',20,24,8,6,0,0,0)),
                      (b'IDAT',zlib.compress(bytes(raw),9)),(b'IEND',b'')]:
        result.extend(struct.pack('>I',len(body))+kind+body+struct.pack('>I',zlib.crc32(kind+body)))
    return bytes(result)
