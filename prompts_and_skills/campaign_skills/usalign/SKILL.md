---
name: usalign
description: Universal Structure Alignment tool for protein and RNA structure comparison. Compute TM-scores, perform structure superposition, and generate visualization scripts. Supports monomeric, oligomeric, and flexible alignments.
---

# USalign Skill

USalign (Universal Structure Alignment) is the recommended tool for protein and RNA structure alignment. It supersedes TM-align, TM-score, and MMalign with a unified interface supporting all structure alignment scenarios.

## Quick Reference

| Task                        | Tool            | Command                                   |
| --------------------------- | --------------- | ----------------------------------------- |
| Align two monomers          | `USalign`       | `USalign struct1.pdb struct2.pdb`         |
| Compute TM-score only       | `TMscore`       | `TMscore struct1.pdb struct2.pdb`         |
| Align multi-chain complexes | `USalign -mm 1` | `USalign complex1.pdb complex2.pdb -mm 1` |
| Extract sequence from PDB   | `pdb2fasta`     | `pdb2fasta struct.pdb`                    |
| Extract secondary structure | `pdb2ss`        | `pdb2ss struct.pdb`                       |
| Convert mmCIF to PDB        | `cif2pdb`       | `cif2pdb struct.cif struct.pdb`           |

## Installed Tools

The following tools are available in `/usr/local/bin/`:

- **USalign** - Universal structure alignment (main tool)
- **TMalign** - Classic TM-align for monomeric proteins
- **TMscore** - TM-score calculation without full alignment
- **MMalign** - Multi-chain complex alignment
- **pdb2fasta** - Convert PDB/mmCIF to FASTA sequence
- **pdb2ss** - Extract secondary structure (3-state: H/E/C)
- **cif2pdb** - Convert mmCIF to PDB format
- **NWalign** - Needleman-Wunsch sequence alignment
- **HwRMSD** - Hierarchical weighted RMSD calculation
- **qTMclust** - TM-score based structure clustering

## Python Wrapper

Use the `usalign_client` module for programmatic access. Copy this into your `python` tool calls:

