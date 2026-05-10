# contextLabeler — Ontology-Constrained AI Labeling for NVDA

An NVDA add-on that speaks meaningful labels for unlabeled UI elements — icon buttons, alt-less images, custom widgets — using Claude AI validated against a hand-edited W3C ontology.

**The problem:** Screen readers depend on developers correctly labeling UI elements. In practice, large portions of modern apps fail this. When a blind user navigates to an unlabeled button, NVDA announces *"button"* — no label, no context. Trial-and-error activation is slow and risky.

**The fix:** Press `NVDA+Shift+L` on any unlabeled element. The add-on extracts context from the focused element, sends it to Claude Haiku, validates the response against a local ontology, and speaks a label — all in under 2 seconds.

```
[user presses NVDA+Shift+L on an icon button]
         ↓
NVDA reads: "mute toggle — toggle icon button"
```

---

## How It Works

```
[NVDA+Shift+L pressed]
        |
        ↓
  context.extract(focused_object)
  → {role, name, class, parent, siblings, app, window_title}
        |
        ↓
  classifier.classify(ctx)
  → POST api.anthropic.com/v1/messages  (Claude Haiku)
  → {"category": "...#ToggleIconButton", "label": "mute toggle"}
        |
        ↓
  ontology.is_valid_leaf(category_uri)
  → SPARQL ASK query against local ontology.ttl
        |
     valid?
    /      \
  yes       no → speak fallback, log warning
   |
   ↓
  ui.message("mute toggle — toggle icon button")
  → cache result for instant repeat
```

The key design decision: Claude is the *guesser*, the ontology is the *constraint*. Every category Claude returns is validated via a SPARQL `ASK` query before being spoken. No hallucinated categories reach the user.

---

## The Ontology

The ontology (`globalPlugins/contextLabeler/ontology.ttl`) is a hand-edited RDF/Turtle file — plain text, readable by anyone. It defines the vocabulary of UI element types Claude is allowed to use:

```
UIElement
├── Control
│   ├── Button
│   │   ├── CommandButton       — button with visible text
│   │   └── IconButton
│   │       ├── ActionIconButton  — one-shot action (save, delete, send)
│   │       └── ToggleIconButton  — binary state (mute/unmute, play/pause)
│   ├── Input
│   │   ├── TextInput
│   │   └── SearchInput
│   └── Selector
│       ├── Dropdown
│       ├── Checkbox
│       └── RadioButton
├── Display
│   ├── Image
│   │   ├── DecorativeImage
│   │   ├── InformativeImage
│   │   └── FunctionalImage
│   └── Icon
│       ├── StatusIcon
│       └── BrandIcon
├── Navigation
│   ├── Link
│   ├── Tab
│   └── MenuItem
└── Unknown                     — fallback sentinel
```

Claude can only return leaf classes (classes with no subclasses). The SPARQL query `FILTER NOT EXISTS { ?child rdfs:subClassOf ?leaf }` enforces this. Want to add a new category? Add a class to the Turtle file and it's live on next reload — no code changes needed.

---

## Tech Stack

| Layer | Choice | Why |
|---|---|---|
| Host | NVDA 2024.1+ (Windows) | Target runtime |
| Language | Python 3.11 (NVDA bundled) | No system Python required |
| Add-on type | Global plugin | Works across all apps |
| Ontology format | RDF/Turtle | W3C standard, hand-readable, version-controllable |
| Ontology library | RDFLib 7.x (vendored) | Pure Python, no native deps, SPARQL support |
| Query language | SPARQL 1.1 | Validation + hierarchy traversal |
| AI model | Claude Haiku (`claude-haiku-4-5-20251001`) | Fast (~400–800ms), cheap, reliable JSON output |
| HTTP client | `urllib.request` (stdlib) | No extra deps needed for one POST endpoint |
| Cache | In-memory dict (500 entries, LRU eviction) | Instant repeat presses |
| Settings UI | NVDA `gui.settingsDialogs.SettingsPanel` | Native NVDA settings panel |

**Vendored dependencies** (committed to repo, no pip at runtime):
- `rdflib` ~1.5 MB
- `pyparsing` ~250 KB
- `isodate` ~50 KB

Total add-on bundle: ~2 MB.

---

## Repository Structure

```
nvda_reader/
├── manifest.ini                           # NVDA add-on metadata
├── globalPlugins/
│   └── contextLabeler/
│       ├── __init__.py                    # GlobalPlugin, hotkey, orchestration
│       ├── context.py                     # NVDAObject → context dict
│       ├── classifier.py                  # Claude API wrapper + prompt templates
│       ├── ontology.py                    # RDFLib graph wrapper + SPARQL
│       ├── queries.py                     # SPARQL query string constants
│       ├── ontology.ttl                   # the ontology (hand-edited Turtle)
│       ├── cache.py                       # in-memory result cache
│       ├── settings.py                    # NVDA settings panel (API key)
│       └── _vendor/                       # vendored RDFLib + deps
├── tests/
│   ├── test-bad-a11y.html                 # browser test page with broken a11y
│   └── test_ontology.py                   # standalone ontology unit tests
├── docs/
│   ├── developer-setup.md                 # Windows dev environment guide
│   ├── ontology-guide.md                  # how to extend the ontology
│   └── architecture.md                    # detailed pipeline explanation
├── scripts/
│   ├── package-addon.sh                   # builds contextLabeler-x.x.x.nvda-addon
│   ├── vendor-deps.sh                     # vendoring script (Mac/Linux)
│   └── vendor-deps.ps1                    # vendoring script (Windows PowerShell)
└── WINDOWS_SETUP.txt                      # quick command reference for Windows
```

