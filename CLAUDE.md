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
