# Mission: Prokaryotic Reverse Transcriptase Census & Accessory Discovery — from scratch

You are running a from-scratch census of **reverse transcriptases (RTs) across
~1.94 billion metagenomic protein cluster representatives**, followed by a
systematic hunt for the genes that travel with them. Prokaryotic RTs are not
retroviral relics — they are the engines of at least five distinct functional
systems (group II introns, retrons, diversity-generating retroelements,
abortive-infection modules, CRISPR spacer acquisition from RNA), several of
which were only recognized as anti-phage defense in the last few years. The
gene neighborhoods of RTs are where that biology lives: retrons are useless
without their cognate effectors, DGRs without their target genes and Avd,
Abi-RTs without their partners. Most published surveys worked from reference
genomes; this dataset is 1–2 orders of magnitude deeper. The prize is the same
as any census of this kind: **new RT classes, and new effector/partner
families nobody has named yet.**

## What exists (verify everything yourself)

- **The p50 cluster representatives** (50%-identity clustering of the full
  ~16B-protein metagenomic DB), attached read-only via [storage] (see
  `[workspace]/resources/[file]`):
  - `[file]` — [size], **1,939,242,578 sequences** (verify
    by summing your per-shard counts; do not trust this number until your own
    sweep manifest reproduces it)
  - `[folder]/` — the same set pre-split into 64 gzipped shards (sweep these)
  - `[file]` — [size] member→representative map. Prefer the [database] MCP's
    `expand_clusters` over streaming this file.
- **The [database] MCP** — `protein_loci` (genomic neighborhoods ±N kb with
  orientation and features), `expand_clusters`, sequence fetch, Foldseek/
  structure tools, ColabFold/MSA. The census's synteny engine.
- **Compute dispatch** (`[harness]-compute` MCP) for GPU folding — budget is
  capped; spend it on adjudication-critical folds, not decoration.

## Inputs you must assemble yourself (task 1 territory)

No profile files are provided. Find, fetch, and verify them:

- **Pfam RT domain**: PF00078 (RVT_1) is the core; consider RVT_2 (PF07727)
  and group-II-intron maturase/X-domain profiles as auxiliaries.
- **Published RT classification resources** — candidates to evaluate (pick
  what you can actually obtain and verify; record source URL + sha256 for
  every file you stage): the Toro & Nisa-Martínez RT classification
  alignments; the Zimmerly lab group II intron database; Mestre et al. (NAR
  2020) "Systematic prediction of genes functionally associated with
  bacterial retrons" and its supplementary alignments (retron + UG groups);
  Roux et al. environmental RT survey profiles. If a source is unreachable,
  say so in the manifest and proceed with what you verified — do not
  fabricate provenance.
- **Seed RT proteins (positive controls, ≥5)** — resolve these named,
  well-characterized proteins to sequence databases yourself and verify each
  annotation before staging (`[workspace]/inputs/rt_seed_proteins.faa`):
  - **Ec86 RT** — retron-Eco1 (retron msDNA RT, *E. coli*)
  - **LtrA** — Ll.LtrB group II intron RT/maturase (*Lactococcus lactis*)
  - **BPP-1 brt** — the *Bordetella* phage DGR reverse transcriptase
  - **AbiK** — abortive-infection RT (*Lactococcus lactis*)
  - **RT-Cas1 fusion** — the *Marinomonas mediterranea* MMB-1 (or equivalent
    published) CRISPR-associated RT-Cas1
  Every seed must be recovered by your sweep panel before the sweep is
  trusted (the same logic as any positive-control roll-call).

## The sweep (stage 2)

Same recipe that works at this scale: `hmmsearch --noali --cpu 14 -Z 8
--domZ 8 -E 0.01 --domE 0.01` per shard against your panel; one manifest row
per shard with `shard, n_seqs, n_hits, domtbl_sha256`; Σ n_seqs must equal
the declared 1,939,242,578 exactly or the discrepancy must be explained.
`checks/sweep_complete.py` enforces this.

## ⚠ The scale problem — read this before designing anything

Cas13 is rare; **RTs are not**. Group II introns alone are among the most
abundant mobile elements in bacteria. Expect the raw sweep to return
**millions of hits** where a Cas13 sweep returned ~336K. Design for it:

- **Curate by architecture first** (RT core domain coverage, length windows
  per class, catalytic motif presence — the YADD/YXDD box), THEN cluster the
  survivors (e.g., MMseqs2 at ~50–70% id) and work at **cluster-representative
  level** from that point on. Set-completeness discipline applies at the
  cluster level: every REP gets a decision; members inherit it. Never
  enumerate millions of members through an LLM context.
