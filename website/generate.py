"""Website generator: a static, dependency-free site (GitHub Pages ready) written to website/dist/.

Pages: index (search by app), one page per app (install steps, downloads, previews), palette.
The site is styled with the Miami Cruise tokens themselves and follows the system dark/light
setting, with a Dark/Light override that is remembered. All links are relative, so it works
from a project path such as https://user.github.io/miami-cruise/ or from a folder on disk.

Reads the theme files in ../dist/ and packages them as downloads, so build the themes first.
Content (apps, steps, URLs) lives in content.py; page templates and checks live here.
"""
import hashlib
import html
import re
import shutil
import zipfile
from pathlib import Path

from palette import TOKEN_ORDER, VERSION, contrast
from themes import GROUPS
from themes import _hl
from themes.brand import BRAND, brand_values, fill

ROOT = Path(__file__).resolve().parent.parent  # project root
WEB = Path(__file__).resolve().parent  # website/

from .content import APPS, REPO_URL, SITE_URL, TAGLINE, TOKEN_USE
from .icons import ASSETS as ICON_ASSETS, ICONS

# --------------------------------------------------------------------- helpers


def esc(s):
    return html.escape(s, quote=True)


def app_icon(app, up=""):
    if not 1 <= len(app["mono"]) <= 4:
        raise ValueError(f'{app["id"]}: mono badge label must be 1–4 characters')
    tone = app.get("badge_tone", "accent")
    if tone not in ("accent", "info", "orchid"):
        raise ValueError(f'{app["id"]}: badge_tone must be accent, info or orchid')
    fallback = f'<span class="icon-fallback">{esc(app["mono"])}</span>'
    image = (f'<img src="{up}assets/apps/{esc(app["id"])}.svg" alt="" width="40" height="40">'
             if app["id"] in ICONS and not app.get("text_badge") else "")
    return f'<div class="app-icon badge-{tone} badge-length-{len(app["mono"])}" aria-hidden="true">{fallback}{image}</div>'


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def human_size(n):
    return f"{n} B" if n < 1024 else f"{n / 1024:.1f} KB"


def check_contrast(pals):
    """Fail the build if a pairing the site relies on drops below 4.5:1."""
    pairs = [("text", "bg"), ("text", "panel"), ("muted", "bg"), ("muted", "panel"), ("muted", "hover"),
             ("accent", "bg"), ("accent", "panel"), ("info", "bg"), ("warning", "bg"), ("on-accent", "accent"),
             ("text", "hover"), ("disabled", "panel")]
    for name, (p, _) in pals.items():
        for fg, bg in pairs:
            ratio = contrast(p[fg], p[bg])
            if ratio < 4.5:
                raise SystemExit(f"site: {name} {fg} on {bg} is {ratio:.2f}:1, below 4.5:1")


def check_links(out: Path):
    bad = []
    for page in out.rglob("*.html"):
        text = page.read_text()
        for m in re.finditer(r'(?:href|src)="([^"]+)"', text):
            ref = m.group(1)
            if re.match(r"^(https?:|mailto:|#|data:|javascript:)", ref):
                continue
            target = (page.parent / ref.split("#")[0].split("?")[0]).resolve()
            if not target.exists():
                bad.append(f"{page.relative_to(out)} -> {ref}")
    if bad:
        raise SystemExit("site: broken links:\n  " + "\n  ".join(bad))


# ------------------------------------------------------------------ rendering

THEME_INIT = ("<script>(function(){try{var t=new URLSearchParams(location.search).get('theme')||localStorage.getItem('mc-theme');"
              "if(t==='dark'||t==='light')document.documentElement.setAttribute('data-theme',t);}catch(e){}})();</script>")


def page(title, desc, body, up="", current=""):
    def nav(label, href, key):
        cur = ' aria-current="page"' if key == current else ""
        return f'<a href="{up}{href}"{cur}>{label}</a>'

    repo = f'<a href="{esc(REPO_URL)}">Source</a>' if REPO_URL else ""
    links = nav("Apps", "index.html#apps", "apps") + nav("Palette", "palette.html", "palette") + repo
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="color-scheme" content="dark light">
<link rel="icon" href="{up}assets/mark.svg" type="image/svg+xml">
<link rel="stylesheet" href="{up}assets/style.css">
{THEME_INIT}
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="top"><div class="wrap">
  <a class="brand" href="{up}index.html"><img src="{up}assets/mark.svg" alt="" width="32" height="32"><span>Miami Cruise</span></a>
  <nav aria-label="Main">{links}</nav>
  <div class="seg" role="group" aria-label="Colour theme">
    <button type="button" data-set="auto" aria-pressed="true">Auto</button>
    <button type="button" data-set="dark" aria-pressed="false">Dark</button>
    <button type="button" data-set="light" aria-pressed="false">Light</button>
  </div>
