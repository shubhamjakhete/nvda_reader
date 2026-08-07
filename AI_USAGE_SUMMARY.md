# AI Usage Summary — ContextLabeler (nvda_reader)

**Author:** Shubham Jakhete  
**Repository:** `github.com/shubhamjakhete/nvda_reader`  
**Document date:** 2026-08-05  
**Purpose:** Factual record of how AI was used in this project, for disclosure and interview review.

**Evidence basis:** Git history (all commits authored by Shubham Jakhete; many tagged `Co-Authored-By`), recoverable `DESIGN.md` / `CLAUDE.md` from early commits, project docs under `docs/`, and Cursor agent transcripts available locally. Items that cannot be verified from those sources are marked **[unverified]**.

---

## 1. Project overview

ContextLabeler is an NVDA screen-reader add-on that labels unlabeled UI controls. It extracts text metadata from the focused element, asks **Claude Haiku** for a category + short label, validates the category against a local **RDF/Turtle ontology** (RDFLib + SPARQL), and speaks a result.

Later work on branch `feature/grounding-and-determinism` added:

- Tiered verification speech (ontology-confirmed category spoken first; LLM label hedged)
- Persistent deterministic label store + stable fingerprinting
- Offline evaluation (benchmark, ablation, consistency)

**Product AI (runtime):** Anthropic Claude (`claude-haiku-4-5-20251001`) via HTTPS in `globalPlugins/contextLabeler/classifier.py`.  
**Development AI (build):** Claude Code / Claude Sonnet (majority of commits) and Cursor (documented for demo page + VS Code ontology work).

---

## 2. How AI was used

| Phase | How AI was used | Evidence |
|---|---|---|
| **Requirements / planning** | Initial design captured in `DESIGN.md` (status APPROVED; generated via `/office-hours` process on 2026-05-08). Locked goals, non-goals, stack, and 8-phase build plan. `CLAUDE.md` instructed an implementing agent to follow that spec without stack substitutions. | Commit `43c9078`; recoverable blob `git show 43c9078:DESIGN.md` |
| **Architecture** | Spec chose Python + vendored RDFLib + Turtle + SPARQL + Claude Haiku + stdlib `urllib`/`json`. Directory layout matches NVDA `globalPlugins/` packaging. | `DESIGN.md` Tech Stack; `docs/architecture.md` |
| **Implementation (v0)** | Agent implemented phases from `DESIGN.md` skeletons (plugin modules, ontology, vendoring, tests). | `05b0816` — “Phases 1 + 3 complete… Co-Authored-By: Claude Sonnet 4.6” |
| **Debugging** | AI-assisted fixes for NVDA’s stripped Python (`xml.dom.minidom` stub), short-form URI expansion, prompt rules for text vs icon buttons, IA2 HTML class extraction, cache collisions. | Commits `697fb5d`, `b7b90d7`, `5e07e35`, `d972316`, `d2969e9`, `876910c` (all Co-Authored-By Claude) |
| **Feature 1 / 3 + eval** | Implementation aligned with `docs/implementation_plan.md`; commits credit Claude Sonnet 4.6. | `4584d2b`, `3158504`, `8d4796f`, `750f517`, `2fb2e77` |
| **Demo / accessibility fixtures** | Cursor agent built `tests/test2-demo.html` and VS Code supplement ontology from detailed user specs. | Commit `8b5fb51` — `Co-authored-by: Cursor`; Cursor transcript `1d98eb07-…` |
| **Testing** | Unit tests and eval harness code co-authored with Claude; benchmark/ablation/consistency runs produce measured results. | `tests/test_*.py`; `eval/`; `docs/feature-grounding-and-determinism.md` |
| **Final review / docs** | Feature write-up and public README polish co-authored with Claude; `DESIGN.md`/`CLAUDE.md` removed from public tree. | `2fb2e77`, `7cfa0a4` |
| **Interview prep (not product code)** | Cursor used to draft Q&A on trade-offs, AI failures, prompts, directory structure. | Cursor transcript `2ee748f6-…` (2026-08-04+) |

**Two distinct “AI” roles (do not conflate):**

1. **Classifier model in the add-on** — user-facing labeling.  
2. **Coding agents** — helped write/debug/document the add-on under human-authored specs and commits.

---

## 3. Development timeline

