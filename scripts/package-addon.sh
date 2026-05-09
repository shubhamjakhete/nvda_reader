#!/usr/bin/env bash
set -euo pipefail

VERSION=$(grep '^version' manifest.ini | sed 's/version = "\(.*\)"/\1/')
OUTPUT="contextLabeler-${VERSION}.nvda-addon"

echo "Packaging version $VERSION → $OUTPUT"

# Build zip in a temp dir to control the layout
TMP=$(mktemp -d)
trap "rm -rf $TMP" EXIT

cp manifest.ini "$TMP/"
cp -r globalPlugins "$TMP/"

# Remove __pycache__ dirs from the bundle
find "$TMP" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find "$TMP" -name "*.pyc" -delete 2>/dev/null || true

cd "$TMP"
zip -r "../$(pwd | xargs basename).zip" . > /dev/null
cd -

mv "${TMP}.zip" "$OUTPUT" 2>/dev/null || (cd "$TMP" && zip -r "../../$OUTPUT" . > /dev/null)

# The zip was created relative to TMP; rebuild properly
rm -f "$OUTPUT"
(cd "$TMP" && zip -r - .) > "$OUTPUT"

echo "Done: $OUTPUT ($(du -sh $OUTPUT | cut -f1))"