</div></header>
<main id="main">
{body}
</main>
<footer><div class="wrap">
  <span>Miami Cruise v{VERSION} · MIT licence</span>
  <span><a href="{up}credits.html">App icon credits &amp; licences</a> · {('<a href="' + esc(REPO_URL) + '">Source</a>') if REPO_URL else ''}</span>
</div></footer>
<script src="{up}assets/app.js" defer></script>
</body>
</html>
"""


def code_block(os_label, lang, text):
    label = f'<span class="os">{esc(os_label)}</span>' if os_label else ""
    return (f'<div class="code">{label}<pre><code class="lang-{esc(lang)}">{esc(text)}</code></pre>'
            f'<button type="button" class="copy" hidden aria-label="Copy to clipboard">Copy</button></div>')


def render_steps(app, downloads):
    items = []
    for n, (title, blocks) in enumerate([download_step(app, downloads)] + list(app["steps"])):
        parts = []
        for kind, content in blocks:
            if kind == "p":
                parts.append(f"<p>{content}</p>")
            elif kind == "note":
                parts.append(f'<p class="note">{content}</p>')
            elif kind == "warn":
                parts.append(f'<p class="note warn">{content}</p>')
            elif kind == "code":
                parts.extend(code_block(*c) for c in content)
        if n == 0 and SITE_URL and app.get('download_cli', True):
            cmds = [(None, "bash", "\n".join(f'curl -fsSLO {SITE_URL.rstrip("/")}/{d["href"]}' for d in downloads))]
            parts.append('<details class="disclosure"><summary>Download from a terminal instead</summary>' + code_block(*cmds[0]) + "</details>")
        items.append(f"<li><h3>{esc(title)}</h3>{''.join(parts)}</li>")
    return '<ol class="steps">' + "".join(items) + "</ol>"


def download_step(app, downloads):
    names = " and ".join(f'<a href="../{d["href"]}" download><code>{esc(d["name"])}</code></a>' for d in downloads)
    text = app.get('download_intro', f"Download {names}.")
    needs_terminal = any(
        kind == "code" and any(label for label, _, _ in content)
        for _, blocks in app["steps"] for kind, content in blocks
    )
    if needs_terminal:
        text += f" Then open a terminal in the folder where {'it was' if len(downloads) == 1 else 'they were'} saved (usually <code>Downloads</code>)."
    blocks = [("p", text)]
    if app.get("file_note"):
        blocks.append(("note", app["file_note"]))
    return ("Download", blocks)


def app_page(app, downloads):
    dl = "".join(
        f'<a class="btn mc-primary" href="../{d["href"]}" download>Download <small>{esc(d["name"])} · {d["size"]}</small></a>'
        f'<details class="checksum"><summary>SHA-256 checksum</summary><code>{d["sha"]}</code></details>'
        for d in downloads
    )
    shots = ""
    if app["shots"]:
        figs = "".join(
            f'<figure><a class="shot-preview" href="../previews/{esc(src)}" data-zoom aria-label="Enlarge screenshot: {esc(alt)}"><img src="../previews/{esc(src)}" alt="{esc(alt)}" loading="lazy"></a><figcaption>{esc(alt)}</figcaption></figure>'
            for src, alt in app["shots"]
        )
        shots = f'<div class="shots">{figs}</div>'
    facts = "".join(f"<li><b>{k}</b><br>{esc(v)}</li>" for k, v in (
        ("Variants", app.get("variants", "Dark and light")), ("Covers", app["covers"]), ("Glow", app["glow"])))
    body = f"""<div class="wrap">
