"""Convert real tmux SGR screen captures to HTML; shared by TUI previews."""
import html
import re
from themes._hl import ansi


def ansi_html(screen, p):
    """Convert a tmux-rendered screen, not a mock UI or a raw terminal stream."""
    colours = ansi(p)
    out, style, start = [], {}, 0

    def colour(index):
        if index < 16:
            return colours[index]
        if index < 232:
            n = index - 16
            levels = (0, 95, 135, 175, 215, 255)
            return '#%02x%02x%02x' % (levels[n // 36], levels[(n // 6) % 6], levels[n % 6])
        return '#%02x%02x%02x' % ((8 + (index - 232) * 10,) * 3)

    def span(chunk):
        current = dict(style)
        if current.pop('reverse', False):
            fg, bg = current.get('color', p['text']), current.get('background', p['bg'])
            current.update(color=bg, background=fg)
        return ('<span style="' + ';'.join(f'{k}:{v}' for k, v in current.items()) + '">' +
                html.escape(chunk) + '</span>')

    for match in re.finditer(r'\x1b\[([0-9;]*)m', screen):
        out.append(span(screen[start:match.start()]))
        codes = [int(n) for n in match[1].split(';') if n] or [0]
        i = 0
        while i < len(codes):
            c = codes[i]
            if c == 0:
                style = {}
            elif c in (1, 2, 3, 4, 7, 9):
                key, value = {1: ('font-weight', 'bold'), 2: ('opacity', '.65'),
                              3: ('font-style', 'italic'), 4: ('text-decoration', 'underline'),
                              7: ('reverse', True), 9: ('text-decoration', 'line-through')}[c]
                style[key] = value
            elif c in (22, 23, 24, 27, 29, 39, 49):
                for key in {22: ['font-weight', 'opacity'], 23: ['font-style'],
                            24: ['text-decoration'], 27: ['reverse'], 29: ['text-decoration'],
                            39: ['color'], 49: ['background']}[c]:
                    style.pop(key, None)
            elif 30 <= c <= 37 or 90 <= c <= 97:
                style['color'] = colour(c - 30 if c < 90 else c - 90 + 8)
            elif 40 <= c <= 47 or 100 <= c <= 107:
                style['background'] = colour(c - 40 if c < 100 else c - 100 + 8)
            elif c in (38, 48):
                key = 'color' if c == 38 else 'background'
                if codes[i + 1] == 2:
                    style[key] = '#%02x%02x%02x' % tuple(codes[i + 2:i + 5])
                    i += 4
                elif codes[i + 1] == 5:
                    style[key] = colour(codes[i + 2])
                    i += 2
                else:
                    raise ValueError(f'Unhandled SGR {codes}')
            else:
                raise ValueError(f'Unhandled SGR {codes}')
            i += 1
        start = match.end()
    out.append(span(screen[start:]))
    result = ''.join(out)
    if '\x1b' in result:
        raise ValueError('Unconverted screen escape')
    return result

