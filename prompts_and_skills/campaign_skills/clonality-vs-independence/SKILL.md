---
name: clonality-vs-independence
description: >
  Use BEFORE claiming any protein family is "recurrent", "conserved", or
  "co-occurring" with an anchor gene. Raw occurrence counts lie: one phage
  bloom or clonal expansion can put hundreds of identical copies in the data.
  This skill is the dedup-then-count discipline that separates real
  evolutionary associations from clonal noise.
---

# Clonality vs independence

The single most common false-positive mode in neighbourhood surveys: a family
looks "recurrent" (high n_occ) but every member is the same sequence from one
clonal expansion. Association evidence only counts INDEPENDENT occurrences.

## The bar (do not relax it)

A family counts as recurrent only if ALL THREE hold:
1. **≥3 non-identical members** after collapsing at 90% identity (p90
   clusters, not raw sequences — two members >90% identical are ONE
   observation).
2. **On ≥3 distinct contigs** (same contig = same locus = one observation,
   whatever the copy number).
3. **Across ≥2 independent anchor lineages** (different effector subtypes, or
   anchors <90% identical to each other). A family that only ever rides one
   effector clone is hitchhiking, not partnering.

## Procedure (against a loci table with p90/p50/p20 columns)

```python
import pandas as pd
loci = pd.read_parquet("[workspace]/inputs/loci_*.parquet")
fam = loci[loci.p20_family == FAMILY_ID]
n_p90      = fam.p90_family.nunique()      # non-identical members
n_contigs  = fam.contig.nunique()
n_lineages = fam.effector_subtype.nunique()  # or cluster anchors at 90% id
print(n_p90, n_contigs, n_lineages)  # 3 / 3 / 2 minimum
```

If you lack precomputed p90 columns: cluster member sequences yourself
(`mmseqs easy-cluster --min-seq-id 0.9` or greedy CD-HIT-style in python)
BEFORE counting. Never count raw rows.

## Reporting requirement

Every recurrence claim in a report must state the triplet explicitly:
"recurrent (n_nonident_p90=7, contigs=6, effector_lineages=3)". A claim
without the triplet is unreviewable and the supervisor will bounce it.

## Known trap

Metagenomic assemblies duplicate loci across samples of the same site.
If members trace to one biosample/site, treat as ONE observation regardless
of contig count — check sample metadata when counts hover near the bar.
