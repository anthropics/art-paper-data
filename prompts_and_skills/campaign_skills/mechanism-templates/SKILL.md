---
name: mechanism-templates
description: >
  Use when writing the "mechanistic hypothesis" section of a deep-dive
  report on a candidate accessory protein — maps domain/feature evidence to
  testable mechanism classes from characterized defence-system biology.
  Turns "function unknown" into a falsifiable hypothesis with a proposed
  experiment.
---

# Mechanism hypothesis templates

Match observed features to a mechanism class; state the hypothesis AND what
evidence would falsify it. Never assert a mechanism — propose it.

| Feature evidence | Mechanism class | Precedent | First test |
|---|---|---|---|
| 1-4 TM segments, small (<200 aa), induced context | Membrane depolarization / abortive infection effector | Csx28 (VI-B) | Growth/membrane-potential assay on expression |
| HEPN motif (R-X4-H) | RNase — collateral or regulatory | Cas13 itself; Csx1 | Motif-mutant RNase assay |
| CARF/SAVED domain | Cyclic-oligonucleotide sensor gating an effector domain | Csx1/Csm6 | cOA binding + activation |
| WYL domain (+wHTH) | Ligand-responsive transcriptional regulator of the locus | WYL1 (VI-D) | EMSA on own promoter |
| TPR/HEAT repeats | Protein-protein adaptor / effector recruitment | various | Pulldown vs anchor |
| Paired small genes, one TM or one nuclease + conserved upstream partner | TA / abortive-infection module | multiple defence TAs | Co-expression rescue |
| DUF + strict co-conservation with a known accessory (e.g. rides with Csx27) | Cofactor/modulator of that accessory | Csx27/Csx28 pairing | Co-occurrence stats + co-fold ([database]-of3 / boltz2 complex) |
| Nucleotide cyclase/kinase fold | Second-messenger synthesis (CBASS-like coupling) | CD-NTase | Product detection |

## Requirements

- Tie every feature in the table's left column to the evidence that produced
  it (skill: dark-family-annotation) — hypothesis quality is capped by
  annotation quality.
- One PRIMARY hypothesis + at most one alternative; more reads as a list of
  guesses.
- End the section with "distinguishing observation": the single computable
  or wet-lab observation that separates primary from alternative (favor
  computable: co-fold with the anchor via [database]-boltz2, co-occurrence
  contingency across lineages, promoter-motif search).
