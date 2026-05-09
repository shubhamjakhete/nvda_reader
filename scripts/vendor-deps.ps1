$ErrorActionPreference = "Stop"
$VENDOR_DIR = "globalPlugins\contextLabeler\_vendor"
if (Test-Path $VENDOR_DIR) { Remove-Item -Recurse -Force $VENDOR_DIR }
New-Item -ItemType Directory -Path $VENDOR_DIR | Out-Null
pip install --target="$VENDOR_DIR" --no-deps rdflib==7.0.0
pip install --target="$VENDOR_DIR" --no-deps pyparsing
pip install --target="$VENDOR_DIR" --no-deps isodate
New-Item -ItemType File -Path "$VENDOR_DIR\__init__.py" | Out-Null
Write-Host "Vendored deps into $VENDOR_DIR"