<p class="crumbs"><a href="../index.html">Miami Cruise</a> / <a href="../index.html#apps">Apps</a> / {esc(app['name'])}</p>
<div class="apphead">{app_icon(app, '../')}
  <div><h1>{esc(app['name'])}</h1><p>{esc(app['tagline'])}</p></div></div>
{shots}
<div class="layout">
  <section class="instructions" aria-labelledby="install"><h2 id="install">Install</h2>{render_steps(app, downloads)}</section>
  <aside class="side">
    <div class="box"><h2>Download</h2><div class="dl">{dl}</div></div>
    <div class="box"><h2>About</h2><ul class="facts">{facts}</ul><details class="disclosure"><summary>Tested environments and coverage</summary><p>{esc(app["tested"])}</p></details></div>
  </aside>
</div>
</div>"""
    return page(f"{app['name']} · Miami Cruise", f"Install Miami Cruise for {app['name']}: {app['tagline']}", body, up="../", current="apps")


def swatch(token, hexv):
    return (f'<button type="button" class="swatch" data-hex="{hexv}" aria-label="Copy {esc(token)} {hexv}">'
            f'<i style="background:{hexv}"></i><span><b>{esc(token)}</b><code>{hexv}</code></span></button>')


def index_page(scene, pals, zip_info):
    def card(a):
        search = (a["name"] + " " + a["aliases"] + " " + " ".join(a["tags"]) +
                  " " + a["category"] + " " + a["tagline"]).lower()
        return (f'<li data-card data-cat="{esc(a["category"])}" data-search="{esc(search)}">'
                f'<a class="card" href="apps/{a["id"]}.html">{app_icon(a)}'
                f'<strong>{esc(a["name"])}</strong><p>{esc(a["tagline"])}</p>'
                f'<ul class="tags">{"".join(f"<li class=tag>{esc(t)}</li>" for t in a["tags"])}</ul></a></li>')

    cats = [c for c in GROUPS if any(a["category"] == c for a in APPS)]
    groups = "".join(
        f'<section class="app-group" data-group="{esc(c)}"><h3>{esc(c)}</h3>'
        f'<ul class="grid">{"".join(card(a) for a in APPS if a["category"] == c)}</ul></section>'
        for c in cats
    )
    chips = ""
    if len(cats) > 1:
        buttons = '<button type="button" data-cat-set="" aria-pressed="true">All</button>' + "".join(
            f'<button type="button" data-cat-set="{esc(c)}" aria-pressed="false">{esc(c)}</button>' for c in cats)
        chips = f'<div class="chips" role="group" aria-label="Filter by app group">{buttons}</div>'
    dark = pals["dark"][0]
    strip = "".join(swatch(k, dark[k]) for k in ("bg", "panel", "border", "text", "accent", "success", "warning", "danger", "info", "orange", "orchid"))
    zip_btn = (f'<a class="btn ghost" href="{zip_info["href"]}" download>Download everything <small>{zip_info["size"]}</small></a>')
    body = f"""<div class="wrap">
<section class="hero">
  <div>
    <h1>Miami <em>Cruise</em></h1>
    <p class="lead">{esc(TAGLINE)}</p>
    <div class="cta"><a class="btn mc-primary" href="#apps">Pick your app</a><a class="btn ghost" href="palette.html">See the palette</a></div>
  </div>
  <div class="scene">{scene}</div>
</section>
</div>
<section class="section" id="apps"><div class="wrap">
  <h2>Find your app</h2>
  <p class="sub">Every app has its own page with downloads and step-by-step setup for macOS, Linux and Windows.</p>
  <label class="search" for="q"><span class="sr">Search apps</span>
    <input id="q" type="search" placeholder="Search apps: nvim, vim, wezterm, css…" autocomplete="off" spellcheck="false">
    <kbd aria-hidden="true">/</kbd></label>
  {chips}
  <p class="count" id="count" aria-live="polite"></p>
  <div class="app-groups" id="app-groups">{groups}</div>
  <p class="empty" id="empty" hidden>No app matches that yet. The <a href="apps/tokens.html">design tokens</a> work for anything.</p>
  <p style="margin-top:22px">{zip_btn}</p>
</div></section>
<section class="section"><div class="wrap">
  <h2>The palette</h2>
  <p class="sub">Click a swatch to copy its hex. <span id="copied" class="hl" aria-live="polite"></span></p>
  <div class="swatches">{strip}</div>
  <p style="margin-top:18px"><a href="palette.html">All tokens, light variant and contrast ratios →</a></p>