```python
import subprocess
import tempfile
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import re


@dataclass
class AlignmentResult:
    """Result from a USalign structure alignment."""
    tm_score_chain1: float      # TM-score normalized by chain 1 length
    tm_score_chain2: float      # TM-score normalized by chain 2 length
    rmsd: float                 # RMSD of aligned residues
    aligned_length: int         # Number of aligned residues
    seq_identity: float         # Sequence identity of aligned region
    chain1_length: int          # Length of chain 1
    chain2_length: int          # Length of chain 2
    alignment_string: str       # Alignment in text format
    rotation_matrix: Optional[list] = None  # 3x4 rotation matrix
    raw_output: str = ""        # Full stdout for debugging


def run_usalign(
    pdb1: str,
    pdb2: str,
    output_prefix: Optional[str] = None,
    mm_mode: int = 0,
    ter_mode: int = 0,
    chain_id1: str = "",
    chain_id2: str = "",
    split_mode: int = 0,
    outfmt: int = 0,
) -> AlignmentResult:
    """
    Run USalign on two structures and parse results.

    Args:
        pdb1: Path to first structure (PDB/mmCIF)
        pdb2: Path to second structure (PDB/mmCIF)
        output_prefix: Prefix for output files (PyMOL scripts, etc.)
        mm_mode: Multi-chain mode (0=auto, 1=oligomeric, 2=monomer)
        ter_mode: How to handle TER records (0=read all chains, 1=first chain, 2=split by TER)
        chain_id1: Specific chain from structure 1 (e.g., "A" or "A,B")
        chain_id2: Specific chain from structure 2
        split_mode: Chain split mode (0=auto, 1=by model, 2=by TER)
        outfmt: Output format (0=full, 1=compact, 2=tabular)

    Returns:
        AlignmentResult with TM-scores, RMSD, and alignment details
    """
    cmd = ["USalign", pdb1, pdb2]

    if output_prefix:
        cmd.extend(["-o", output_prefix])
    if mm_mode > 0:
        cmd.extend(["-mm", str(mm_mode)])
    if ter_mode > 0:
        cmd.extend(["-ter", str(ter_mode)])
    if chain_id1:
        cmd.extend(["-chain1", chain_id1])
    if chain_id2:
        cmd.extend(["-chain2", chain_id2])
    if split_mode > 0:
        cmd.extend(["-split", str(split_mode)])
    if outfmt > 0:
        cmd.extend(["-outfmt", str(outfmt)])

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        raise RuntimeError(f"USalign failed: {result.stderr}")

    return parse_usalign_output(result.stdout)


def parse_usalign_output(output: str) -> AlignmentResult:
    """Parse USalign stdout into structured result."""
    lines = output.strip().split("\n")

    tm1, tm2 = 0.0, 0.0
    rmsd = 0.0
    aligned_len = 0
    seq_id = 0.0
    len1, len2 = 0, 0
    alignment_lines = []
    rotation_matrix = []

    for i, line in enumerate(lines):
        # Parse lengths - handle both "Structure_1" and "Chain_1" formats
        if "Length of Structure_1:" in line or "Length of Chain_1:" in line:
            match = re.search(r"Length of (?:Structure|Chain)_1:\s*(\d+)", line)
            if match:
                len1 = int(match.group(1))
        if "Length of Structure_2:" in line or "Length of Chain_2:" in line:
            match = re.search(r"Length of (?:Structure|Chain)_2:\s*(\d+)", line)
            if match:
                len2 = int(match.group(1))

        # Parse aligned length and RMSD
        if "Aligned length=" in line:
            match = re.search(r"Aligned length=\s*(\d+),\s*RMSD=\s*([\d.]+)", line)
            if match:
                aligned_len = int(match.group(1))
                rmsd = float(match.group(2))
            # Seq_ID
            match = re.search(r"Seq_ID=n_identical/n_aligned=\s*([\d.]+)", line)
            if match:
                seq_id = float(match.group(1))

        # Parse TM-scores - handle both "Structure_1" and "Chain_1" formats
        if "TM-score=" in line and "(normalized by" in line:
            match = re.search(r"TM-score=\s*([\d.]+)", line)
            if match:
                if "Structure_1" in line or "Chain_1" in line:
                    tm1 = float(match.group(1))
                elif "Structure_2" in line or "Chain_2" in line:
                    tm2 = float(match.group(1))

        # Parse rotation matrix (3 lines starting with numbers)
        if line.strip().startswith(("0 ", "1 ", "2 ")):
            parts = line.split()
            if len(parts) == 5:
                rotation_matrix.append([float(x) for x in parts[1:]])

        # Capture alignment block
        if line.startswith((":", "(")) or (len(line) > 0 and line[0].isupper() and "-" in line):
            alignment_lines.append(line)

    return AlignmentResult(
        tm_score_chain1=tm1,
        tm_score_chain2=tm2,
        rmsd=rmsd,
        aligned_length=aligned_len,
        seq_identity=seq_id,
        chain1_length=len1,
        chain2_length=len2,
        alignment_string="\n".join(alignment_lines[-6:]) if alignment_lines else "",
        rotation_matrix=rotation_matrix if len(rotation_matrix) == 3 else None,
        raw_output=output,
    )


def run_tmscore(pdb1: str, pdb2: str) -> AlignmentResult:
    """
    Compute TM-score without full alignment (faster).

    Use when you only need TM-score, not the structural superposition.
    """
    result = subprocess.run(
        ["TMscore", pdb1, pdb2],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"TMscore failed: {result.stderr}")

    return parse_usalign_output(result.stdout)


def pdb_to_fasta(pdb_path: str) -> dict[str, str]:
    """
    Extract sequences from PDB/mmCIF file.

    Returns:
        Dict mapping chain IDs to sequences
    """
    result = subprocess.run(
        ["pdb2fasta", pdb_path],
        capture_output=True,
        text=True,
    )

    sequences = {}
    current_chain = None
    current_seq = []

    for line in result.stdout.strip().split("\n"):
        if line.startswith(">"):
            if current_chain:
                sequences[current_chain] = "".join(current_seq)
            # Parse chain ID from header like ">1abc:A"
            parts = line[1:].split(":")
            current_chain = parts[1] if len(parts) > 1 else parts[0]
            current_seq = []
        else:
            current_seq.append(line.strip())

    if current_chain:
        sequences[current_chain] = "".join(current_seq)

    return sequences


def pdb_to_secondary_structure(pdb_path: str) -> dict[str, str]:
    """
    Extract secondary structure assignment from PDB.

    Returns:
        Dict mapping chain IDs to SS strings (H=helix, E=strand, C=coil)
    """
    result = subprocess.run(
        ["pdb2ss", pdb_path],
        capture_output=True,
        text=True,
    )

    structures = {}
    current_chain = None
    current_ss = []

    for line in result.stdout.strip().split("\n"):
        if line.startswith(">"):
            if current_chain:
                structures[current_chain] = "".join(current_ss)
            parts = line[1:].split(":")
            current_chain = parts[1] if len(parts) > 1 else parts[0]
            current_ss = []
        else:
            current_ss.append(line.strip())

    if current_chain:
        structures[current_chain] = "".join(current_ss)

    return structures
```

