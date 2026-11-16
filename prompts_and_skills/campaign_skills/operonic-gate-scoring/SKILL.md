---
name: operonic-gate-scoring
description: >
  Use when arguing a family IS or IS NOT operonically coupled to an anchor
  gene — including when you disagree with precomputed gate scores. Computes
  rank/strand/gap enrichment vs a background, and documents the gates' known
  blind spot (strand-saturated windows) so rescues are argued quantitatively.
---

# Operonic gate scoring

Four signals, computed per family over all loci carrying it, each vs the
window background (all genes in ±10 kb of the anchor):

- **rank_enrich** — is the family closer in gene-rank to the anchor than
  background? (median |rank|, permutation p or z vs shuffled ranks)
- **strand_enrich** — fraction of members on the anchor's strand vs the
  window's strand composition.
- **med_gap** — median intergenic gap to the adjacent gene toward the
  anchor; operonic couples sit <100 bp typically, co-resident cargo drifts.
- **z_rank** — z-score of the family's mean rank vs the empirical rank
  distribution of ALL families in the same windows.

```python
import pandas as pd
loci = pd.read_parquet("[workspace]/inputs/loci_*.parquet")
win  = loci  # all window genes = background
fam  = loci[loci.p20_family == FAMILY_ID]
bg_rank = win["rank"].abs()
print("median |rank| fam vs bg:", fam["rank"].abs().median(), bg_rank.median())
print("strand match:", fam.strand_match.mean(), win.strand_match.mean())
print("median gap:", fam.gap.median())
```

## The known blind spot — argue rescues here

strand_enrich carries no information in **strand-saturated windows** (whole
neighbourhood co-oriented, common in defence islands): the gate under-calls
real partners there. When rescuing a gate-failed family, show (a) the window
strand composition demonstrating saturation, (b) rank + gap still passing.
A rescue argued without (a) is hand-waving.

## Reporting requirement

Verdicts that contradict a precomputed gate must show the recomputed
numbers side by side with the gate's, and name which signal you discount
and why. "The gate is wrong" without numbers gets bounced.
