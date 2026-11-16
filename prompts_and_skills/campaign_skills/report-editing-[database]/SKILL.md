---
name: report-editing-[database]
description: biology-[database] additions to the report-editing checklist (Nature-style formatting, figure standards, identifier hygiene).
---

# Report editing — biology-[database] additions

Appended to the base `report-editing` checklist; same format, same
enforcement. See that skill for E1–E9 and editor conduct.

## Checklist

- **M1** — Nature structure: Title is one declarative sentence (the
  claim, not the topic); Abstract ≤200 words, single paragraph,
  unreferenced, following the five-move logic within that budget;
  Main ≤3000 words with 2–4 result subsections each anchored on a
  display item; Methods reproducible (exact commands, versions,
  thresholds); References numbered with DOIs.
- **M2** — figure standards: ≤4 main figures, each making ONE point;
  ≥300 DPI or vector; colourblind-safe palettes; axes labelled with
  units; n and test in caption. Protein structures are PyMOL
  ray-traced cartoons (not matplotlib 3D scatters); genomic loci are
  arrow-gene diagrams with scale bars.
- **M3** — identifier hygiene: cohort labels trace to stable anchors
  (accession, [database] hash, file:row) recorded in a table; no contracted
  labels in reader-facing text; working names in backticks with
  "(working name)" at first use; no invented numbers — `~estimate`
  or TBD where unmeasured.
