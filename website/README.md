# Miami Cruise website

A static, dependency-free website: search by app, an install page for each app with copy buttons and downloads (with SHA-256 checksums), and a palette page. It uses the Miami Cruise palette itself, follows the system dark/light setting, and makes no external requests.

| Path | What it is |
|---|---|
| `content.py` | What the site says: the apps, install steps and URLs. This is the file you edit. |
| `generate.py` | Page templates, packaging and checks. |
| `assets/` | The site's CSS and JavaScript. |
| `previews/` | Screenshots of the site, used by the project README. |
| `render.sh` | Re-renders those screenshots. |
| `dist/` | The generated site. Not committed; this is what gets published. |

The logo and hero-scene artwork are shared with the rest of the project and live in `../brand/`.

## Build and preview

```sh
python3 -I ../build.py          # builds the themes first, then the website
python3 -m http.server -d dist 8000
```

Then open <http://localhost:8000>. All links are relative, so `dist/index.html` also works opened straight from disk.

## Publish

One repository is enough. In GitHub, set **Settings, Pages, Source** to **GitHub Actions**. `.github/workflows/pages.yml` builds and deploys `website/dist` on every push to `main`. The site is published at https://lanjelin.github.io/miami-cruise. `SITE_URL` and `REPO_URL` in `content.py` make the site add source links and `curl` download commands; update them if the repository moves.

## Add an app

Add an entry to `APPS` in `content.py` (name, files, install steps, tags) and put its screenshots under `../previews/`. The build fails on a broken link or a text-contrast pair below 4.5:1.