---

## Installation (Windows)

### Option A — Download ZIP (no git required)

1. Download the ZIP from GitHub → **Code → Download ZIP**
2. Extract and rename the folder to `nvda_reader-main`
3. Open PowerShell **as Administrator** and run:

```powershell
New-Item -ItemType SymbolicLink `
  -Path "$env:APPDATA\nvda\scratchpad\globalPlugins\contextLabeler" `
  -Target "$env:USERPROFILE\Desktop\nvda_reader-main\globalPlugins\contextLabeler"
```

4. In NVDA: **Preferences → Settings → Advanced** → check *"Enable loading of custom code from the Developer Scratchpad Directory"*
5. Press `NVDA+Ctrl+F3` to reload plugins

### Option B — Git clone (for development)

```powershell
git clone https://github.com/shubhamjakhete/nvda_reader.git
cd nvda_reader

New-Item -ItemType SymbolicLink `
  -Path "$env:APPDATA\nvda\scratchpad\globalPlugins\contextLabeler" `
  -Target "$PWD\globalPlugins\contextLabeler"
```

Then follow steps 4–5 above.

### Set your API key

1. Get a key from [console.anthropic.com](https://console.anthropic.com) → API Keys
2. In NVDA: **Preferences → Settings → Context Labeler** → paste the key

---

## Usage

| Action | Keys |
|---|---|
| Label the focused element | `NVDA+Shift+L` |
| Reload plugins after code change | `NVDA+Ctrl+F3` |
| View NVDA log (for errors) | `NVDA+F1` → View Log |

**Workflow:** Tab through any app. When NVDA says just *"button"* or *"graphic"* with no useful label, press `NVDA+Shift+L`. You'll hear something like:

- *"send message — action icon button"*
- *"mute toggle — toggle icon button"*
- *"brand logo — brand icon"*

Results are cached — pressing the hotkey again on the same element is instant.

---

## Testing

### Unit tests (Mac/Linux/Windows — no NVDA needed)

```bash
python -m unittest tests/test_ontology.py
```

Tests that the ontology loads, has the right leaf classes, validates known URIs, and rejects made-up ones.

### Integration test (Windows + NVDA)

1. Open `tests/test-bad-a11y.html` in Chrome or Edge
2. Press `Tab` to move through the unlabeled elements
3. Press `NVDA+Shift+L` on each one
4. Verify the spoken label is plausibly correct

The test page includes: unlabeled icon buttons, images with no `alt`, ambiguous buttons, and a custom `div[role="button"]` widget.

---

## Extending the Ontology

Open `globalPlugins/contextLabeler/ontology.ttl` and add a new class:

```turtle
:ShareButton a owl:Class ;
    rdfs:subClassOf :ActionIconButton ;
    rdfs:label "share button"@en ;
    rdfs:comment "Icon button that shares or exports content."@en .
```

Press `NVDA+Ctrl+F3` to reload. The new class is immediately available — Claude will start using it and it will be validated by SPARQL automatically.

See `docs/ontology-guide.md` for the full guide.

---

## Error Handling

The add-on never crashes NVDA. All errors degrade to a spoken fallback:

| Error | What NVDA speaks |
|---|---|
| No API key set | *"Context Labeler: API key not set in settings"* |
| Network timeout (8s) | *"Context Labeler: network timeout"* |
| HTTP 401 (bad key) | *"Context Labeler: invalid API key"* |
| HTTP 429 (rate limit) | *"Context Labeler: rate limited, try again"* |
| Claude returns invalid category | *"unlabeled element — could not classify"* |
| Any other exception | *"Context Labeler: error — see NVDA log"* |

---

## Acceptance Criteria (v0)

- [x] Add-on loads in NVDA scratchpad without errors
- [x] "Context Labeler" panel appears under NVDA Preferences → Settings
- [x] `NVDA+Shift+L` with no API key speaks the "API key not set" message
- [x] With a valid API key, pressing `NVDA+Shift+L` on an unlabeled button produces a correct spoken label within 2 seconds
- [x] Second press on the same element is instant (cache hit)
- [x] Hallucinated categories are rejected — fallback message spoken, no crash
- [x] `python -m unittest tests/test_ontology.py` passes 100%
- [x] `scripts/package-addon.sh` produces a valid `.nvda-addon` file

---

## Roadmap (v1+)

- Vision API — send screenshots for richer context on graphical elements
- Auto-trigger on focus — optional mode, announce unlabeled elements automatically
- Per-app ontology overrides — custom vocabulary for specific apps
- Persistent disk cache — survive NVDA restarts
- Customizable hotkey

---

## License

MIT — see `LICENSE`.

**Author:** Shubham Jakhete