| Date (commit author date) | Milestone | Commit(s) | AI tool noted in Git |
|---|---|---|---|
| 2026-05-08 | Seed design + agent instructions | `43c9078` | Spec for Claude Code |
| 2026-05-08 | Initial add-on v0.1.0 build | `05b0816` | Claude Sonnet 4.6 |
| 2026-05-09 | Setup docs; RDFLib/NVDA Python fixes; ontology descriptions in prompt | `57846e8` … `6f68acf` | Claude Sonnet 4.6 |
| 2026-05-10 | Public polish; URI/prompt/context/cache fixes | `7cfa0a4` … `876910c` | Claude Sonnet 4.6 |
| 2026-06-18–19 | Demo HTML + VS Code ontology supplement | `8b5fb51` | Cursor |
| 2026-07-05 | Feature 1 (grounding), Feature 3 (store), eval suite + results + write-up | `4584d2b` … `2fb2e77` on `feature/grounding-and-determinism` | Claude Sonnet 4.6 |

Branch policy for Features 1/3: work isolated on `feature/grounding-and-determinism` (see `docs/implementation_plan.md`).

---

## 4. Key technical decisions and trade-offs

These decisions appear in design docs and/or shipped code. Attribution of “human vs AI first proposal” is **[partially unverified]** for Feature 1/3 except where Git/docs state a choice and rationale.

| Decision | Choice | Trade-off / rationale | Evidence |
|---|---|---|---|
| Ontology representation | RDF/Turtle + SPARQL via RDFLib (not JSON enum) | Credibility + extend without rewriting validation code; larger vendored footprint | `DESIGN.md`; `docs/architecture.md` |
| Runtime model | Claude Haiku | Latency/cost for interactive a11y vs larger models | `classifier.py` `MODEL` |
| v0 input modality | Text metadata only | No vision cost/privacy; weaker on images | `DESIGN.md` non-goals |
| v0 cache | In-memory only | Simpler; lost on restart | `DESIGN.md` non-goal: persistent disk cache |
| Later: determinism | Persistent JSON store + fingerprint (Feature 3) | **Scope change:** persistent cache was deferred in v0, then intentionally added | `3158504`; `store.py`; `cache.fingerprint()` |
| Fingerprint inputs | Prefer `automation_id`; exclude `window_title` / `window_text` | Stability vs risk of collisions without AutomationId | `docs/feature-grounding-and-determinism.md`; `cache.py` |
| Invalid LLM category | Ancestor walk + speech tiers (not hard bail) | Partial usefulness vs silence | `4584d2b`; `speech.py` |
| Ancestor walk implementation | Python BFS in production; SPARQL depth query retained | Testability / RDFLib aggregation risk | Feature write-up §1.1 |
| Label store format | JSON file (atomic write) | Simpler than SQLite for plugin + inspectable | `store.py`; implementation plan |
| Eval trade-off measured | Constrained ontology vs free-form categories | Shows ontology contribution quantitatively | `eval/ablation.py`; results in feature write-up |
| Explicitly deferred | Vision, rules-first UIA mapping, community store, scan mode, earcons | Scope control for UIST demo branch | `docs/implementation_plan.md` §7 |

**Responsible-AI product decision:** treat Claude as a *guesser*; ontology + store as *constraints*. Ablation: free-form invalid category rate **83.6%** vs constrained **0.0%** (documented in `docs/feature-grounding-and-determinism.md`).

---

## 5. Examples of accepting, modifying, and rejecting AI suggestions

### Accepted (with evidence)

- Follow `DESIGN.md` stack and skeletons for v0 implementation → `05b0816`.
- Include leaf `rdfs:label`/`rdfs:comment` in the classifier prompt → `6f68acf`.
- Prompt rules: non-empty Name → CommandButton; icon categories only when Name empty → `d972316`.
- Stub `xml.dom.minidom` for NVDA’s stripped Python so RDFLib loads → `b7b90d7` / `697fb5d`.
- Expand `:ShortForm` category URIs before SPARQL validation → `5e07e35`.
- Cursor implementation of detailed demo HTML + `vscode.ttl` supplement under strict “additive only” file constraints → `8b5fb51`.
- Feature 1/3 modules and eval harness as committed with Claude co-author tags → `4584d2b`, `3158504`, `8d4796f`.

### Modified (human constraints on AI output)

