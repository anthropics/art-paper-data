---
name: synteny-figure
description: >
  Use when drawing locus/neighbourhood maps for a report — the figure
  conventions that pass editorial review the first time. Figures are the #1
  editorial bounce reason; this is the recipe that avoids the bounces.
---

# Synteny figures that pass review

## Conventions (all of them, every time)

- **Anchor-centered**: anchor gene at x=0, loci aligned on it; flip loci so
  the anchor points rightward on every row (orientation-normalize).
- **Non-identical loci only**: one row per p90-distinct locus (dedup first —
  showing 15 identical clonal loci misrepresents the evidence and reviewers
  know it). State "n=… non-identical loci of … total" in the caption.
- **Row order** = anchor lineage/subtype, grouped — so lineage breadth is
  visible at a glance.
- **Color by family**, consistent across ALL figures in the report; the
  candidate family in a saturated highlight color, anchor in black/grey,
  known families in muted fixed colors, unassigned genes light grey.
  Distinct colors — never a continuous colormap for categorical families.
- **Gene arrows** show strand; intergenic distance to scale (or state
  "not to scale"); scale bar in kb.
- **Legend maps color → family id → annotation**, not just color → number.

## Caption requirements

Sentence 1: what is shown (n loci, how selected, dedup level). Sentence 2:
what the reader should see ("FAMILY sits 1-2 genes downstream of the anchor
on the same strand in 3 subtypes"). Factual title on the figure itself, not
a conclusion ("Neighbourhoods of FAMILY across VI-B loci", not "FAMILY is a
partner").

## Output

Matplotlib (or dna_features_viewer) to PNG at ≥200 dpi into the report dir;
one combined multi-panel per figure file rather than many single-panel
files. Commit the plotting script beside the PNG so the figure is
regenerable.
