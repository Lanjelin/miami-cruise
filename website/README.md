# Miami Cruise website

A static, dependency-free website: search by app, an install page for each app with copy buttons and downloads (with SHA-256 checksums), and a palette page. It uses the Miami Cruise palette itself, follows the system dark/light setting, and makes no external requests.

| Path | What it is |
|---|---|
| `content.py` | Site-wide text (tagline, token descriptions) and the app list, which is built from the theme modules. |
| `generate.py` | Page templates, packaging and checks. |
| `assets/` | The site's CSS and JavaScript. |
| `assets/apps/` | Original app logos, pinned source/attribution records and licence notices. |
| `icons.py` | Discovers optional logos and validates their attribution records. |
| `previews/` | Screenshots of the site, used by the project README. |
| `render.sh` | Re-renders those screenshots. |
| `dist/` | The generated site. Not committed; this is what gets published. |

Reading styles use the existing palette's body-text token for instructions and important descriptions; secondary labels retain the muted token. Installation steps have generous spacing and wrapping code blocks. Terminal download commands are always visible. Checksums and detailed test coverage use native expandable sections, which also work without JavaScript. App galleries list dark and light as separate images; merged contact sheets are still emitted by the preview generators. Screenshots use uniform 16:10, uncropped preview frames without image padding; single previews are capped at 760px wide and clicking opens a native zoom dialog with fit/actual-size controls. Without JavaScript, the preview links open the original images.

The install steps are not written here: they come from each theme's `GUIDE`, so the website and the READMEs in `dist/` can't disagree. The logo and hero-scene artwork live in `../brand/`.

The home page and supported application pages include **Install with an agent**
with a copyable no-clone prompt linking to the repository installation contract.
App-page prompts scope the request to that app; web/CSS and token assets keep their
project-integration workflow. Prompt text lives in `content.py` and reuses the
existing accessible copy controls.

## Build and preview

```sh
python3 -I ../build.py          # builds the themes first, then the website
python3 -m http.server -d dist 8000
```

Then open <http://localhost:8000>. All links are relative, so `dist/index.html` also works opened straight from disk.

## Publish

One repository is enough. In GitHub, set **Settings, Pages, Source** to **GitHub Actions**. `.github/workflows/pages.yml` builds and deploys `website/dist` on every push to `main`. The site is published at https://lanjelin.github.io/miami-cruise. `SITE_URL` and `REPO_URL` in `../project.py` make the site add source links and `curl` download commands; update them if the repository moves.

## Add an app

Add a module to `../themes/` with its `GUIDE` (see `../docs/PORTING.md`) and rebuild. The site, the `dist/<app>/README.md` and the README apps table all pick it up; this folder needs no edit. The build fails on a broken link or a text-contrast pair below 4.5:1. With more than one category the index shows filter chips next to the search.

### Optional original app icon

Every app works without a logo: a short type badge is shown in the same tile. `GUIDE.mono` can specify a recognizable label of 1–4 characters (prefer 2–3). Without it, single-word names of up to four characters are kept; longer names use up to three initials, so Windows Terminal becomes `WT`. Long names are never squeezed into the tile. Four-character labels use a slightly smaller, fixed font size. Optional `badge_tone` is `accent` (default), `info` or `orchid`, using the matching dark/light palette. The build rejects oversized labels and unknown tones.

Adding an app never requires artwork. Web/CSS uses `CSS`, design tokens use `{}`, and eza uses `eza` because no standalone logo with clear reuse terms was identified. Original artwork always takes priority; the styled badge also appears if its image fails to load.

For a logo, first check the artwork's own reuse terms, not just the application's code licence. Add the unmodified original SVG as `assets/apps/<app_id>.svg`, and an accompanying `<app_id>.json` recording `name`, `creator`, `license`, `license_url`, commit-pinned `source`, licensing `evidence`, `changes` and the `checked` date. Include required licence notices locally and reference them with `license_file`. See the existing entries. No central registry or theme-module edit is needed.

The build validates these records, copies the assets without fetching anything and generates `credits.html`, linked from every footer. Logos retain their original colours and proportions, inside a shared Miami Cruise tile. Adjacent app names provide accessible labels; logos are decorative. Failed image loads reveal the text fallback when JavaScript is available. No icon fonts, CDNs or hotlinks are used.