- **VS Code ontology:** User required reading real `ontology.ttl` classes; fallback from nonexistent `:NavigationButton` to `:Link` for tree/breadcrumb classes (stated in user prompt; reflected in commit). Path: `globalPlugins/contextLabeler/vscode.ttl`.
- **Ancestor resolution:** Plan allowed SPARQL `ANCESTORS_BY_DEPTH` *or* Python walk; shipped primary path is BFS (`ontology.nearest_valid_ancestor`), SPARQL query kept in `queries.py`.
- **Store hit behavior:** Recompose via `speech.compose()` from stored fields rather than caching the raw spoken string (documented rationale: ontology labels can change).
- **Public repo hygiene:** Agent-oriented `CLAUDE.md` / `DESIGN.md` gitignored and removed from tracked tree → `7cfa0a4` (specs remain recoverable from Git history).

### Rejected or kept out of scope (documented)

- Screenshots / vision API (v0 and Feature branch out-of-scope).
- Auto-label on every focus (hotkey-only in v0 design).
- Swapping RDFLib / Turtle / `urllib` for alternatives (`CLAUDE.md`: “Do not deviate from the tech stack”).
- Using prompt length / temperature as the primary determinism fix — system uses persistent store instead (`docs/feature-grounding-and-determinism.md` Test 3 narrative).
- Free-form categories in production — `freeform=True` exists for **eval Condition B only** (`classifier.py`, `eval/ablation.py`).

**[unverified]** Exact chat turns where an agent proposed vision, SQLite, or earcons and were verbally rejected are not in the two Cursor transcripts retained for this workspace. Rejection is evidenced by out-of-scope docs and what shipped.

---

## 6. Testing and validation

### Automated unit tests

- Command: `python3 -m unittest discover tests`
- **39 tests** documented in feature write-up; re-run for this document: **39 OK** (2026-08-05).
- Coverage includes ontology leaves/ancestors, speech tiers, fingerprint stability, store atomicity/eviction/pin, determinism across simulated restarts (`tests/test_determinism.py`).

### Offline evaluation (API-backed)

| Suite | Role | Paths |
|---|---|---|
| Replay | Category/label accuracy, latency | `eval/replay.py`, `eval/benchmark.json` (55 entries) |
| Ablation | Constrained vs free-form | `eval/ablation.py`, `eval/ablation_*.json` |
| Consistency | 10× LLM variance | `eval/consistency.py`, `eval/consistency_results.json` |

Headline numbers (from `docs/feature-grounding-and-determinism.md`, not re-run for this summary): constrained replay cat acc **90.9%**, invalid **0%**; ablation invalid **0%** vs **83.6%**; consistency avg category agreement **98.4%**, ~**1.6** distinct labels/entry.

### Manual / integration checks (as documented in commits)

- Claude API smoke test noted in `05b0816` message.
- Windows/NVDA verification called out as pending in early build commit; later fixes target real NVDA Python/IA2 behavior (`b7b90d7`, `d2969e9`).
- Demo page designed for live academic demos of unlabeled controls (`tests/test2-demo.html`).

### Code review posture

- Spec-first: agent instructed to stop on failed phase verification (`CLAUDE.md`).
- Human commits under personal Git identity; co-author trailers disclose AI assistance.
- Feature branch isolation before merge to `main`.

---

## 7. Accessibility considerations

- **Problem addressed:** unlabeled / icon-only UI announced poorly by screen readers.
- **Interaction model:** explicit gesture (`NVDA+Shift+L`); optional pin (`K`) and relabel (`R`) — avoids silent ambient re-labeling.
- **Speech design:** verified category first; hedge LLM label (`likely` / `unverified guess` / `possibly`) in `speech.py` — epistemic honesty for blind users.
- **Graceful degradation:** invalid/unknown categories → fallback speech, not NVDA crash.
- **Demo fixtures:** deliberately **inaccessible** HTML (missing names/alts) to demonstrate the add-on’s purpose; mixed with correctly labeled controls as controls (`tests/test2-demo.html` user spec).
- **Privacy:** text metadata sent to Anthropic API; no screenshots in shipped scope.
- **Limits acknowledged in write-up:** weaker on images without vision; Win32 sparse context; label wording variance.

---

## 8. Limitations and AI-use disclosure

### Development disclosure

