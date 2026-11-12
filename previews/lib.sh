# Shared helpers for the per-app preview scripts. Source it from previews/<app>/render.sh:
#   cd "$(dirname "$0")/../.." && . previews/lib.sh
# Gives you $tmp (removed on exit) and shot SIZE OUT.png /path/to/page.html [SELECTOR NAME...]
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
# Optional trailing SELECTOR NAME... also exports each generated DOM panel.
# Node 22+ supplies native WebSocket; no npm dependencies or persistent profiles.
shot() {
  node previews/screenshot.mjs "$@"
}
