# USalign Parameters Reference

Complete reference for USalign command-line options and parameters.

## USalign Main Options

### Input/Output

| Option        | Description                                            | Default |
| ------------- | ------------------------------------------------------ | ------- |
| `-o <prefix>` | Output prefix for superposed structure and scripts     | None    |
| `-a`          | Normalize TM-score by average length of two structures | False   |
| `-u <length>` | Normalize TM-score by specified length                 | Auto    |
| `-d <d0>`     | Use specified d0 for TM-score calculation              | Auto    |

### Chain Selection

| Option         | Description                                            | Default    |
| -------------- | ------------------------------------------------------ | ---------- |
| `-chain1 <id>` | Specify chain(s) from structure 1 (e.g., "A" or "A,B") | All chains |
| `-chain2 <id>` | Specify chain(s) from structure 2                      | All chains |

### Multi-chain Modes (-mm)

| Value | Mode       | Description                                             |
| ----- | ---------- | ------------------------------------------------------- |
| 0     | Auto       | Automatically detect if oligomeric alignment needed     |
| 1     | Oligomeric | Align multi-chain complexes, find optimal chain pairing |
| 2     | Monomeric  | Force monomeric alignment (concatenate all chains)      |
| 3     | CP         | Circular permutation alignment                          |
| 4     | MSTA       | Multiple structure alignment                            |
| 5     | Flexible   | Flexible structure alignment (hinge detection)          |

### TER Record Handling (-ter)

| Value | Behavior                       |
| ----- | ------------------------------ |
| 0     | Read all chains (default)      |
| 1     | Read first chain only          |
| 2     | Split structure by TER records |

### Chain Splitting (-split)

| Value | Behavior               |
| ----- | ---------------------- |
| 0     | Auto-detect (default)  |
| 1     | Split by MODEL records |
| 2     | Split by TER records   |

### Molecule Type (-mol)

| Value  | Description           |
| ------ | --------------------- |
| `auto` | Auto-detect (default) |
| `prot` | Protein               |
| `RNA`  | RNA                   |
| `DNA`  | DNA                   |

### Output Format (-outfmt)

| Value | Format                       |
| ----- | ---------------------------- |
| 0     | Full output (default)        |
| 1     | Compact output               |
| 2     | Tabular output (for parsing) |

### Performance Options

| Option          | Description                                            |
| --------------- | ------------------------------------------------------ |
| `-fast`         | Fast mode, fewer iterations (less accurate but faster) |
| `-dir <path>`   | Path to directory containing template structures       |
| `-suffix <ext>` | File extension for templates (default: .pdb)           |

### Output Files

When `-o <prefix>` is specified, USalign creates:

| File               | Description                          |
| ------------------ | ------------------------------------ |
| `<prefix>.pml`     | PyMOL visualization script           |
| `<prefix>_all.pdb` | Superposed structures in single file |
| `<prefix>_atm`     | Transformed structure 1              |
| `<prefix>.fasta`   | Aligned sequences in FASTA format    |

## TMscore Options

TMscore computes TM-score without full structure alignment.

| Option        | Description                                  |
| ------------- | -------------------------------------------- |
| `-a`          | Normalize by average length                  |
| `-u <length>` | Normalize by specified length                |
| `-d <d0>`     | Specify d0 value                             |
| `-L`          | Use both structures for length normalization |

## MMalign Options

MMalign is specifically for multi-chain complex alignment.

| Option        | Description                 |
| ------------- | --------------------------- |
| `-o <prefix>` | Output prefix               |
| `-a`          | Normalize by average length |
| `-d <d0>`     | Specify d0 value            |

## pdb2fasta Options

Extract sequences from PDB/mmCIF files.

| Option         | Description                         |
| -------------- | ----------------------------------- |
| `-mol <type>`  | Molecule type filter (prot/RNA/DNA) |
| `-atom <type>` | Atom type filter (CA/P/all)         |
| `-ter <mode>`  | TER handling (0/1/2)                |

## pdb2ss Options

Extract secondary structure assignments.

| Option        | Description   |
| ------------- | ------------- |
| `-mol <type>` | Molecule type |
| `-ter <mode>` | TER handling  |

## cif2pdb Options

Convert mmCIF to PDB format.

```bash
cif2pdb input.cif output.pdb
```

## qTMclust Options

TM-score based structure clustering.

