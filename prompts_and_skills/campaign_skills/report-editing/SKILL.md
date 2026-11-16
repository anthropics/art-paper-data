---
name: report-editing
description: The editorial checklist every report is graded against before merge. Workers pre-flight against it; the editor walks it item-by-item via the [harness]-editorial tools.
---

# Report editing — the checklist

This is the single source of truth for what "publishable" means in
this harness. The editor role checks these items one at a time (the
`[harness]-editorial` MCP serves them in order and refuses sign-off until
every applicable item is recorded). Workers: **pre-flight your report
against this list before declaring done** — a report that arrives
clean merges in one editorial pass.

Item IDs are stable; presets may append their own items in a
`report-editing-*` skill of the same format.

## Checklist

- **E1** — `prospectus.md` present, ≤1 page, with Topic / Headline /
  Why it matters / Status. The feed card is built from it.
- **E2** — `EVIDENCE.md` rows cover every substantive claim in the
  body, each with a pass/fail state and a pointer to the supporting
  artifact. No body claim without a row; no row contradicted by the
  body.
- **E3** — evidence trail present: a keyed table at the END of the
  canonical deliverable (after References / Extended Data), one row
  per substantive claim → task id(s), artifact path(s),
  identifier(s)/hash(es), and the exact quantities behind any number
  stated approximately in prose.
- **E4** — register: no task tags, file paths, internal column or
  variable names, or database hashes inline in body prose. Things are
  called by their scientific name; machine addresses live in the
  evidence trail.
- **E5** — identifier conservation: every identifier that left the
  prose in this revision reappears in the evidence trail or
  `EVIDENCE.md`, OR its claim was deliberately cut. The harness
  supplies the disappeared-identifier list as evidence — confirm each
  is a deliberate cut, not a loss.
- **E6** — claim calibration: each substantive claim is identifiable
  in the prose as shown / inferred / speculated, the label matches
  the cited evidence, and no claim is stronger than in the previous
  revision without new evidence. A speculation in the voice of a
  result fails this item.
- **E7** — decisive caveat: the one caveat that most changes how a
  reader weighs the headline claim appears beside that claim AND in
  the abstract — not only in Limitations.
- **E8** — abstract structure: five moves in order — question/why,
  shown, inferred/proposed, decisive caveat, next experiment with the
  result that would kill the hypothesis. A reader stopping after
  moves 2 and 4 is not misled. No field-background openings, no
  pipeline narration.
- **E9** — figure fidelity: every non-schematic figure has a
  co-located `gen_*.py` that regenerates it from data in this
  directory or `[workspace]/` (no orphans); schematics are named
  `schematic_*` and captioned as illustrations; DATA-class figures
  were never touched by generative AI.

- **E10** — cited-source spot-check: pick up to 3 load-bearing
  external citations with DOIs. For each: if a fetched copy exists
  under `[workspace]/resources/articles/` (or `article_fetch` retrieves
  one in ≤1 attempt), open the relevant section and verify the claim
  attributed to it; a contradiction is a FAIL on this item. If no
  open-access copy exists, the claim must be marked abstract-only or
  hedged accordingly — an unhedged body-content claim from an
  unreadable paper is a FAIL; a properly hedged one passes with a
  note. Do not fetch more than 3 papers; do not read whole PDFs —
  target the cited section.

## Editor conduct

- Fix prose yourself when the fix is editorial (wording, structure,
  relocation of identifiers, calibration language): edit
  `main.<suffix>`, `prospectus.md`, `EVIDENCE.md` directly. You may
  not touch data, figures, or `gen_*.py` — a defect there is a
  BOUNCE back to the worker, not your edit.
- Never invent or alter a number, identifier, or claim grade upward.
  You may downgrade a claim's language to match its evidence; state
  why in the item note.
- Notes are for the worker and supervisor: terse, specific,
  actionable.
