---
name: dark-family-annotation
description: >
  Use when a protein family has no Pfam hit (Pfam-dark) or only a weak/partial
  one, and you need to say what it IS. Escalation chain from cheap to
  expensive: sequence profiles → structure prediction → structure search.
  Most novel-candidate families in accessory surveys live here; "unknown"
  is a lazy verdict until this chain is exhausted.
---

# Annotating dark protein families

## Escalation chain (stop at the first confident hit)

1. **Pfam/profile re-check on MULTIPLE members** — not just the
   representative. Fragmented ORFs miss domains; a mid-length member often
   hits where the longest doesn't. Weak hits (E 1e-3..1): note the clan, do
   not trust the family label.
2. **Fold the representative** — `[database]-fold` MCP (ESMFold). pLDDT ≥70 over
   the core = usable model; <50 = likely disordered/wrong-frame, flag and
   stop. 2-3 diverse members (<90% id) if the first is ambiguous — same fold
   from diverse members is itself evidence of a real family.
3. **Structure search** — `[database]-foldseek-afdb` MCP vs AFDB/PDB. Read hits by
   (TM-score, alignment coverage, functional plausibility), not E-value
   alone: TM ≥0.5 full-length = same fold; 0.35-0.5 = possible, needs the
   active-site check below.
4. **Active-site sanity** — a fold call earns a FUNCTION call only if
   catalytic/binding residues are conserved at the aligned positions across
   your family alignment. HEPN needs R-X4-H; nucleases need their metal
   coordinators. Fold-without-residues = "X-like fold, catalytic residues
   absent" — say exactly that.
5. **Genuinely dark** — only after 1-4: report length distribution, TM
   segments (DeepTMHMM-style hydropathy at minimum), coiled-coil/disorder,
   pI, and conserved motifs from the family alignment. "Dark but 2-TM with
   conserved periplasmic Cys pair" is a real annotation; "unknown" is not.

## Precedents that justify the chain

WYL regulators and CARF/Csx1 sensors near Cas13 are invisible to Pfam in many
lineages and were recovered by exactly steps 2-3 (Foldseek rescue). Assume
sequence search under-calls regulators and sensors.

## Reporting requirement

State the terminal step reached and its best hit with metrics:
"Foldseek: TM=0.62 to PDB 7XYZ (CARF domain), R-X4-H conserved 41/41
members". Never report a fold hit without coverage + conserved-residue
status.
