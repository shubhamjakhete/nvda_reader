# Architecture

## Pipeline

When the user presses `NVDA+Shift+L`:

1. **`__init__.py`** — `script_labelFocused` is triggered. Gets the focused `NVDAObject` from NVDA's API.
2. **`context.py`** — `extract(obj)` pulls text-only metadata from the object: role, name, description, window class, app name, parent info, sibling names, window title.
3. **`cache.py`** — `make_key(ctx)` builds a stable cache key. `Cache.lookup()` returns a cached label if this element was seen before.
4. **`settings.py`** — `get_api_key()` reads the Anthropic key from NVDA's config store.
5. **`classifier.py`** — `classify(ctx, allowed_uris, api_key)` POSTs to `api.anthropic.com/v1/messages`. Returns `{"category": URI, "label": str}`.
6. **`ontology.py`** — `is_valid_leaf(uri)` runs a SPARQL ASK query against the loaded RDF graph. Rejects any URI Claude hallucinated. `label_for(uri)` fetches the human-readable `rdfs:label`.
7. **`__init__.py`** — Combines label + category into a speakable string, stores in cache, calls `ui.message()`.

## Key files

| File | Responsibility |
|---|---|
| `__init__.py` | Entry point, hotkey binding, orchestration |
| `context.py` | Pure function: NVDAObject → dict |
| `classifier.py` | HTTP POST to Claude API, returns JSON |
| `ontology.py` | RDFLib graph wrapper, SPARQL execution |
| `queries.py` | SPARQL query string constants |
| `cache.py` | In-memory LRU-ish cache |
| `settings.py` | NVDA settings panel, config read/write |
| `ontology.ttl` | The vocabulary (hand-edited Turtle) |
| `_vendor/` | Vendored RDFLib + deps |

## Why RDFLib + SPARQL

The ontology constraint is enforced at query time, not at string-match time. If Claude returns a URI that isn't a leaf node in the graph, the SPARQL ASK query returns false and the response is rejected. This means you can extend the ontology (add new leaf classes, reorganize hierarchy) without changing any Python code — the SPARQL query adapts automatically.