## Common Use Cases

### Compare Two Protein Structures

```python
# Fetch and compare two kinase structures
from Bio.PDB import PDBList
pdbl = PDBList()

# Download structures
pdbl.retrieve_pdb_file("1ATP", pdir="/workspace", file_format="pdb")
pdbl.retrieve_pdb_file("1CDK", pdir="/workspace", file_format="pdb")

# Run alignment
result = run_usalign("/workspace/pdb1atp.ent", "/workspace/pdb1cdk.ent")

print(f"TM-score (norm by 1ATP): {result.tm_score_chain1:.3f}")
print(f"TM-score (norm by 1CDK): {result.tm_score_chain2:.3f}")
print(f"RMSD: {result.rmsd:.2f} A")
print(f"Aligned residues: {result.aligned_length}")
print(f"Sequence identity: {result.seq_identity:.1%}")

# Interpretation:
# TM-score > 0.5: Same fold
# TM-score > 0.7: Closely related structures
```

### Generate PyMOL Visualization Script

```python
import subprocess
import os

# Align and generate PyMOL script
result = run_usalign(
    "/workspace/structure1.pdb",
    "/workspace/structure2.pdb",
    output_prefix="/workspace/alignment"  # Creates alignment.pml
)

# The alignment.pml file can be loaded in PyMOL:
# pymol alignment.pml
# Or view the superposed structures:
# alignment_all.pdb (combined structure after rotation)

if os.path.exists("/workspace/alignment.pml"):
    with open("/workspace/alignment.pml") as f:
        print("PyMOL script generated:")
        print(f.read()[:500])  # First 500 chars
```

### Align Specific Chains

```python
# Align chain A from structure 1 with chain B from structure 2
result = run_usalign(
    "/workspace/complex1.pdb",
    "/workspace/complex2.pdb",
    chain_id1="A",
    chain_id2="B",
)

print(f"TM-score: {result.tm_score_chain1:.3f}")
```

### Oligomeric Complex Alignment

```python
# Align two multi-chain complexes (e.g., dimers, trimers)
result = run_usalign(
    "/workspace/dimer1.pdb",
    "/workspace/dimer2.pdb",
    mm_mode=1,  # Enable oligomeric alignment
)

print(f"TM-score: {result.tm_score_chain1:.3f}")
print(f"RMSD: {result.rmsd:.2f} A")
```

### Batch Alignment of Multiple Structures

```python
from pathlib import Path

def batch_align(query_pdb: str, target_dir: str, target_pattern: str = "*.pdb") -> list[dict]:
    """Align query against all structures in a directory."""
    results = []

    for target in Path(target_dir).glob(target_pattern):
        try:
            result = run_usalign(query_pdb, str(target))
            results.append({
                "target": target.name,
                "tm_score": result.tm_score_chain1,
                "rmsd": result.rmsd,
                "aligned_length": result.aligned_length,
            })
        except Exception as e:
            results.append({
                "target": target.name,
                "error": str(e),
            })

    # Sort by TM-score descending
    results.sort(key=lambda x: x.get("tm_score", 0), reverse=True)
    return results

# Example: Find closest structures to a query
results = batch_align("/workspace/query.pdb", "/workspace/candidates/")
for r in results[:10]:
    if "tm_score" in r:
        print(f"{r['target']}: TM={r['tm_score']:.3f}, RMSD={r['rmsd']:.2f}")
```

### Extract Sequence and Secondary Structure

