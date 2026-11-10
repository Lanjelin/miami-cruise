"""Highlight groups shared by the Vim and Neovim themes.

core(p) returns {group: spec} with every colour already resolved to hex for palette p.
A spec is {"link": "Other"} or any of fg, bg, sp (hex) and bold, italic, underline, undercurl (True).
Nothing here is specific to one editor: Neovim-only groups live in nvim.py, Vim-only ones in vim.py.
"""
import math

from palette import luminance


def _rgb(h):
    return int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16)


def mix(a, b, t):
    """t = share of b in the result (0 = a, 1 = b); rounds like the Lua helper in nvim.py."""
    out = [math.floor(x + (y - x) * t + 0.5) for x, y in zip(_rgb(a), _rgb(b))]
    return "#%02x%02x%02x" % tuple(out)


def core(p, transparent=False):
    sel = mix(p["bg"], p["accent"], 0.20)

    def tint(token, t):
        return mix(p["bg"], p[token], t)

    on = p["on-accent"]
    groups = {
        # Editor
        "Normal": {"fg": p["text"], "bg": p["bg"]},
        "Cursor": {"fg": on, "bg": p["accent"]},
        "lCursor": {"link": "Cursor"},
        "CursorIM": {"link": "Cursor"},
        "CursorLine": {"bg": p["hover"]},
        "CursorColumn": {"bg": p["hover"]},
        "ColorColumn": {"bg": p["row"]},
        "LineNr": {"fg": p["disabled"]},
        "CursorLineNr": {"fg": p["accent"], "bold": True},
        "SignColumn": {"fg": p["disabled"], "bg": p["bg"]},
        "FoldColumn": {"fg": p["disabled"], "bg": p["bg"]},
        "Folded": {"fg": p["muted"], "bg": p["panel"]},
        "VertSplit": {"fg": p["border"]},
        "StatusLine": {"fg": p["text"], "bg": p["panel"]},
        "StatusLineNC": {"fg": p["muted"], "bg": p["panel"]},
        "TabLine": {"fg": p["muted"], "bg": p["panel"]},
        "TabLineSel": {"fg": p["accent"], "bg": p["bg"], "bold": True},
        "TabLineFill": {"bg": p["panel"]},
        "Pmenu": {"fg": p["text"], "bg": p["panel"]},
        "PmenuSel": {"fg": p["text"], "bg": sel, "bold": True},
        "PmenuSbar": {"bg": p["border"]},
        "PmenuThumb": {"bg": p["disabled"]},
        "WildMenu": {"link": "PmenuSel"},
        "Visual": {"bg": sel},
        "VisualNOS": {"bg": sel},
        "Search": {"fg": p["text"], "bg": tint("warning", 0.35)},
        "IncSearch": {"fg": on, "bg": p["accent"]},
        "MatchParen": {"fg": p["accent"], "bold": True, "underline": True},
        "NonText": {"fg": p["border"]},
        "Whitespace": {"fg": p["border"]},
        "EndOfBuffer": {"fg": p["bg"]},
        "SpecialKey": {"fg": p["border"]},
        "Conceal": {"fg": p["disabled"]},
        "Directory": {"fg": p["info"]},
        "Title": {"fg": p["accent"], "bold": True},
        "ErrorMsg": {"fg": p["danger"]},
        "WarningMsg": {"fg": p["warning"]},
        "MoreMsg": {"fg": p["success"]},
        "ModeMsg": {"fg": p["muted"]},
        "Question": {"fg": p["info"]},
        "QuickFixLine": {"bg": sel},
        "SpellBad": {"sp": p["danger"], "undercurl": True},
        "SpellCap": {"sp": p["warning"], "undercurl": True},
        "SpellLocal": {"sp": p["info"], "undercurl": True},
        "SpellRare": {"sp": p["orchid"], "undercurl": True},
        # Syntax: keywords carry the hero; everything else stays calm
        "Comment": {"fg": p["disabled"], "italic": True},
        "Constant": {"fg": p["orange"]},
        "String": {"fg": p["success"]},
        "Character": {"fg": p["success"]},
        "Number": {"fg": p["orange"]},
        "Boolean": {"fg": p["orange"]},
        "Float": {"fg": p["orange"]},
        "Identifier": {"fg": p["text"]},
        "Function": {"fg": p["info"]},
        "Statement": {"fg": p["accent"]},
        "Conditional": {"fg": p["accent"]},
        "Repeat": {"fg": p["accent"]},
        "Label": {"fg": p["accent"]},
        "Keyword": {"fg": p["accent"]},
        "Exception": {"fg": p["accent"]},
        "Operator": {"fg": p["muted"]},
        "PreProc": {"fg": p["orchid"]},
        "Include": {"fg": p["orchid"]},
        "Define": {"fg": p["orchid"]},
        "Macro": {"fg": p["orchid"]},
        "PreCondit": {"fg": p["orchid"]},
        "Type": {"fg": p["orchid"]},
        "StorageClass": {"fg": p["orchid"]},
        "Structure": {"fg": p["orchid"]},
        "Typedef": {"fg": p["orchid"]},
        "Special": {"fg": p["warning"]},
        "SpecialChar": {"fg": p["warning"]},
        "Tag": {"fg": p["info"]},
        "Delimiter": {"fg": p["muted"]},
        "SpecialComment": {"fg": p["muted"], "italic": True},
        "Debug": {"fg": p["orange"]},
        "Underlined": {"fg": p["info"], "underline": True},
        "Ignore": {"fg": p["disabled"]},
        "Error": {"fg": p["danger"]},
        "Todo": {"fg": on, "bg": p["warning"], "bold": True},
        # Diff
        "DiffAdd": {"bg": tint("success", 0.18)},
        "DiffChange": {"bg": tint("warning", 0.15)},
        "DiffDelete": {"bg": tint("danger", 0.18)},
        "DiffText": {"bg": tint("warning", 0.32)},
    }
    if transparent:
        for name in ("Normal", "SignColumn", "FoldColumn"):
            groups[name].pop("bg")
    return groups


def ansi(p):
    """16 terminal colours. The hero is magenta; bright variants reuse the base colours.

    Slots 0, 7, 8 and 15 are the neutral ramp. On a dark palette it runs dark to light;
    on a light palette black is the text colour and white a light neutral, so 'black' stays readable.
    """
    c = [p["danger"], p["success"], p["warning"], p["orchid"], p["accent"], p["info"]]
    if luminance(p["bg"]) > 0.5:
        return [p["text"]] + c + [p["border"], p["disabled"]] + c + [p["panel"]]
    return [p["border"]] + c + [p["muted"], p["disabled"]] + c + [p["text"]]
