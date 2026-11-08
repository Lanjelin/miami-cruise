# Shared helpers for the per-app preview scripts. Source it from previews/<app>/render.sh:
#   cd "$(dirname "$0")/../.." && . previews/lib.sh
# Gives you $tmp (a scratch folder removed on exit) and shot SIZE OUT.png /path/to/page.html
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
shot() {
  brave-browser --headless=new --no-sandbox --disable-gpu --hide-scrollbars --default-background-color=00000000 \
    --window-size="$1" --screenshot="$2" "file://$3" >/dev/null 2>&1
}
