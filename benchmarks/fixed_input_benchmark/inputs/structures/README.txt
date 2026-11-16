level4_structures bundle
========================
- locus GenBank files: identical to level 3 (ORFs + Pfam domains), plus a
  structure_id qualifier on every CDS.
- structures/: one mmCIF per unique protein sequence, named <structure_id>.cif.
  Identical sequences share one structure file (deduplicated across loci).
- structures/confidence_summary.json: per-protein length, mean pLDDT (0-1),
  pTM, and fold wall-time. Predictions are ESMFold2-Fast, single-sequence,
  1 diffusion sample, seed 0. Interpret pLDDT < 0.5 regions as unreliable.
- locus_097 (22 ORFs; 21 new structures) was added 2026-09-17 with the same
  settings (ESMFold2-Fast, 10 loops, 68 steps, 1 sample, seed 0).
- 2 of 1113 proteins have no structure (GPU memory limit at 2492/2551 aa);
  their CDS entries say so explicitly.
