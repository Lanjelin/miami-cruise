"""Verify native Yazi flavors and capture their actual ANSI screens."""

import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import time
import zipfile

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / "previews")]
from _terminal import ansi_html


def capture(output):
    yazi = shutil.which(os.environ.get("YAZI", "yazi"))
    if not yazi or not shutil.which("tmux"):
        raise SystemExit("Preview needs Yazi and tmux; set YAZI if needed.")
    tokens = json.loads((ROOT / "dist/tokens/tokens.json").read_text())
    sections = []
    with tempfile.TemporaryDirectory(prefix="miami-yazi-") as scratch:
        base = Path(scratch)
        files = base / "night-drive"
        files.mkdir()
        (files / "assets").mkdir()
        (files / "src").mkdir()
        (files / "README.md").write_text("# Miami Cruise\n\nDark and light, one palette.\n")
        (files / "cruise.py").write_text("# Miami Cruise\n\ndef route(city: str) -> str:\n    return f'Night drive to {city}'\n\nprint(route('Ocean Drive'))\n")
        (files / "palette.json").write_text('{"accent": "magenta", "status": "ready"}\n')
        with zipfile.ZipFile(files / "archive.zip", "w") as z:
            z.writestr("notes.txt", "Preview fixture\n")

        for variant, p in tokens.items():
            config = base / variant / "config"
            flavors = config / "flavors"
            flavors.mkdir(parents=True)
            archive = ROOT / f"dist/yazi/miami-cruise-{variant}.yazi.zip"
            with zipfile.ZipFile(archive) as z:
                z.extractall(flavors)
            # Detached tmux cannot answer Yazi's asynchronous appearance probe.
            # Apply the exact flavor.toml content as a user theme for the capture;
            # the ZIPs and flavor selection are verified separately.
            flavor = flavors / f"miami-cruise-{variant}.yazi/flavor.toml"
            syntax = flavors / f"miami-cruise-{variant}.yazi/tmtheme.xml"
            theme = flavor.read_text().replace("\n[indicator]",
                f'\nsyntect_theme = "{syntax}"\n\n[indicator]', 1)
            (config / "theme.toml").write_text(theme +
                "\n# Preview-only: this render host has no Nerd Font. The distributed flavor keeps Yazi's icons.\n"
                "[icon]\nglobs = []\ndirs = []\nfiles = []\nexts = []\nconds = []\n")
            env = {k: v for k, v in os.environ.items() if not k.startswith(("TMUX", "YAZI_")) and k != "NO_COLOR"}
            env.update(YAZI_CONFIG_HOME=str(config), XDG_CACHE_HOME=str(base / variant / "cache"),
                       XDG_STATE_HOME=str(base / variant / "state"), TERM="tmux-256color",
                       COLORTERM="truecolor", LC_ALL="C.UTF-8", YAZI_LOG="debug")
            socket = base / variant / "tmux.sock"

            def tmux(*args, check=True):
                return subprocess.run(["tmux", "-S", str(socket), *args], env=env,
                                      cwd=files, capture_output=True, text=True, check=check).stdout

            def screen():
                return tmux("capture-pane", "-p", "-e", "-t", "preview:0.0")

            def plain(value):
                return re.sub(r"\x1b\[[0-9;]*m", "", value)

            def wait_for(predicate, label):
                deadline = time.monotonic() + 12
                last = ""
                while time.monotonic() < deadline:
                    last = screen()
                    if predicate(last):
                        return last
                    time.sleep(.08)
                log = base / variant / "state/yazi/yazi.log"
                raise RuntimeError(f"Yazi {variant}: timed out waiting for {label}:\n{plain(last)}\nANSI: {last[:600]!r}\nLog: {log.read_text()[-2500:] if log.exists() else 'none'}")

            def stable_screen():
                previous = None
                for _ in range(12):
                    current = screen()
                    if current == previous:
                        return current
                    previous = current
                    time.sleep(.1)
                return previous

            try:
                tmux("-f", os.devnull, "new-session", "-d", "-s", "preview", "-x", "116", "-y", "18",
                     yazi, str(files))
                tmux("set-option", "-g", "status", "off")
                color = lambda token, kind="38": kind + ";2;" + ";".join(
                    str(int(p[token][i:i + 2], 16)) for i in (1, 3, 5))
                shot = wait_for(lambda s: "cruise.py" in plain(s) and color("accent") in s and
                                color("accent", "48") in s, "flavor colours and file list")
                tmux("send-keys", "-t", "preview:0.0", "j", "j", "j")
                wait_for(lambda s: "Night drive" in plain(s), "text preview")
                shot = stable_screen()
                assert color("accent", "48") in shot, "selected-file accent fill missing"
                for token in ("accent", "text", "info", "success"):
                    assert color(token) in shot, (variant, token)
                # Keep the screenshot stable and avoid publishing a random
                # scratch path. Only the displayed path is normalized.
                shot = shot.replace(str(files), "/home/demo/projects/night-drive")
                sections.append(f'<section style="background:{p["bg"]};color:{p["text"]}">'
                                f'<header style="color:{p["accent"]}">Miami Cruise · Yazi · {variant}</header>'
                                f'<pre>{ansi_html(shot, p)}</pre></section>')
                tmux("send-keys", "-t", "preview:0.0", "F1")
                wait_for(lambda s: "mgr.help" in plain(s) and color("accent") in s, "help dialog")
            finally:
                tmux("kill-server", check=False)
    css = ("body{margin:0;padding:14px;display:grid;gap:14px;background:transparent}"
           "section{border-radius:8px;overflow:hidden;padding:16px 20px}"
           "header{font:600 15px system-ui;margin-bottom:12px}"
           "pre{font:13px/16px 'DejaVu Sans Mono',monospace;margin:0;white-space:pre}")
    output.write_text('<!doctype html><meta charset="utf-8"><style>' + css + '</style>' + ''.join(sections))
    print("Verified Yazi: both packaged color schemes as direct themes, UI colours, file lists, previews and help in isolated configs.",
          file=sys.stderr)


if __name__ == "__main__":
    capture(Path(sys.argv[1]))
