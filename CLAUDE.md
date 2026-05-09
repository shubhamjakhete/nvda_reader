# Instructions for Claude Code

This repo will become an **NVDA add-on** called `contextLabeler` that uses an ontology + Claude Haiku to fill in missing accessibility labels for unlabeled UI elements.

## Source of truth

**`DESIGN.md` is the complete build spec.** Read it in full before writing any code. It contains:
- Goals and non-goals (v0 scope is locked — do not exceed it)
- Final tech stack (Python + RDFLib + RDF/Turtle + SPARQL + Claude Haiku — no substitutions)
- Full repo structure to create
- Component specifications with code skeletons
- The complete ontology Turtle file
- Claude API contract (endpoint, headers, prompt templates)
- Vendoring procedure for RDFLib
- An 8-phase build plan with verification steps for each phase
- Acceptance criteria the v0 build must pass

## How to work

1. **Read `DESIGN.md` end to end before starting.** Do not skim.
2. **Follow the 8 phases in order.** Each phase has a verification step. Stop after completing each phase, run the verification, and report the result before starting the next phase.
3. **Do not deviate from the tech stack.** No swapping RDFLib for `pyld`, no swapping `urllib` for `requests`, no swapping Turtle for JSON. The stack choices are deliberate (see DESIGN.md "Tech Stack" section for rationale).
4. **Use the exact code skeletons in DESIGN.md as the starting point** for each component. They are not pseudocode — they are intended to be copy-paste-and-fill.
5. **Do not implement anything in the "Non-goals" list.** Screenshots, auto-trigger on focus, persistent disk cache, etc. are deferred to v1.
6. **Vendor RDFLib using the script described in DESIGN.md "Vendoring Procedure".** Commit the vendored files. Do not assume `pip` is available at runtime.

## Constraints to keep in mind

- **NVDA is Windows-only.** Phases 1, 3 (ontology unit tests), and 8 (packaging) can run on any OS. Phases 2 and 4-7 require a Windows machine with NVDA installed. The user has a Windows laptop ready.
- **No build step at runtime.** NVDA loads Python files directly from the scratchpad or `.nvda-addon` zip. There is no compilation, no transpilation, no bundler.
- **No third-party libraries beyond RDFLib + its deps.** Anything else, use the Python stdlib.
- **Add-on bundle target size: under 5 MB.** RDFLib + deps come to ~2 MB; leave headroom.

## Development Workflow (Mac → Windows)

The user is developing on a Mac and will move the repo to a Windows laptop only when NVDA-runtime testing is required. Follow this split:

### Phases that run on Mac (~70% of the work)

| Phase | What | Mac-doable? |
|---|---|---|
| 1 — Skeleton | Create files, manifest, `__init__.py` stub | Yes |
| 3 — Vendor RDFLib + ontology | `pip install --target`, write `ontology.ttl`, run `test_ontology.py` | Yes (pure Python, no NVDA) |
| 4 — Settings panel | Write the code (won't *run* on Mac without NVDA, but writes fine) | Code only |
| 6 — Classifier | Write the Claude API code; can even test the HTTP call standalone | Code + isolated API test |
| 8 — Packaging script + docs | Write `package-addon.sh`, README, dev-setup guide | Yes |

### Phases that require Windows + NVDA

| Phase | Why Windows-only |
|---|---|
| 2 — Hello-world hotkey verification | Needs NVDA running to confirm the hotkey actually fires |
| 5 — Context extraction verification | Needs real `NVDAObject` instances from focused elements |
| 7 — Cache + error handling end-to-end testing | Real-world testing on Discord/the HTML test page |
| 8 — Final verification | Installing the `.nvda-addon` via NVDA's GUI |

### Three gotchas to enforce while building on Mac

1. **NVDA-only imports won't run on Mac.** Modules like `globalPluginHandler`, `api`, `ui`, `gui`, `config`, `wx` are part of NVDA's bundled Python — they don't exist on a Mac. Do **not** try to `python __init__.py` directly to "test" the plugin. Code that references those modules is correct and expected; it just can't execute outside NVDA.

2. **The only Mac-runnable test is `tests/test_ontology.py`.** It exercises the RDFLib + SPARQL layer in isolation (no NVDA imports). After Phase 3, run `python -m unittest tests/test_ontology.py` to verify before continuing. Do not attempt to write tests that import `globalPluginHandler` or other NVDA modules.

3. **Optional: smoke-test the Claude API on Mac before Phase 6** with a throwaway script that hits `api.anthropic.com` directly. If it returns a response with the user's key, Phase 6 will work first try on Windows.

### Code transfer between Mac and Windows

Use git, not zip files. The user will:
1. Build through Phase 4 on Mac
2. `git push` to https://github.com/shubhamjakhete/nvda_reader
3. `git pull` on the Windows laptop
4. Run Phases 2, 5, 6, 7, 8 verification on Windows
5. If fixes are needed, the user may make them on either machine and sync via git

Do not write code that uses absolute Mac-specific paths (`/Users/...`) or assumes a particular OS at runtime. Use `os.path.dirname(__file__)` and similar relative path patterns throughout.

## When you finish a phase

Report:
- What you built
- Which verification step you ran
- Whether it passed
- What's next

If a verification step fails, **stop and surface the failure**. Do not proceed to the next phase with a broken foundation.

## When all 8 phases are done

Run through the **Acceptance Criteria checklist** in DESIGN.md and confirm every item passes. Then create a `v0.1.0` git tag and a `.nvda-addon` package.

## Things you'll need from the user

The user (Shubham) has these ready to provide when you ask:
- Anthropic API key (only needed at Phase 6)
- A Windows laptop with NVDA installed (needed Phase 2 onward)
- The model ID `claude-haiku-4-5-20251001` — verify it's still current at build time

## Voice

Match the project's tone: practical, direct, evidence-grounded. The user is a builder doing a learning prototype with serious technical ambition (chose RDFLib + SPARQL over JSON for credibility). They want a working artifact, not boilerplate.
