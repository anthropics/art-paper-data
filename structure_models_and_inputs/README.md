# Structure models and prediction inputs

**`1_RT_monomer_models/`** `ART95/` Top-ranked AlphaFold2 model and input alignment of each of the 95 ART RTs. `GenBank8/`, `NART29/`, and `retron32/` Top-ranked AlphaFold2 model of each of the 8 GenBank, 29 NART, and 32 retron RTs. Their input alignments were not kept. Those in `msas_rebuilt/` were rebuilt by the original procedure with a new server query, and were not refolded. `MarsHill_comparison_model/` MarsHill RT model used for structural comparisons. Its input alignment was not kept.

**`2_typeI_RT_partner_cofolds/`** AlphaFold2-multimer models of two type I pairs (2 of the 18 models were kept), scores of all 18, and the six input alignments. The original alignments were not kept. These were rebuilt from the original code and sequences, with the same row counts and chain lengths, and were not refolded. `8k1kY0L4sU` is ART_57, and `CTRL_noncognate` is the shuffled control. The `deepMSA` model is the ART_57 pair folded on a deeper alignment that includes server hits, and `input_alignment_deepMSA/` holds its original input.

**`3_typeII_RT_partner_cofolds/`** AlphaFold2-multimer and Boltz-2 models of the six type II pairs (15 and 10 per pair), the input alignments of both engines, and scores of all 150 models.

**`4_typeIII_partner_model/`** Boltz-2 models of the two type III genes of loci A and C (chain A, partner; chain B, second gene) and their input alignments.

Chain A is the RT and chain B is the partner in RT-partner co-folds. [database] replaces an internal name.