- A large fraction of commits include `Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>`.
- At least one commit includes `Co-authored-by: Cursor <cursoragent@cursor.com>` (`8b5fb51`).
- Early build was explicitly set up for a **Claude Code** agent driven by `DESIGN.md` / `CLAUDE.md` (`43c9078`).
- Human author of all commits: **Shubham Jakhete**. Human responsibilities included approving the design, locking non-goals, providing API key / Windows NVDA environment, writing detailed Cursor prompts for demo/VS Code work, and owning acceptance of Feature 1/3/eval results.

### What this document does *not* claim

- It does **not** claim every line was hand-typed without AI.
- It does **not** claim Cursor transcripts cover the full Feature 1/3 implementation (they do not; those commits cite Claude).
- It does **not** re-verify API eval numbers in this writing session.
- Authorship of every sentence in `docs/implementation_plan.md` (currently untracked in working tree) is **[unverified]** beyond presence in the workspace and alignment with commits.

### Product-model limitations

- LLM labels remain free-text guesses; only categories are ontology-checked.
- Determinism depends on fingerprint quality and store; wrong first labels persist until relabel.
- Prompt alone is insufficient (fence-stripping in `classifier.py`; ablation evidence).

---

## 9. References to chat logs and Git commits

### Cursor agent transcripts (local)

| ID | Topic (from user queries) | Path |
|---|---|---|
| `1d98eb07-e4ae-4ab6-b578-163c3ef86e8e` | `test2-demo.html` spec; VS Code supplement ontology; push to GitHub | `~/.cursor/projects/…/agent-transcripts/1d98eb07-…/` |
| `2ee748f6-1311-4a02-b4d1-796a3df1307e` | Interview prep: trade-offs, AI failures, prompting, directory structure; this summary request | `~/.cursor/projects/…/agent-transcripts/2ee748f6-…/` |

**Important prompts preserved in those logs (paraphrased titles):**

1. Long, constraint-heavy demo HTML accessibility fixture specification (2026-06-18).  
2. Additive-only VS Code ontology supplement with file-touch limits and “read ontology.ttl first” (2026-06-19).  
3. Interview / AI-usage / trade-off Q&A requests (2026-08-04–05).  
4. This document request: factual `AI_USAGE_SUMMARY.md` from chat + Git history (2026-08-05).

Claude Code session transcripts for May–July implementation are **not** present in the Cursor transcripts folder above → **[unavailable in this workspace]**. Git co-author trailers and recoverable `DESIGN.md`/`CLAUDE.md` are the primary evidence for that period.

### Key Git commits (evidence anchors)

```
43c9078  Initial design spec and Claude Code instructions
05b0816  Initial build: contextLabeler NVDA add-on v0.1.0
6f68acf  Improve classification accuracy by including ontology descriptions in prompt
b7b90d7  Fix xml.dom.minidom missing on NVDA's stripped Python
5e07e35  Fix URI mismatch: expand short-form category URIs before validation
d972316  Fix misclassification of text buttons as icon buttons
7cfa0a4  Polish repo for public presentation (gitignore DESIGN.md/CLAUDE.md)
8b5fb51  Add VS Code supplement ontology and contextLabeler demo page  (Cursor)
4584d2b  feat: Feature 1 — ontology grounding with tiered verification speech
3158504  feat: Feature 3 — deterministic labeling via persistent store and fingerprinting
8d4796f  feat: evaluation suite — benchmark, replay harness, ablation, consistency
750f517  eval: add full benchmark run results
2fb2e77  docs: add comprehensive write-up for Feature 1, Feature 3, and eval suite
```

### Key file paths

| Path | Role |
|---|---|
| `globalPlugins/contextLabeler/classifier.py` | Runtime Claude API + prompts |
| `globalPlugins/contextLabeler/ontology.ttl` | Hand-edited vocabulary |
| `globalPlugins/contextLabeler/speech.py` | Verification tiers |
| `globalPlugins/contextLabeler/store.py` | Persistent labels |
| `globalPlugins/contextLabeler/vscode.ttl` | App-specific supplement |
| `docs/implementation_plan.md` | Feature 1/3/eval plan |
| `docs/feature-grounding-and-determinism.md` | Results + learnings |
| `eval/` | Ablation / consistency evidence |
| `tests/` | Unit tests + demo HTML |
| `git show 43c9078:DESIGN.md` | Original approved design (not in working tree) |
| `git show 43c9078:CLAUDE.md` | Original agent instructions |

---

*End of summary. Update this file if additional chat exports (e.g. Claude Code) are archived alongside the repo.*
