---
name: [database]-metagenomic-database-search-retrieval
description: Search [size] metagenomic proteins (fast minhash + sensitive DIAMOND), retrieve loci/contigs/samples — when UniProt/NCBI coverage isn't enough
---

# [database] — metagenomic database search & retrieval

`[database]` is a metagenomic database indexed for **fast protein search** over
**[size] proteins** assembled from public metagenomes ([sources]),
plus the contigs and samples they came from. It is auto-connected as
an MCP server in this session — tools appear as `mcp__[database]__*`.

## When to reach for [database] instead of UniProt/NCBI

- You need homologs/variants **beyond** what's in curated databases
  (environmental, uncultured, novel taxa).
- You want **genomic context** for a protein: operon neighbors, flanking DNA,
  which contigs/samples carry it.
- You want **environmental distribution**: which biomes/hosts/studies a
  protein family appears in.
- You want a fast (~100ms) family-level scan before committing to a slow
  BLAST against nr.

UniProt/NCBI remain better for: curated annotations, structures, literature
links, reviewed reference sequences.

## Which MCP server is which

| you want | server | tool | notes |
|---|---|---|---|
| sequence search ([size] proteins) | `[database]` | `search_fast`, `seq_search`, `search_sensitive` | minhash + DIAMOND |
| genomic context | `[database]` | `locus_get`, `contig_get`, `sample_get` | operon neighbors, source biome |
| **ESMFold** | `[database]-fold` | `fold(sequences: list[str])` | seconds; also `fold_chunked`, `esm2_embed` |
| **OpenFold-3** (AF3 arch) | `[database]-of3` | `of3_fold`, `of3_fold_complex` | minutes; MSA via ColabFold |
| **Boltz-2** (affinity) | `[database]-boltz2` | `boltz2_fold_complex(chains)` | protein+ligand+nucleic |
| **Foldseek** vs AFDB | `[database]-foldseek-afdb` | `foldseek_search` | structural homologs by TM-score |

The structure servers are GPU-backed and may take 30–60 s to
register their tools at session start; call `*_status` first if
the fold tool isn't listed yet.

## Tools — `[database]` search server

| tool | purpose | key params | returns |
|---|---|---|---|
| `mcp__[database]__search_fast` | Minhash family search vs [size] ref proteins (~100–250ms; batched) | `sequences[]`, `top_n`, `min_matches`, `as_url` | `[[{n_matches, protein_id, p90..p20, name, organism, tax_id}]…]` per input |
| `mcp__[database]__search_sensitive` | Minhash → p20-expand → DIAMOND blastp (~10–30s/query) | `sequences[]`, `top_n`, `min_identity`, `as_url` | `[[{protein_id, pident, evalue, bitscore, …}]…]` |
| `mcp__[database]__protein_hash` | Compute [database] hash ID for a sequence (no DB hit) | `sequence` | `{hash, length, row_key}` |
| `mcp__[database]__protein_get` | Look up one protein in [table] | `sequence` \| `hash`+`length` | `{hash, length, sequence, annotations}` |
| `mcp__[database]__protein_loci` | All CDS loci where this protein occurs | `sequence` \| `hash`, `source?`, `limit`, `include_dna`, `flank` | `[{source, contig_hash, contig_length, start, end, strand, dna?}]` |
| `mcp__[database]__contig_samples` | Which samples contain this contig | `contig_hash`, `contig_length`, `source?` | `[{accession, source, name}]` |
| `mcp__[database]__sample_get` | Full sample metadata | `accession`, `source` | `{accession, source, metadata{…}}` |
| `mcp__[database]__contig_get` | Contig DNA (optionally sliced) + features | `contig_hash`, `contig_length`, `source`, `start`, `end?`, `include_features`, `include_sequence`, `as_url` | `{…, sequence?, features?}` |

`source ∈ {[sources]}`; omit to fan-out across all. Set
`as_url=True` for large results — returns a [storage] signed link instead of
inlining (lifts the ~5MB inline cap).

## Recipe: protein → loci → flanking DNA → samples

Given an AA sequence, find where it (or close homologs) occurs in
metagenomes and pull genomic context:

1. `search_fast(sequences=[AA], top_n=20)` → pick the best `protein_id`
   (or `search_sensitive` if you need alignment-grade identity).
2. `protein_loci(sequence=AA, limit=50, include_dna=True, flank=500)` →
   list of `{contig_hash, contig_length, start, end, strand, dna}` per
   occurrence. `dna` is the CDS ± 500 bp flanks.
3. For one locus's broader context:
   `contig_get(contig_hash=…, contig_length=…, source=…, start=locus.start-5000,
   end=locus.end+5000, include_features=True, include_sequence=True)` → 10 kb
   window sequence + neighboring CDS features.
4. Trace to samples: `contig_samples(contig_hash=…, contig_length=…)` →
   `[{accession, source}]`, then `sample_get(accession=…, source=…)` for
   biome/host/study metadata.

## Recipe: batch homolog scan

Given a FASTA of queries, get a homolog table fast:

1. Read sequences with biopython.
2. `search_fast(sequences=[...], top_n=5, as_url=True)` → download the
   JSON, one hit-list per input. ~100 seqs in 2–5 s.
3. For hits above your threshold, loop `protein_get` (or build a list of
   row_keys for a future batch endpoint).

## Gotchas

- `protein_loci` is O(occurrences) — a ubiquitous protein
  (e.g., ribosomal) can return thousands; always set `limit`.
- `search_sensitive` runs DIAMOND server-side (~10–30s per query);
  prefer `search_fast` for triage, `search_sensitive` only when you
  need %identity.
- `sample_get` requires `source` (no fan-out) — get it from `contig_samples`.
- Inline DNA is capped at ~5MB; for large pulls use `as_url=True` and
  `curl -o` the signed link.
