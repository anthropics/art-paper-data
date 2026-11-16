---
name: hmmer
description: Protein homology search and domain annotation using HMMER via the EBI web API. Supports phmmer (sequence vs sequence DB), hmmscan (sequence vs profile DB like Pfam), hmmsearch (profile vs sequence DB), and jackhmmer (iterative search). No local installation required.
---

# HMMER Web Service Skill

HMMER uses profile hidden Markov models for sensitive protein homology detection. The EBI provides a free REST API supporting all four HMMER search algorithms. HMMER finds remote homologs that BLAST misses and provides gold-standard Pfam domain annotations.

## Quick Reference

| Algorithm     | Input              | Searches Against            | Best For                                          |
| ------------- | ------------------ | --------------------------- | ------------------------------------------------- |
| **phmmer**    | protein sequence   | sequence database           | Finding homologs (like BLASTP but more sensitive) |
| **hmmscan**   | protein sequence   | profile HMM database (Pfam) | Domain/family annotation                          |
| **hmmsearch** | MSA or HMM profile | sequence database           | Searching with custom profiles                    |
| **jackhmmer** | protein sequence   | sequence database           | Finding distant homologs (iterative)              |

## When to Use Each Algorithm

- **phmmer**: Default choice for finding homologous proteins. More sensitive than BLAST.
- **hmmscan**: Annotating domains in a protein sequence. Returns Pfam family hits.
- **hmmsearch**: When you already have a multiple sequence alignment or HMM profile.
- **jackhmmer**: For very remote homology — iteratively refines a profile from initial hits.

## Using the Client Script

The `scripts/hmmer_client.py` module provides a Python interface to the EBI HMMER API.

### Domain Annotation (hmmscan)

```python
import subprocess, sys
sys.path.insert(0, "/path/to/hmmer/scripts")
from hmmer_client import hmmscan, get_domain_annotations, summarize_results

# Quick Pfam domain annotation
sequence = "MKWMFKEDHSLEHRCVESAKIRAKYPDRVPVIVEKVSGSQIVDIDKRKYLVPSDITVAQFMWIIRKRIQLPSEKAIFLFVDKTVPQSR"
annotations = get_domain_annotations(sequence)
for ann in annotations:
    print(f"  {ann['name']} ({ann['acc']}): {ann['description']}")
    print(f"    E-value: {ann['evalue']:.2e}, region: {ann['ali_from']}-{ann['ali_to']}")
```

### Homology Search (phmmer)

```python
from hmmer_client import phmmer, summarize_results

sequence = "MKWMFKEDHSLEHRCVESAKIRAKYPDRVPVIVEKVSGSQIVDIDKRKYLVPSDITVAQFMWIIRKRIQLPSEKAIFLFVDKTVPQSR"

# Search against UniProt reference proteomes (default)
results = phmmer(sequence)
summarize_results(results)

# Search against PDB sequences
results = phmmer(sequence, database="pdb")
summarize_results(results)
```

### Iterative Search (jackhmmer)

```python
from hmmer_client import jackhmmer, summarize_results

# Find remote homologs with iterative refinement
results = jackhmmer(sequence, database="swissprot", iterations=3)
summarize_results(results, top_n=15)
```

### Profile-Based Search (hmmsearch)

```python
from hmmer_client import hmmsearch, summarize_results

# Search with a Stockholm-format MSA
msa = open("my_alignment.sto").read()
results = hmmsearch(msa, database="swissprot")
summarize_results(results)
```

### Generic Search Function

```python
from hmmer_client import search

# Low-level search with custom parameters
results = search(
    algo="phmmer",
    input_data="MKWMFKEDHSLEHR...",
    database="swissprot",
    E=0.001,         # Stricter E-value threshold
    domE=0.001,      # Domain E-value threshold
)
```

## Databases

### Sequence Databases (phmmer, hmmsearch, jackhmmer)

| ID          | Description                                 |
| ----------- | ------------------------------------------- |
| `refprot`   | Reference Proteomes (default)               |
| `uniprot`   | Full UniProt                                |
| `swissprot` | SwissProt — manually reviewed, high quality |
| `pdb`       | PDB — sequences with solved structures      |
| `rp15`      | Representative Proteomes 15% co-membership  |
| `rp35`      | Representative Proteomes 35%                |
| `rp55`      | Representative Proteomes 55%                |
| `rp75`      | Representative Proteomes 75%                |

### Profile HMM Databases (hmmscan)

| ID     | Description                     |
| ------ | ------------------------------- |
| `pfam` | Pfam protein families (default) |

## Interpreting Results

### Key Metrics

| Metric        | Significant | Description                                            |
| ------------- | ----------- | ------------------------------------------------------ |
| **E-value**   | < 0.01      | Expected false positives at this score; lower = better |
| **Bit score** | > 25        | Log-odds score; higher = better match                  |
| **Bias**      | Low         | Composition bias correction; high bias = less reliable |

### Domain-Level Fields

| Field         | Description                                                     |
| ------------- | --------------------------------------------------------------- |
| `cevalue`     | Conditional E-value (significance given the sequence was found) |
| `ievalue`     | Independent E-value (significance from domain alone)            |
| `iali`–`jali` | Alignment coordinates on target                                 |
| `ienv`–`jenv` | Envelope coordinates (broader region of homology)               |

### E-value Guidelines

- **< 1e-10**: Very strong match, almost certainly homologous
- **1e-10 to 1e-5**: Strong match, likely homologous
- **1e-5 to 0.01**: Moderate match, probable homolog
- **0.01 to 1.0**: Weak match, investigate further
- **> 1.0**: Not significant

## Command-Line Usage

The client can also be run directly:

```bash
# phmmer search
python hmmer_client.py --algo phmmer --sequence "MKWMFKEDHSLEHR..."

# hmmscan for domain annotation
python hmmer_client.py --algo hmmscan --sequence "MKWMFKEDHSLEHR..."

# Search with specific database
python hmmer_client.py --algo phmmer --sequence "MKWMFKEDHSLEHR..." --database swissprot

# Read sequence from file
python hmmer_client.py --algo phmmer --input-file protein.fasta
```

## Troubleshooting

| Issue                       | Solution                                                                   |
| --------------------------- | -------------------------------------------------------------------------- |
| Timeout waiting for results | Increase `max_attempts` or `poll_interval`; large DB searches take longer  |
| No significant hits         | Try jackhmmer for remote homologs, or relax E-value threshold              |
| Too many hits               | Use stricter thresholds (`E=1e-5`), or search a smaller database           |
| HTTP 500 from API           | EBI server issue — retry after a few minutes                               |
| Malformed sequence error    | Ensure input is protein amino acid letters only (no headers for raw input) |
