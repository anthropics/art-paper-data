"""
USalign Python client for structure alignment.

This module provides a Python interface to USalign and related tools for
protein/RNA structure alignment and TM-score calculation.

Available tools:
- USalign: Universal structure alignment (main tool)
- TMscore: Fast TM-score calculation
- pdb2fasta: Extract sequences from PDB files
- pdb2ss: Extract secondary structure assignments
- cif2pdb: Convert mmCIF to PDB format
"""

import os
import re
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class AlignmentResult:
    """Result from a USalign structure alignment."""

    tm_score_chain1: float  # TM-score normalized by chain 1 length
    tm_score_chain2: float  # TM-score normalized by chain 2 length
    rmsd: float  # RMSD of aligned residues (Angstroms)
    aligned_length: int  # Number of aligned residues
    seq_identity: float  # Sequence identity of aligned region (0-1)
    chain1_length: int  # Length of chain 1
    chain2_length: int  # Length of chain 2
    alignment_string: str  # Alignment in text format
    rotation_matrix: list | None = None  # 3x4 rotation matrix [t, u]
    raw_output: str = ""  # Full stdout for debugging

    @property
    def tm_score_avg(self) -> float:
        """Average TM-score (normalized by both lengths)."""
        return (self.tm_score_chain1 + self.tm_score_chain2) / 2

    @property
    def is_same_fold(self) -> bool:
        """Returns True if TM-score indicates same fold (>0.5)."""
        return self.tm_score_avg > 0.5

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "tm_score_chain1": self.tm_score_chain1,
            "tm_score_chain2": self.tm_score_chain2,
            "tm_score_avg": self.tm_score_avg,
            "rmsd": self.rmsd,
            "aligned_length": self.aligned_length,
            "seq_identity": self.seq_identity,
            "chain1_length": self.chain1_length,
            "chain2_length": self.chain2_length,
            "is_same_fold": self.is_same_fold,
        }


@dataclass
class BatchAlignmentResult:
    """Results from batch alignment of multiple structures."""

    query: str
    results: list[dict] = field(default_factory=list)
    errors: list[dict] = field(default_factory=list)

    def top_hits(self, n: int = 10) -> list[dict]:
        """Get top N hits sorted by TM-score."""
        return sorted(self.results, key=lambda x: x.get("tm_score", 0), reverse=True)[:n]


def parse_usalign_output(output: str) -> AlignmentResult:
    """
    Parse USalign stdout into structured result.

    Handles output from USalign, TMalign, TMscore, and MMalign.
    """
    lines = output.strip().split("\n")

    tm1, tm2 = 0.0, 0.0
    rmsd = 0.0
    aligned_len = 0
    seq_id = 0.0
    len1, len2 = 0, 0
    alignment_lines = []
    rotation_matrix = []

    for _i, line in enumerate(lines):
        # Parse lengths - handle different formats
        if "Length of Chain_1:" in line or "Length of Structure_1:" in line:
            match = re.search(r"Length of (?:Chain|Structure)_1:\s*(\d+)", line)
            if match:
                len1 = int(match.group(1))
        if "Length of Chain_2:" in line or "Length of Structure_2:" in line:
            match = re.search(r"Length of (?:Chain|Structure)_2:\s*(\d+)", line)
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

        # Parse TM-scores - handle both old and new format
        if "TM-score=" in line:
            match = re.search(r"TM-score=\s*([\d.]+)", line)
            if match:
                score = float(match.group(1))
                if "Chain_1" in line or "Structure_1" in line or "Length_1" in line:
                    tm1 = score
                elif "Chain_2" in line or "Structure_2" in line or "Length_2" in line:
                    tm2 = score
                elif tm1 == 0:  # First TM-score found
                    tm1 = score
                elif tm2 == 0:  # Second TM-score found
                    tm2 = score

        # Parse rotation matrix (3 lines: t0 u00 u01 u02)
        if line.strip() and line.strip()[0].isdigit():
            parts = line.split()
            if len(parts) == 5 and parts[0] in ("0", "1", "2"):
                try:
                    rotation_matrix.append([float(x) for x in parts[1:]])
                except ValueError:
                    pass

        # Capture alignment block (last 6 lines with alignment)
        if ":" in line or (len(line) > 0 and not line.startswith(" ")):
            if any(c in line for c in "ACDEFGHIKLMNPQRSTVWY-"):
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