| Option           | Description                       | Default     |
| ---------------- | --------------------------------- | ----------- |
| `-list <file>`   | File containing list of PDB paths | Required    |
| `-out <file>`    | Output cluster assignments        | stdout      |
| `-TMcut <float>` | TM-score threshold for clustering | 0.5         |
| `-chain <id>`    | Chain to use from each structure  | First chain |

## HwRMSD Options

Hierarchical weighted RMSD calculation.

| Option        | Description                 |
| ------------- | --------------------------- |
| `-o <prefix>` | Output prefix               |
| `-a`          | Use all atoms               |
| `-ca`         | Use only CA atoms (default) |

## NWalign Options

Needleman-Wunsch sequence alignment.

| Option         | Description       | Default |
| -------------- | ----------------- | ------- |
| `-gap <float>` | Gap penalty       | -1.0    |
| `-ext <float>` | Extension penalty | -0.5    |

## TM-score Interpretation

| TM-score Range | Interpretation               |
| -------------- | ---------------------------- |
| < 0.17         | Random structural similarity |
| 0.17 - 0.30    | Twilight zone                |
| 0.30 - 0.50    | Same superfamily             |
| 0.50 - 0.70    | Same fold                    |
| 0.70 - 0.90    | Closely related              |
| > 0.90         | Nearly identical             |

## Example Commands

### Basic Alignment

```bash
# Simple alignment
USalign structure1.pdb structure2.pdb

# Generate PyMOL script
USalign structure1.pdb structure2.pdb -o alignment

# Normalize by average length
USalign structure1.pdb structure2.pdb -a
```

### Chain-specific Alignment

```bash
# Align specific chains
USalign complex1.pdb -chain1 A complex2.pdb -chain2 B

# Multiple chains
USalign complex1.pdb -chain1 A,B complex2.pdb -chain2 C,D
```

### Oligomeric Alignment

```bash
# Align dimers
USalign dimer1.pdb dimer2.pdb -mm 1

# Force monomeric treatment
USalign dimer1.pdb dimer2.pdb -mm 2
```

### RNA Structure Alignment

```bash
# Align RNA structures
USalign rna1.pdb rna2.pdb -mol RNA
```

### Flexible Alignment

```bash
# Detect hinges and flexible regions
USalign structure1.pdb structure2.pdb -mm 5
```

### Circular Permutation

```bash
# Handle circularly permuted proteins
USalign cp_protein1.pdb cp_protein2.pdb -mm 3
```

### Batch Processing

```bash
# Align query against database
USalign query.pdb -dir templates/ -suffix .pdb -outfmt 2 > results.tsv
```

### Clustering

```bash
# Create structure clusters
qTMclust -list pdb_list.txt -out clusters.txt -TMcut 0.5
```

### Sequence Extraction

```bash
# Extract all sequences
pdb2fasta structure.pdb > sequences.fasta

# Extract protein only
pdb2fasta structure.pdb -mol prot > protein.fasta

# Extract secondary structure
pdb2ss structure.pdb > secondary_structure.txt
```

### Format Conversion

```bash
# Convert mmCIF to PDB
cif2pdb input.cif output.pdb
```

## Common Patterns

### Compare Experimental vs Predicted

```bash
# AlphaFold vs experimental
USalign AF-P00533-F1-model_v4.pdb 1m14.pdb -o egfr_comparison
```

### Domain Alignment

```bash
# Align single domain
USalign domain1.pdb domain2.pdb -ter 1
```

### Multi-model Ensemble

```bash
# Align all models in NMR ensemble
USalign ensemble.pdb reference.pdb -split 1
```

## Performance Tips

1. **Use `-fast` for screening**: When comparing many structures, use fast mode for initial filtering, then run full alignment on top hits.

2. **Batch processing**: Use `-dir` option for aligning against a template library instead of scripting multiple calls.

3. **Memory management**: For very large structures, consider splitting into domains.

4. **Output parsing**: Use `-outfmt 2` for tabular output that's easy to parse programmatically.

## Troubleshooting

| Issue                             | Solution                                   |
| --------------------------------- | ------------------------------------------ |
| "Cannot read structure"           | Check file format, try cif2pdb for mmCIF   |
| Low TM-score for similar proteins | Check chain selection with -chain1/-chain2 |
| Memory error                      | Use -fast mode or split structure          |
| Wrong chain aligned               | Explicitly specify chains                  |
| NMR ensemble issues               | Use -split 1 to separate models            |
