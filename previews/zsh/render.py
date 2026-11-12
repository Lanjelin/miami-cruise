"""Capture native Zsh prompts in disposable shells; use Oh My Zsh when installed."""

import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import time

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / "previews")]
from _terminal import ansi_html


def render(output):
    omz = Path(os.environ.get("ZSH", Path.home() / ".local/share/oh-my-zsh"))
    for executable in ("zsh", "git", "tmux"):
        if not shutil.which(executable):
            raise SystemExit(f"Preview needs {executable}.")

    palettes = json.loads((ROOT / "dist/tokens/tokens.json").read_text())
    sections = []
    with tempfile.TemporaryDirectory(prefix="miami-zsh-") as scratch:
        base = Path(scratch)
        for variant, p in palettes.items():
            home = base / variant / "home"
            zdot = base / variant / "zdot"
            custom = base / variant / "custom"
            for folder in (home, zdot, custom / "themes"):
                folder.mkdir(parents=True)
            shutil.copyfile(ROOT / f"dist/zsh/miami-cruise-{variant}.zsh-theme",
                            custom / "themes" / f"miami-cruise-{variant}.zsh-theme")
            startup = (
                f'HOST=cruise\nZSH={str(omz)!r}\nZSH_CUSTOM={str(custom)!r}\n'
                f'ZSH_THEME=miami-cruise-{variant}\nplugins=()\n'
                'DISABLE_AUTO_UPDATE=true\nZSH_DISABLE_COMPFIX=true\n'
                'source "$ZSH/oh-my-zsh.sh"\n')
            if not (omz / "oh-my-zsh.sh").is_file():
                startup = f'HOST=cruise\nsource {str(custom / "themes" / f"miami-cruise-{variant}.zsh-theme")!r}\n'
            zdot.joinpath(".zshrc").write_text(startup)
            # Global zshenv may redirect ZDOTDIR to HOME/.config/zsh.
            (home / ".config/zsh").mkdir(parents=True)
            (home / ".config/zsh/.zshrc").symlink_to(zdot / ".zshrc")
            env = {k: v for k, v in os.environ.items()
                   if not k.startswith(("TMUX", "ZSH", "GIT_")) and k not in ("NO_COLOR", "FZF_DEFAULT_OPTS")}
            env.update(HOME=str(home), ZDOTDIR=str(zdot), TERM="tmux-256color",
                       COLORTERM="truecolor", LC_ALL="C.UTF-8", XDG_CONFIG_HOME=str(base / variant / "config"),
                       XDG_CACHE_HOME=str(base / variant / "cache"), GIT_CONFIG_GLOBAL=os.devnull,
                       GIT_CONFIG_NOSYSTEM="1", HISTFILE=str(base / variant / "history"))

            def git(*args, cwd=home):
                subprocess.run(["git", *args], cwd=cwd, env=env, check=True,
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            remote = base / variant / "remote.git"
            repo = home / "projects/miami-cruise"
            repo.mkdir(parents=True)
            git("init", "--bare", "--initial-branch=master", str(remote))
            git("init", "--initial-branch=master", cwd=repo)
            git("config", "user.name", "Preview", cwd=repo)
            git("config", "user.email", "preview@example.invalid", cwd=repo)
            (repo / "README.md").write_text("# Miami Cruise\n")
            git("add", "README.md", cwd=repo)
            git("commit", "-m", "Start theme", cwd=repo)
            git("remote", "add", "origin", str(remote), cwd=repo)
            git("push", "-u", "origin", "master", cwd=repo)
            for n in (1, 2):
                (repo / "palette.txt").write_text(f"Palette revision {n}\n")
                git("add", "palette.txt", cwd=repo)
                git("commit", "-m", f"Refine palette {n}", cwd=repo)
            (repo / "notes.txt").write_text("Preview notes\n")
            long = repo / "examples/summer-night-drive/configuration/integration/terminal/zsh"
            long.mkdir(parents=True)
            socket = base / variant / "tmux.sock"

            def tmux(*args, check=True):
                return subprocess.run(["tmux", "-S", str(socket), *args], cwd=repo,
                                      env=env, text=True, capture_output=True, check=check).stdout

            def screen():
                return tmux("capture-pane", "-p", "-e", "-t", "preview:0.0")

            def plain(value):
                return re.sub(r"\x1b\[[0-9;]*m", "", value)

            def wait_for(predicate, label):
                deadline = time.monotonic() + 10
                last = ""
                while time.monotonic() < deadline:
                    last = screen()
                    if predicate(plain(last)):
                        return last
                    time.sleep(.08)
                raise RuntimeError(f"Zsh preview timed out waiting for {label}:\n{plain(last)}")

            try:
                tmux("-f", os.devnull, "new-session", "-d", "-s", "preview", "-x", "98", "-y", "17",
                     "-c", str(repo), "zsh", "-i")
                tmux("set-option", "-g", "status", "off")
                wait_for(lambda s: "master ⇡2 ?1" in s and "~/projects/miami-cruise" in s, "initial prompt")
                tmux("send-keys", "-t", "preview:0.0", "git status --short", "Enter")
                wait_for(lambda s: "?? notes.txt" in s and s.count("master ⇡2 ?1") >= 2, "Git status")
                tmux("send-keys", "-t", "preview:0.0",
                     "cd examples/summer-night-drive/configuration/integration/terminal/zsh", "Enter")
                shot = wait_for(lambda s: "~/p/miami-cruise/" in s and s.count("master ⇡2 ?1") >= 3,
                                "adaptive path")
                for token in ("accent", "warning", "success", "info"):
                    rgb = ";".join(str(int(p[token][i:i + 2], 16)) for i in (1, 3, 5))
                    assert "38;2;" + rgb in shot, (variant, token)
                # This render host has no Powerline font. Substitute only the
                # missing branch glyph in the HTML; the prompt and its SGR
                # colours still come from the real tmux capture above.
                branch = ('<svg class="branch-symbol" viewBox="0 0 12 16" aria-label="branch">'
                          '<path d="M3 2v9a3 3 0 0 0 3 3h3M3 7a3 3 0 0 0 3 3h3"/>'
                          '<circle cx="3" cy="2" r="1.2"/><circle cx="9" cy="10" r="1.2"/>'
                          '<circle cx="9" cy="14" r="1.2"/></svg>')
                prompt_html = ansi_html(shot.rstrip(), p).replace("", branch)
                sections.append(
                    f'<section style="background:{p["bg"]};color:{p["text"]}">'
                    f'<header style="color:{p["accent"]}">Miami Cruise · Zsh · {variant}</header>'
                    f'<pre>{prompt_html}</pre></section>')
            finally:
                tmux("kill-server", check=False)

    css = ("body{margin:0;padding:14px;display:grid;gap:14px;background:transparent}"
           "section{border-radius:8px;overflow:hidden;padding:16px 20px}"
           "header{font:600 15px system-ui;margin-bottom:12px}"
           "pre{font:15px/1.25 'DejaVu Sans Mono',monospace;margin:0;white-space:pre}"
           ".branch-symbol{display:inline-block;width:9px;height:14px;vertical-align:-2px;"
           "fill:none;stroke:currentColor;stroke-width:1.25;stroke-linecap:round;stroke-linejoin:round}")
    output.write_text('<!doctype html><meta charset="utf-8"><style>' + css + '</style>' + ''.join(sections))
    print("Verified Zsh: both generated themes in isolated shells (Oh My Zsh when installed), Git ahead/untracked, adaptive path.",
          file=sys.stderr)


if __name__ == "__main__":
    render(Path(sys.argv[1]))