```python
# Get sequence from PDB
sequences = pdb_to_fasta("/workspace/structure.pdb")
for chain, seq in sequences.items():
    print(f"Chain {chain}: {seq[:50]}... ({len(seq)} residues)")

# Get secondary structure
ss = pdb_to_secondary_structure("/workspace/structure.pdb")
for chain, structure in ss.items():
    helix_frac = structure.count("H") / len(structure)
    sheet_frac = structure.count("E") / len(structure)
    print(f"Chain {chain}: {helix_frac:.1%} helix, {sheet_frac:.1%} sheet")
```

### Compare AlphaFold Model to Experimental Structure

```python
import requests

def fetch_alphafold_structure(uniprot_id: str, output_path: str):
    """Download AlphaFold structure for a UniProt ID."""
    url = f"https://alphafold.ebi.ac.uk/files/AF-{uniprot_id}-F1-model_v4.pdb"
    response = requests.get(url)
    response.raise_for_status()
    with open(output_path, "w") as f:
        f.write(response.text)

# Compare AlphaFold prediction to experimental structure
fetch_alphafold_structure("P00533", "/workspace/af_egfr.pdb")

result = run_usalign("/workspace/af_egfr.pdb", "/workspace/pdb1m14.ent")

print(f"AlphaFold vs Experimental:")
print(f"  TM-score: {result.tm_score_chain1:.3f}")
print(f"  RMSD: {result.rmsd:.2f} A")
print(f"  Aligned: {result.aligned_length}/{result.chain1_length} residues")
```

## Understanding TM-score

TM-score is the gold standard for measuring structural similarity:

| TM-score  | Interpretation                            |
| --------- | ----------------------------------------- |
| < 0.17    | Random structural similarity              |
| 0.17-0.30 | Twilight zone, uncertain relationship     |
| 0.30-0.50 | Same superfamily, likely similar function |
| 0.50-0.70 | Same fold, related structures             |
| > 0.70    | Closely related or identical folds        |
| > 0.90    | Nearly identical structures               |

**Key properties:**

- Length-independent (normalized by target length)
- Always between 0 and 1
- Values > 0.5 indicate same fold with high confidence

## CLI Reference

See `references/parameters_reference.md` for complete command-line options.

### Quick Examples

```bash
# Basic alignment
USalign struct1.pdb struct2.pdb

# Generate PyMOL script
USalign struct1.pdb struct2.pdb -o output_prefix

# Oligomeric alignment
USalign complex1.pdb complex2.pdb -mm 1

# Align specific chains
USalign struct1.pdb -chain1 A struct2.pdb -chain2 B

# Use TM-score normalization by average length
USalign struct1.pdb struct2.pdb -a

# Fast mode (fewer iterations)
USalign struct1.pdb struct2.pdb -fast

# RNA structure alignment
USalign rna1.pdb rna2.pdb -mol RNA
```

## Troubleshooting

| Issue                             | Solution                                                |
| --------------------------------- | ------------------------------------------------------- |
| "Structure too short"             | Ensure structure has > 5 residues                       |
| Low TM-score for similar proteins | Try different chain selection with `-chain1`/`-chain2`  |
| Memory error with large complexes | Use `-fast` mode or split into domains                  |
| Different alignment than expected | Check `-ter` and `-split` options for multi-model files |
| mmCIF parsing issues              | Convert to PDB first with `cif2pdb`                     |

## Integration with Other Tools

### With Foldseek

Use Foldseek to find structural homologs, then USalign for detailed comparison:

```python
from foldseek_client import search as foldseek_search

# Find homologs
hits = foldseek_search("/workspace/query.pdb")

# Get top hit PDB and align in detail
top_hit_pdb = download_pdb(hits["pdb100"][0]["pdb_id"])
detailed = run_usalign("/workspace/query.pdb", top_hit_pdb)
print(f"Detailed alignment: TM={detailed.tm_score_chain1:.3f}, RMSD={detailed.rmsd:.2f}")
```

### With BioPython for Structure Preparation

```python
from Bio.PDB import PDBParser, PDBIO, Select

class ChainSelect(Select):
    def __init__(self, chain_id):
        self.chain_id = chain_id

    def accept_chain(self, chain):
        return chain.id == self.chain_id

# Extract single chain for alignment
parser = PDBParser()
structure = parser.get_structure("complex", "/workspace/complex.pdb")

io = PDBIO()
io.set_structure(structure)
io.save("/workspace/chain_a.pdb", ChainSelect("A"))

# Now align the extracted chain
result = run_usalign("/workspace/chain_a.pdb", "/workspace/reference.pdb")
```