def run_usalign(
    pdb1: str,
    pdb2: str,
    output_prefix: str | None = None,
    mm_mode: int = 0,
    ter_mode: int = 0,
    chain_id1: str = "",
    chain_id2: str = "",
    split_mode: int = 0,
    outfmt: int = 0,
    fast: bool = False,
    mol_type: str = "",
    use_average_length: bool = False,
) -> AlignmentResult:
    """
    Run USalign on two structures and parse results.

    Args:
        pdb1: Path to first structure (PDB/mmCIF, can be gzipped)
        pdb2: Path to second structure (PDB/mmCIF, can be gzipped)
        output_prefix: Prefix for output files (creates .pml, _all.pdb, etc.)
        mm_mode: Multi-chain mode
            0 = auto-detect (default)
            1 = oligomeric alignment
            2 = force monomeric alignment
        ter_mode: TER record handling
            0 = read all chains (default)
            1 = first chain only
            2 = split by TER records
        chain_id1: Specific chain(s) from structure 1 (e.g., "A" or "A,B")
        chain_id2: Specific chain(s) from structure 2
        split_mode: Chain splitting
            0 = auto (default)
            1 = split by MODEL records
            2 = split by TER records
        outfmt: Output format
            0 = full output (default)
            1 = compact
            2 = tabular (for parsing)
        fast: Use fast mode (fewer iterations, less accurate)
        mol_type: Molecule type ("" = auto, "prot", "RNA", "DNA")
        use_average_length: Normalize TM-score by average length (-a flag)

    Returns:
        AlignmentResult with TM-scores, RMSD, and alignment details

    Raises:
        FileNotFoundError: If input files don't exist
        RuntimeError: If USalign fails
    """
    # Validate inputs
    if not os.path.exists(pdb1):
        raise FileNotFoundError(f"Structure 1 not found: {pdb1}")
    if not os.path.exists(pdb2):
        raise FileNotFoundError(f"Structure 2 not found: {pdb2}")

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
    if fast:
        cmd.append("-fast")
    if mol_type:
        cmd.extend(["-mol", mol_type])
    if use_average_length:
        cmd.append("-a")

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        raise RuntimeError(f"USalign failed: {result.stderr}")

    return parse_usalign_output(result.stdout)


def run_tmscore(pdb1: str, pdb2: str) -> AlignmentResult:
    """
    Compute TM-score without full structural alignment.

    Faster than run_usalign when you only need the TM-score,
    not the structural superposition or output files.

    Args:
        pdb1: Path to first structure
        pdb2: Path to second structure

    Returns:
        AlignmentResult (primarily use tm_score_chain1/chain2)
    """
    if not os.path.exists(pdb1):
        raise FileNotFoundError(f"Structure 1 not found: {pdb1}")
    if not os.path.exists(pdb2):
        raise FileNotFoundError(f"Structure 2 not found: {pdb2}")

    result = subprocess.run(
        ["TMscore", pdb1, pdb2],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"TMscore failed: {result.stderr}")

    return parse_usalign_output(result.stdout)


def run_mmalign(
    pdb1: str,
    pdb2: str,
    output_prefix: str | None = None,
) -> AlignmentResult:
    """
    Align multi-chain complexes using MMalign.

    Specifically designed for comparing oligomeric structures
    (dimers, trimers, etc.) where chain correspondence matters.

    Args:
        pdb1: Path to first complex
        pdb2: Path to second complex
        output_prefix: Prefix for output files

    Returns:
        AlignmentResult with complex-level TM-scores
    """
    if not os.path.exists(pdb1):
        raise FileNotFoundError(f"Structure 1 not found: {pdb1}")
    if not os.path.exists(pdb2):
        raise FileNotFoundError(f"Structure 2 not found: {pdb2}")

    cmd = ["MMalign", pdb1, pdb2]
    if output_prefix:
        cmd.extend(["-o", output_prefix])

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        raise RuntimeError(f"MMalign failed: {result.stderr}")

    return parse_usalign_output(result.stdout)


def pdb_to_fasta(pdb_path: str) -> dict[str, str]:
    """
    Extract amino acid/nucleotide sequences from a PDB/mmCIF file.

    Args:
        pdb_path: Path to structure file

    Returns:
        Dict mapping chain IDs to sequences
    """
    if not os.path.exists(pdb_path):
        raise FileNotFoundError(f"Structure not found: {pdb_path}")

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
            # Parse chain ID from header like ">1abc:A" or ">1abc_A"
            header = line[1:]
            if ":" in header:
                parts = header.split(":")
                current_chain = parts[1].split()[0] if len(parts) > 1 else parts[0]
            elif "_" in header:
                parts = header.split("_")
                current_chain = parts[-1].split()[0]
            else:
                current_chain = header.split()[0]
            current_seq = []
        elif line.strip():
            current_seq.append(line.strip())

    if current_chain:
        sequences[current_chain] = "".join(current_seq)

    return sequences


def pdb_to_secondary_structure(pdb_path: str) -> dict[str, str]:
    """
    Extract secondary structure assignment from PDB.

    Uses DSSP-like algorithm to assign:
    - H: helix (alpha, 3-10, pi)
    - E: extended strand (beta sheet)
    - C: coil/loop

    Args:
        pdb_path: Path to structure file

    Returns:
        Dict mapping chain IDs to secondary structure strings
    """
    if not os.path.exists(pdb_path):
        raise FileNotFoundError(f"Structure not found: {pdb_path}")

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
            # Same parsing as pdb_to_fasta
            header = line[1:]
            if ":" in header:
                parts = header.split(":")
                current_chain = parts[1].split()[0] if len(parts) > 1 else parts[0]
            elif "_" in header:
                parts = header.split("_")
                current_chain = parts[-1].split()[0]
            else:
                current_chain = header.split()[0]
            current_ss = []
        elif line.strip():
            current_ss.append(line.strip())

    if current_chain:
        structures[current_chain] = "".join(current_ss)

    return structures


