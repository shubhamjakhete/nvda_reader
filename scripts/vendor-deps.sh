#!/usr/bin/env bash
set -euo pipefail
VENDOR_DIR="globalPlugins/contextLabeler/_vendor"
rm -rf "$VENDOR_DIR"
mkdir -p "$VENDOR_DIR"
python3 -m pip install --target="$VENDOR_DIR" --no-deps rdflib==7.0.0
python3 -m pip install --target="$VENDOR_DIR" --no-deps pyparsing
python3 -m pip install --target="$VENDOR_DIR" --no-deps isodate
touch "$VENDOR_DIR/__init__.py"
echo "Vendored deps into $VENDOR_DIR"
