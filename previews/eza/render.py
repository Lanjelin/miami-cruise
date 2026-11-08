"""Capture real eza output from a disposable fixture; convert its SGR colours to HTML.

Run after building: EZA=/path/to/eza python3 -I previews/eza/render.py out.html
The HTML supplies only the terminal background and default text, not listing colours.
"""
import html
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
EZA = shutil.which(os.environ.get("EZA", "eza"))
if not EZA:
    raise SystemExit("eza is required for this preview; set EZA=/path/to/eza")


def ansi_html(text):
    """Convert the reset/bold/underline/true-colour SGR emitted by this fixture."""
    out, style, start = [], {}, 0
    for match in re.finditer(r"\x1b\[([0-9;]*)m", text):
        chunk = html.escape(text[start:match.start()])
        out.append('<span style="' + ";".join(f"{k}:{v}" for k, v in style.items()) + '">' + chunk + "</span>")
        codes = [int(n) for n in match[1].split(";") if n] or [0]
        i = 0
        while i < len(codes):
            code = codes[i]
            if code == 0:
                style = {}
            elif code == 1:
                style["font-weight"] = "bold"
            elif code == 4:
                style["text-decoration"] = "underline"
            elif code in (38, 48) and codes[i + 1] == 2:
                style["color" if code == 38 else "background"] = "rgb(" + ",".join(map(str, codes[i + 2:i + 5])) + ")"
                i += 4
            else:
                raise ValueError(f"Unsupported SGR in eza preview: {codes}")
            i += 1
        start = match.end()
    out.append(html.escape(text[start:]))
    result = "".join(out)
    if "\x1b" in result:
        raise ValueError("Unconverted terminal escape in eza output")
    return result


def capture():
    tokens = json.loads((ROOT / "dist/tokens/tokens.json").read_text())
    with tempfile.TemporaryDirectory(prefix="miami-eza-preview-") as tmp:
        base = Path(tmp)
        files = base / "sample"
        files.mkdir()
        (files / "themes").mkdir()
        for name in ("README.md", "build.py", "removed.txt"):
            (files / name).write_text("Miami Cruise\n")
        env = {k: v for k, v in os.environ.items() if k not in
               ("LS_COLORS", "EZA_COLORS", "EXA_COLORS", "GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE")}
        env.update(LC_ALL="C", TZ="UTC", COLUMNS="120")

        def git(*args):
            subprocess.run(["git", *args], cwd=files, env=env, check=True, capture_output=True)

        git("init", "-b", "main")
        git("add", ".")
        git("-c", "user.name=Preview", "-c", "user.email=preview@example.invalid",
            "-c", "commit.gpgsign=false", "-c", "core.hooksPath=/dev/null", "commit", "-m", "Preview fixture")
        (files / "README.md").write_text("Miami Cruise\nUpdated guide\n")
        (files / "removed.txt").unlink()
        for name, size in (("photo.png", 24000), ("music.flac", 3200000), ("release.zip", 96000),
                           ("cache.tmp", 64), ("run.sh", 128)):
            with (files / name).open("wb") as f:
                f.truncate(size)
        (files / "run.sh").chmod(0o755)
        (files / "latest").symlink_to("README.md")
        (files / "broken").symlink_to("removed.txt")
        os.mkfifo(files / "events.pipe")
        for path in files.iterdir():
            os.utime(path, (1735689600, 1735689600), follow_symlinks=False)
        sections = []
        for variant in ("dark", "light"):
            config = base / variant
            config.mkdir()
            shutil.copyfile(ROOT / f"dist/eza/miami-cruise-{variant}.yml", config / "theme.yml")
            result = subprocess.run([EZA, "--long", "--header", "--git", "--no-user", "--no-time",
                                     "--icons=never", "--group-directories-first", "--color=always", "."],
                                    cwd=files, env={**env, "EZA_CONFIG_DIR": str(config)},
                                    check=True, capture_output=True, text=True)
            if result.stderr:
                raise RuntimeError(result.stderr)
            if not all(name in result.stdout for name in ("README.md", "themes", "broken")):
                raise RuntimeError("eza preview did not contain the expected fixture files")
            p = tokens[variant]
            title = "Miami Cruise" if variant == "dark" else "Miami Cruise Day"
            sections.append(f'<section style="background:{p["bg"]};color:{p["text"]}">'
                            f'<header style="color:{p["accent"]}">{title} · eza</header>'
                            f'<pre>{ansi_html(result.stdout)}</pre></section>')
        return '<!doctype html><meta charset="utf-8"><style>' + CSS + '</style>' + "".join(sections)


CSS = """body{margin:0;padding:14px;display:grid;gap:14px;background:transparent}
section{border-radius:8px;overflow:hidden;padding:16px 24px}
header{font:600 15px system-ui;margin-bottom:12px}
pre{font:16px/1.55 'DejaVu Sans Mono',monospace;margin:0;white-space:pre}
"""

if __name__ == "__main__":
    Path(sys.argv[1]).write_text(capture())