</div></section>"""
    return page("Miami Cruise: a night-drive colour scheme",
                "Miami Cruise is a dark and light colour scheme with teal-ink neutrals and one magenta hero accent. Themes for Neovim, Vim, WezTerm and the web.",
                body, current="")


def credits_page():
    items = []
    for app_id, meta in ICONS.items():
        notice = (f' · <a href="assets/apps/{esc(meta["license_file"])}">Full licence notice</a>'
                  if meta.get("license_file") else "")
        items.append(
            f'<section class="box"><h2>{esc(meta["name"])}</h2>'
            f'<p>Artwork: {esc(meta["creator"])}. '
            f'<a href="{esc(meta["license_url"])}">{esc(meta["license"])}</a>{notice}.</p>'
            f'<p><a href="{esc(meta["source"])}">Original SVG source</a> · '
            f'<a href="{esc(meta["evidence"])}">Licence reference</a> · '
            f'<a href="assets/apps/{esc(app_id)}.svg">Local SVG</a></p>'
            f'<p>Changes: {esc(meta["changes"])} Checked {esc(meta["checked"])}.</p></section>'
        )
    body = ('<div class="wrap section"><h1>App icon credits</h1>'
            '<p class="lead">App cards use text badges. Original artwork is retained here with its attribution '
            'for reference; the SVGs retain their original colours and proportions.</p>'
            '<p>Third-party logos are covered by their own licences, not the Miami Cruise MIT licence. '
            'Names and trademarks belong to their respective owners; no endorsement is implied. '
            'Apps without a suitable logo use a text fallback.</p>'
            '<div class="credits">' + ''.join(items) + '</div></div>')
    return page('App icon credits · Miami Cruise', 'Sources, creators and licences for app artwork.', body)


def palette_page(pals):
    sections = ""
    for name, label in (("dark", "Dark"), ("light", "Light")):
        p = pals[name][0]
        sections += (f'<div class="ramp"><h3>{label}</h3><div class="swatches">'
                     + "".join(swatch(k, p[k]) for k in TOKEN_ORDER) + "</div></div>")
    rows = ""
    d, l = pals["dark"][0], pals["light"][0]
    for k in TOKEN_ORDER:
        def cr(p):
            if k == "on-accent":
                return f"{contrast(p[k], p['accent']):.1f}"
            if k in ("bg", "panel", "border", "hover", "row", "focus"):
                return "–"
            return f"{contrast(p[k], p['bg']):.1f}"
        rows += (f'<tr><td><code>{k}</code></td><td>{esc(TOKEN_USE[k])}</td>'
                 f'<td><span class="dot" style="background:{d[k]}"></span><code>{d[k]}</code></td><td>{cr(d)}</td>'
                 f'<td><span class="dot" style="background:{l[k]}"></span><code>{l[k]}</code></td><td>{cr(l)}</td></tr>')
    body = f"""<div class="wrap">
<p class="crumbs"><a href="index.html">Miami Cruise</a> / Palette</p>
<div class="section">
  <h1>Palette</h1>
  <p class="lead">Seventeen tokens, defined once in OKLCH and shared by every app. Click a swatch to copy its hex. <span id="copied" class="hl" aria-live="polite"></span></p>
  {sections}
  <h2 style="margin-top:30px">Tokens and contrast</h2>
  <p class="sub" style="color:var(--mc-muted)">Contrast is measured against <code>bg</code> (<code>on-accent</code> against <code>accent</code>). Every text and accent colour is at least 4.5:1.</p>
  <div class="tablewrap"><table><thead><tr><th>Token</th><th>Use</th><th>Dark</th><th>Contrast</th><th>Light</th><th>Contrast</th></tr></thead><tbody>{rows}</tbody></table></div>
  <h2 style="margin-top:30px">Design</h2>
  <ul>
    <li><b>One hero, calm supporting colours.</b> Magenta is the only loud colour. It marks the primary action, selection, focus and links.</li>
    <li><b>Teal-ink neutrals.</b> Every neutral shares one tinted hue; dark and light differ only in lightness.</li>
    <li><b>Meaning never depends on glow.</b> Selection is a tint plus a solid stripe and focus is a solid outline. The glow only decorates them.</li>
    <li><b>Contrast by construction.</b> The build adjusts each colour until it meets its minimum, and fails if it can't.</li>
  </ul>
  <h2 style="margin-top:30px">Logo</h2>
  <p class="sub" style="color:var(--mc-muted)">A night road toward a magenta sunset. Use the mark at small sizes and the logo from about 64px up. Both are SVG.</p>
  <div class="logos">
    <figure><img src="assets/logo.svg" alt="Miami Cruise logo" width="128" height="128"><figcaption><a href="assets/logo.svg" download>logo.svg</a></figcaption></figure>
    <figure><img src="assets/mark.svg" alt="Miami Cruise mark" width="128" height="128"><figcaption><a href="assets/mark.svg" download>mark.svg</a></figcaption></figure>
  </div>
  <p style="margin-top:20px"><a class="btn" href="apps/tokens.html">Get the tokens as JSON</a></p>
