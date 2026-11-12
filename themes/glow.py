"""Native Glamour JSON styles for Glow's Markdown renderer, not its browser UI."""
import json

from palette import contrast


def style(p):
    def colour(token, **kwargs):
        return dict(color=p[token], **kwargs)

    # Keep familiar Markdown typography and markers. These structural choices
    # are explicit because a custom Glamour stylesheet is not a colour overlay.
    result = dict(
        document=colour('text', background_color=p['bg'], block_prefix='\n', block_suffix='\n', margin=2),
        block_quote=colour('muted', indent=1, indent_token='│ '),
        paragraph={}, list=dict(level_indent=2),
        heading=colour('accent', bold=True, block_suffix='\n'),
        h1=colour('on-accent', background_color=p['accent'], bold=True, prefix=' ', suffix=' '),
        h2=dict(prefix='## '), h3=dict(prefix='### '), h4=dict(prefix='#### '),
        h5=dict(prefix='##### '), h6=dict(prefix='###### '),
        text={}, emph=dict(italic=True), strong=dict(bold=True),
        strikethrough=dict(crossed_out=True),
        hr=colour('muted', format='\n--------\n'),
        item=dict(block_prefix='• '), enumeration=dict(block_prefix='. '),
        task=dict(ticked='[✓] ', unticked='[ ] '),
        link=colour('info', underline=True), link_text=colour('info', bold=True),
        image=colour('info', underline=True), image_text=colour('muted', format='Image: {{.text}} →'),
        code=colour('text', background_color=p['panel'], prefix='\u00a0', suffix='\u00a0'),
        code_block=colour('text', background_color=p['bg'], margin=2),
        table=colour('text'), definition_list={}, definition_term=colour('info', bold=True),
        definition_description=dict(block_prefix='\n→ '), html_block={}, html_span={},
    )
    roles = dict(
        text='text', error='danger', comment='disabled', comment_preproc='orchid',
        keyword='accent', keyword_reserved='accent', keyword_namespace='accent', keyword_type='orchid',
        operator='muted', punctuation='muted', name='text', name_builtin='info', name_tag='accent',
        name_attribute='info', name_class='orchid', name_constant='orange', name_decorator='orchid',
        name_exception='orchid', name_function='info', name_other='text', literal='text',
        literal_number='orange', literal_date='orange', literal_string='success', literal_string_escape='warning',
        generic_deleted='danger', generic_emph='text', generic_inserted='success',
        generic_strong='text', generic_subheading='accent',
    )
    chroma = {key: colour(token) for key, token in roles.items()}
    chroma['comment']['italic'] = True
    chroma['generic_emph']['italic'] = True
    chroma['generic_strong']['bold'] = True
    chroma['generic_subheading']['bold'] = True
    chroma['error']['underline'] = True
    chroma['background'] = dict(background_color=p['bg'])
    result['code_block']['chroma'] = chroma

    def check(node, inherited_fg=p['text'], inherited_bg=p['bg']):
        fg, bg = node.get('color', inherited_fg), node.get('background_color', inherited_bg)
        if contrast(fg, bg) < 4.5:
            raise ValueError(f'Glow: {fg} on {bg} is below 4.5:1')
        for child in node.values():
            if isinstance(child, dict):
                check(child, fg, bg)

    check(result)
    return result


