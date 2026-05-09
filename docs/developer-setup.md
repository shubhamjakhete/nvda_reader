# Developer Setup (Windows)

## Prerequisites

- Windows 10 or 11
- NVDA 2024.1 or newer — download from nvaccess.org
- Python 3.11 (only needed for vendoring; not needed to run NVDA)
- Git

## First-time setup

1. Clone the repo:
   ```
   git clone https://github.com/shubhamjakhete/nvda-context-labeler.git
   cd nvda-context-labeler
   ```

2. Vendor the dependencies (run once):
   ```powershell
   .\scripts\vendor-deps.ps1
   ```

3. Symlink the add-on into NVDA's scratchpad:
   ```powershell
   New-Item -ItemType SymbolicLink `
     -Path "$env:APPDATA\nvda\scratchpad\globalPlugins\contextLabeler" `
     -Target "$PWD\globalPlugins\contextLabeler"
   ```

4. Enable scratchpad in NVDA:
   - NVDA menu → Preferences → Settings → Advanced
   - Check "Enable loading of custom code from the Developer Scratchpad Directory"

5. Reload NVDA plugins: press `NVDA+Ctrl+F3` (or restart NVDA).

6. Add your Anthropic API key:
   - NVDA menu → Preferences → Settings → Context Labeler
   - Paste your key from console.anthropic.com

## Testing

Open `tests/test-bad-a11y.html` in any browser. Tab to an unlabeled button. Press `NVDA+Shift+L`. You should hear a label within 2 seconds.

## After code changes

Press `NVDA+Ctrl+F3` to reload plugins without restarting NVDA. Check the NVDA log (`NVDA+F1` → View Log) for errors.
