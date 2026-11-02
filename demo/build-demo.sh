#!/usr/bin/env bash
# Builds the static interactive demo into demo/dist  (usage: bash demo/build-demo.sh)
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"; WEB="$HERE/../web"; OUT="$HERE/dist"
rm -rf "$OUT"; mkdir -p "$OUT/app"
cp -r "$WEB"/. "$OUT/app/"
cp "$HERE/demo-backend.js" "$OUT/app/vendor/supabase.js"          # the real client is replaced by the in-browser fake
rm -f "$OUT/app/vendor/ifinex-local.js" 2>/dev/null || true
cp "$HERE/demo-google.html" "$OUT/app/demo-google.html"           # simulated Google consent page (clearly labelled)
printf '{"format":"ifinex-server","version":1,"name":"iFiNeX DEMO","site":"","supabaseUrl":"https://demo.example.invalid","supabaseKey":"demo-not-a-real-key"}\n' > "$OUT/app/ifinex-config.json"
cp "$HERE"/*.html "$HERE/shared.css" "$HERE/viewer.js" "$HERE"/*.js "$OUT/" 2>/dev/null || true
rm -f "$OUT/demo-backend.js" "$OUT/demo-google.html.js" 2>/dev/null || true
mkdir -p "$OUT/shots"; [ -d "$HERE/shots" ] && cp "$HERE"/shots/* "$OUT/shots/" 2>/dev/null || true
touch "$OUT/.nojekyll"
echo "demo built: $OUT"