GUIDE = dict(
    name='Glow', category='Reading & monitoring', mono='Glow',
    tags=['Markdown', 'Reader'], aliases='glow glamour markdown md reader documentation',
    status='Markdown verified with Glow 3.0.0 on Linux; browser/pager chrome is not themed',
    tagline='Readable Markdown, magenta headings and matching code syntax in your terminal.',
    files=[(f'glow/miami-cruise-{v}.json', f'miami-cruise-{v}.json',
            f'Glamour Markdown style · {v}, palette background') for v in ('dark', 'light')],
    file_note='Native Glamour JSON styles for rendered Markdown, not replacement glow.yml files. Glow itself is unmodified. Browser lists, help bars and pager chrome retain their built-in colours. These files do not change keybindings, paging, wrapping or file discovery.',
    shots=[("glow/dark.png", "Real Glow Markdown output with the dark theme: headings, links, quotes, lists, tables and code"),
           ("glow/light.png", "Real Glow Markdown output with the light theme: headings, links, quotes, lists, tables and code")],
    tested='Glow 3.0.0 (Glamour 2.0.1) on Linux: dark/light styles, file and stdin input, config loading and CLI style precedence, headings, emphasis, quotes, lists/tasks, tables, inline code, Python/JSON/diff/plain code blocks, true-colour output and width control. Browser/pager chrome intentionally not themed; macOS/Windows not tested',
    variants='Dark and light, with palette backgrounds',
    covers='Markdown body, headings, emphasis, links/images, quotes, rules, lists/tasks, tables, definitions, inline code and fenced-code syntax',
    glow='No: the flat palette (Glow is the application name)',
    steps=[('Try a Markdown style', [
        ('p', 'Install Glow and use a true-colour terminal with a matching dark or light background. Keep these JSON files in a permanent folder. Back up same-named customized files before copying. There is no bat dependency, syntax-cache build or patched Glow binary.'),
        ('code', [('Linux / macOS', 'bash', 'mkdir -p ~/.config/glow/styles\ncp miami-cruise-*.json ~/.config/glow/styles/\nglow -s "$HOME/.config/glow/styles/miami-cruise-dark.json" README.md'),
                  ('Windows (PowerShell)', 'powershell', '$styles = Join-Path $env:APPDATA "glow/styles"\nNew-Item -ItemType Directory -Force $styles | Out-Null\nCopy-Item miami-cruise-*.json $styles\nglow -s (Join-Path $styles "miami-cruise-dark.json") README.md')]),
        ('p', 'Choose dark or light to match your terminal. Each style paints the Miami Cruise palette background for Markdown body and fenced code, with accent fills on inline code and first-level headings. Glow has no separate background toggle in glow.yml: switch the style path to choose the other file. Its built-in auto selection does not switch between custom files.'),
        ('note', 'Markdown body colours (headings, links, quotes, tables) render true-colour. Fenced-code syntax highlighting goes through Chroma\'s terminal256 formatter, so those colours are quantized to the nearest of 256 terminal colours and can look very slightly off from the exact palette hex.'),
    ]), ('Keep your current Glow settings', [
        ('p', 'For persistence, edit only the style key in your existing glow.yml, preserving pager, width, mouse and other settings. Run glow --help to find your platform\'s config path, or glow config to open it. Use the actual absolute JSON path; the example below must be adapted to your machine.'),
        ('code', [(None, 'yaml', 'style: "/absolute/path/to/miami-cruise-dark.json"')]),
        ('note', 'This is a complete Markdown stylesheet, not a merge with another custom stylesheet. Familiar heading prefixes, list markers, quote bars and emphasis are included. Glow\'s -s flag overrides the style key. Keep your existing width and paging preferences; the theme does not set them.'),
        ('code', [('Linux / macOS', 'bash', '# Optional one-off width, without editing config:\nglow -s "$HOME/.config/glow/styles/miami-cruise-light.json" -w 80 README.md')]),
    ]), ('Scope and removal', [
        ('p', 'The same Markdown style can be used when reading documents in Glow\'s TUI. It does not theme the file browser, search/list selection, status/help bars or other application chrome. No upstream patch or custom Glow build is involved.'),
        ('p', 'To uninstall, restore your previous style key (or remove it to use Glow\'s default auto style) and stop passing this JSON path via -s. Then remove only the two Miami Cruise JSON files. Other Glow settings stay intact.'),
        ('note', 'Tested with Glow 3.0.0 on Linux. The JSON format is Glamour\'s native Markdown styling API; older versions and other platforms are not verified. Reference: https://github.com/charmbracelet/glow#styles'),
    ])],
)


def export(pals, dist):
    out = dist / 'glow'
    out.mkdir(parents=True, exist_ok=True)
    for variant, (p, _) in pals.items():
        (out / f'miami-cruise-{variant}.json').write_text(json.dumps(style(p), indent=2) + '\n')