- **The tree caps at ~2,500 leaves.** Sample representatives per cluster with
  documented stratification (rare classes exhaustive, abundant classes
  proportionally subsampled — group II introns must not drown retrons/Abi/UG
  groups). Record what was excluded and why; the placement table must still
  assign every curated rep a class+clade (profile/phylogenetic placement is
  fine for reps not in the tree — say which method placed each one).
- **The census cannot fetch loci for millions of effectors.** Per-family
  clade sampling with declared caps (e.g., up to N loci per rep-cluster,
  exhaustive for rare classes) — the caps must be in the census README and
  their effect on gate-2 independence counting must be argued, not ignored.

## The frame (stage 3)

Classify every curated RT into the known functional classes — **group II
intron, retron, DGR, Abi-type, CRISPR-associated RT, and the UG (unknown
group) lineages** — using profile placement plus a phylogeny of sampled
representatives. `checks/classes_recovered.py` gates on the five major
classes being recovered (they are all abundant enough that absence means a
pipeline bug, not biology). UG groups and anything that fits no published
class are the interesting residue: catalog them explicitly.

## The census (stage 4)

For the sampled loci: neighbors ±10 kb with orientation, gene-family
clustering (calibrate the clustering granularity against the known controls
before freezing it — Avd must neither merge into RTs nor shatter), then
adjudicate every candidate family through the three gates (clade
conservation / independence / operonic signal vs within-window permutation
null) into an 8-column `[workspace]/analyses/census_v1.tsv`:
`family, verdict, priority, clades, n_p90, n_contigs, n_lineages, reason`
(verdicts PROMOTE / PARK / KILL / CONTROL; distinct numeric priorities on
every PROMOTE; deciding criterion cited in every reason).

**Known positive controls the census must recover** (`checks/census_controls.py`
gates on the first two):
- **Avd** adjacent to DGR-class RTs (the accessory variability determinant)
- **cas1/cas2** adjacent to CRISPR-associated RTs (often fused — handle
  fusion vs adjacency explicitly)
- Retron cognate effectors (2TM proteins, ATPases, HNH nucleases, etc.) —
  diverse by design; recover at least some named retron effector families
  and verdict them CONTROL with citations
- DGR target genes (VR-containing, typically C-type lectin folds) —
  reportable control; their detection validates the DGR loci

**Known blind spots to design against**: fragmented RTs at contig edges
(don't count fragments as novel classes); RVT-adjacent false positives
(other polymerase palm domains); group II intron ORF-less fragments; and
same-biosample pseudo-replication inflating independence counts (collapse
before counting, as always).

## Deep dives (stage 5)

Seeded from `census_v1.tsv` PROMOTE rows in priority order. Each deep dive
follows the survey doctrine: full evidence dossier (occurrence table,
alignment, fold if adjudication-critical, synteny figure, selection
signal where informative), the four-gate report template, an explicit
kill-test (what observation would refute the association?), and a
`family:` front-matter key naming the census family so the roll-call can
account for it. Refutations are first-class outcomes: a promoted family
demoted with evidence counts exactly as much as a confirmation.

## Contracts — author them yourself at seed time

You (the launch agent) must author the contract chain before creating tasks,
following the survey doctrine pattern: **inputs → rt-set → frame → census →
deep-dives**, chained with `requires`, the stage-gating ones exclusive, with
these check scripts wired as deliverables where they exist:
`checks/inputs_staged.py`, `checks/sweep_complete.py`,
`checks/classes_recovered.py`, `checks/census_controls.py`,
`checks/promoted_coverage.py` — plus the file deliverables named above
(`rt_set_v1.tsv`, tree + placements, `census_v1.tsv`). Give deep-dives a
`seed_from` on the census PROMOTE rows with a brief_template that carries
family, clades, evidence triplet, and reason, and attach the
`metagenomic-surveys` skill package. **Set `recommended_skills:
["metagenomic-surveys"]` on the inline tasks you create too**, not only in
seed_from — census and adjudication tasks need the syllabus as much as deep
dives.

## Methods discipline

The `metagenomic-surveys` skill package (seven skills) is the operating
doctrine for this survey: identity roll-calls over counts, rep-level vs
member-level counting per `clonality-vs-independence`, gate arguments with
numbers per `operonic-gate-scoring`, `family-adjudication-rubric` verdicts,
`novelty-kill-test` before any "novel" claim, `dark-family-annotation` for
Pfam-dark candidates, mechanism templates with pre-registered distinguishing
observations. Load them; cite them when they decide something.

File hygiene: raw domtbls and fetched archives gzipped under gitignored
`[workspace]/resources/cache/`; only distilled tables committed; every committed
artifact regenerable by a committed script.