</div>
</div>"""
    return page("Palette · Miami Cruise", "The Miami Cruise palette: tokens, hex values and contrast ratios for dark and light.", body, current="palette")


def not_found():
    body = '<div class="wrap section"><h1>Page not found</h1><p class="lead">That page drove off the map.</p><p><a class="btn" href="index.html">Back to Miami Cruise</a></p></div>'
    return page("Not found · Miami Cruise", "Page not found", body)


# ---------------------------------------------------------------------- export


def export(pals, dist: Path):
    """dist is the themes output folder (input here); the website is written to website/dist/."""
    needed = {"nvim", "vim", "wezterm", "web", "tokens", "brand"}
    missing = sorted(t for t in needed if not (dist / t).is_dir())
    if missing:
        raise SystemExit(f"site: build these targets first: {', '.join(missing)} (python3 -I build.py builds all in order)")
    check_contrast(pals)

    out = WEB / "dist"
    if out.exists():
        shutil.rmtree(out)
    for sub in ("assets", "apps", "downloads", "previews"):
        (out / sub).mkdir(parents=True)

    # brand + assets
    dark = pals["dark"][0]
    bv = brand_values(dark)
    scene = fill((BRAND / "scene.svg.tpl").read_text(), bv)
    shutil.copy(dist / "brand/logo.svg", out / "assets/logo.svg")
    shutil.copy(dist / "brand/mark.svg", out / "assets/mark.svg")
    css_vars = (dist / "web/miami-cruise.css").read_text() + "\n" + (dist / "web/glow.css").read_text()
    light_vars = "\n".join(f"    --mc-{k}: {pals['light'][0][k]};" for k in TOKEN_ORDER)
    auto = f"\n@media (prefers-color-scheme: light) {{\n  :root:not([data-theme]) {{\n    color-scheme: light;\n{light_vars}\n  }}\n}}\n\n"
    (out / "assets/style.css").write_text(css_vars + auto + (WEB / "assets/style.css").read_text())
    shutil.copy(WEB / "assets/app.js", out / "assets/app.js")
    shutil.copytree(ICON_ASSETS, out / "assets/apps")

    # previews used by the pages
    for app in APPS:
        for src, _ in app["shots"]:
            dest = out / "previews" / src
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(ROOT / "previews" / src, dest)

    # downloads
    per_app = {}
    for app in APPS:
        items = []
        for src, name, label in app["files"]:
            dest = out / "downloads" / app["id"] / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(dist / src, dest)
            items.append(dict(href=f"downloads/{app['id']}/{name}", name=name, label=f"Download {name}",
                              size=human_size(dest.stat().st_size), sha=sha256(dest)))
        per_app[app["id"]] = items
    zpath = out / "downloads/miami-cruise-all.zip"
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for app in APPS:
            for src, name, _ in app["files"]:
                zi = zipfile.ZipInfo(f"miami-cruise/{app['id']}/{name}", date_time=(2026, 1, 1, 0, 0, 0))
                zi.compress_type = zipfile.ZIP_DEFLATED
                z.writestr(zi, (dist / src).read_bytes())
        zi = zipfile.ZipInfo("miami-cruise/LICENSE", date_time=(2026, 1, 1, 0, 0, 0))
        zi.compress_type = zipfile.ZIP_DEFLATED
        z.writestr(zi, (ROOT / "LICENSE").read_bytes())
    zip_info = dict(href="downloads/miami-cruise-all.zip", size=human_size(zpath.stat().st_size))

    # pages
    (out / "index.html").write_text(index_page(scene, pals, zip_info))
    (out / "palette.html").write_text(palette_page(pals))
    (out / "credits.html").write_text(credits_page())
    (out / "404.html").write_text(not_found())
    for app in APPS:
        (out / "apps" / f"{app['id']}.html").write_text(app_page(app, per_app[app["id"]]))
    check_links(out)