def cif_to_pdb(cif_path: str, pdb_path: str) -> str:
    """
    Convert mmCIF file to PDB format.

    Args:
        cif_path: Path to input mmCIF file
        pdb_path: Path for output PDB file

    Returns:
        Path to output PDB file
    """
    if not os.path.exists(cif_path):
        raise FileNotFoundError(f"mmCIF file not found: {cif_path}")

    result = subprocess.run(
        ["cif2pdb", cif_path, pdb_path],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(f"cif2pdb failed: {result.stderr}")

    return pdb_path


def batch_align(
    query_pdb: str,
    target_dir: str,
    target_pattern: str = "*.pdb",
    fast: bool = True,
) -> BatchAlignmentResult:
    """
    Align a query structure against all structures in a directory.

    Args:
        query_pdb: Path to query structure
        target_dir: Directory containing target structures
        target_pattern: Glob pattern for target files
        fast: Use fast mode for quicker alignments

    Returns:
        BatchAlignmentResult with sorted results and any errors
    """
    if not os.path.exists(query_pdb):
        raise FileNotFoundError(f"Query structure not found: {query_pdb}")

    batch_result = BatchAlignmentResult(query=query_pdb)

    for target in Path(target_dir).glob(target_pattern):
        try:
            result = run_usalign(query_pdb, str(target), fast=fast)
            batch_result.results.append(
                {
                    "target": target.name,
                    "target_path": str(target),
                    "tm_score": result.tm_score_chain1,
                    "tm_score_reverse": result.tm_score_chain2,
                    "rmsd": result.rmsd,
                    "aligned_length": result.aligned_length,
                    "seq_identity": result.seq_identity,
                }
            )
        except Exception as e:
            batch_result.errors.append(
                {
                    "target": target.name,
                    "error": str(e),
                }
            )

    # Sort by TM-score descending
    batch_result.results.sort(key=lambda x: x.get("tm_score", 0), reverse=True)
    return batch_result


def cluster_structures(
    pdb_dir: str,
    tm_threshold: float = 0.5,
    output_file: str | None = None,
) -> dict:
    """
    Cluster structures by TM-score using qTMclust.

    Args:
        pdb_dir: Directory containing PDB files to cluster
        tm_threshold: TM-score threshold for clustering (default: 0.5)
        output_file: Optional output file for cluster assignments

    Returns:
        Dict with cluster assignments and representatives
    """
    # Create list file
    pdb_files = list(Path(pdb_dir).glob("*.pdb"))
    if not pdb_files:
        raise ValueError(f"No PDB files found in {pdb_dir}")

    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        for pdb in pdb_files:
            f.write(f"{pdb}\n")
        list_file = f.name

    try:
        out_file = output_file or tempfile.mktemp(suffix="_clusters.txt")
        result = subprocess.run(
            [
                "qTMclust",
                "-list",
                list_file,
                "-out",
                out_file,
                "-TMcut",
                str(tm_threshold),
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            raise RuntimeError(f"qTMclust failed: {result.stderr}")

        # Parse output
        clusters = {}
        with open(out_file) as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) >= 2:
                    cluster_id = parts[0]
                    member = parts[1]
                    if cluster_id not in clusters:
                        clusters[cluster_id] = {"representative": member, "members": []}
                    clusters[cluster_id]["members"].append(member)

        return {
            "clusters": clusters,
            "num_clusters": len(clusters),
            "num_structures": len(pdb_files),
            "tm_threshold": tm_threshold,
        }

    finally:
        os.unlink(list_file)
        if output_file is None and os.path.exists(out_file):
            os.unlink(out_file)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage: python usalign_client.py <pdb1> <pdb2> [output_prefix]")
        print("\nTools available:")
        print("  USalign - Universal structure alignment")
        print("  TMscore - Fast TM-score calculation")
        print("  pdb2fasta - Extract sequences")
        print("  pdb2ss - Extract secondary structure")
        print("  cif2pdb - Convert mmCIF to PDB")
        print("  qTMclust - TM-score based clustering")
        sys.exit(1)

    pdb1 = sys.argv[1]
    pdb2 = sys.argv[2]
    output_prefix = sys.argv[3] if len(sys.argv) > 3 else None

    result = run_usalign(pdb1, pdb2, output_prefix=output_prefix)

    print("\nAlignment Results:")
    print(f"  TM-score (norm by structure 1): {result.tm_score_chain1:.4f}")
    print(f"  TM-score (norm by structure 2): {result.tm_score_chain2:.4f}")
    print(f"  RMSD: {result.rmsd:.2f} A")
    print(f"  Aligned length: {result.aligned_length}")
    print(f"  Sequence identity: {result.seq_identity:.1%}")
    print(f"  Same fold: {result.is_same_fold}")

    if output_prefix:
        print("\nOutput files:")
        print(f"  PyMOL script: {output_prefix}.pml")
        print(f"  Superposed structure: {output_prefix}_all.pdb")
