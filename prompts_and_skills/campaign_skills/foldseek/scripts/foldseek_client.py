"""
Foldseek API client for structural similarity searches.

This module provides a Python interface to the Foldseek web API at search.foldseek.com.
"""

import io
import re
import tarfile
import time
from dataclasses import dataclass
from pathlib import Path

import requests

API_BASE = "https://search.foldseek.com/api"

# Available databases
DATABASES = {
    "afdb50": "AlphaFold DB 50% clustered (~54M structures)",
    "afdb-swissprot": "AlphaFold Swiss-Prot subset (~540K)",
    "afdb-proteome": "AlphaFold reference proteomes (~23M)",
    "pdb100": "PDB 100% identity clustered (~340K)",
    "mgnify_esm30": "ESM Metagenomic Atlas (~200M)",
    "gmgcl_id": "Global Microbial Gene Catalog",
}

# Default databases for quick searches
DEFAULT_DATABASES = ["afdb50", "pdb100"]


@dataclass
class FoldseekHit:
    """A single Foldseek alignment hit."""

    query: str
    target: str
    identity: float
    alignment_length: int
    mismatches: int
    gap_opens: int
    query_start: int
    query_end: int
    target_start: int
    target_end: int
    evalue: float
    bitscore: float
    database: str = ""

    @property
    def uniprot_id(self) -> str | None:
        """Extract UniProt accession if present."""
        match = re.search(r"AF-([A-Z0-9]+)-F\d+", self.target)
        return match.group(1) if match else None

    @property
    def pdb_id(self) -> str | None:
        """Extract PDB ID if present."""
        match = re.search(r"^(\w{4})_(\w)$", self.target)
        return match.group(1) if match else None

    def matches_pattern(self, pattern: str) -> bool:
        """Check if target matches exclusion pattern."""
        return pattern.lower() in self.target.lower()


def parse_m8(content: str, database: str = "") -> list[FoldseekHit]:
    """
    Parse Foldseek m8 (BLAST tabular) format.

    Args:
        content: TSV content from m8 file
        database: Database name to tag hits with

    Returns:
        List of FoldseekHit objects
    """
    hits = []
    for line in content.strip().split("\n"):
        if not line or line.startswith("#"):
            continue
        fields = line.split("\t")
        if len(fields) >= 12:
            hits.append(
                FoldseekHit(
                    query=fields[0],
                    target=fields[1],
                    identity=float(fields[2]),
                    alignment_length=int(fields[3]),
                    mismatches=int(fields[4]),
                    gap_opens=int(fields[5]),
                    query_start=int(fields[6]),
                    query_end=int(fields[7]),
                    target_start=int(fields[8]),
                    target_end=int(fields[9]),
                    evalue=float(fields[10]),
                    bitscore=float(fields[11]),
                    database=database,
                )
            )
    return hits


def search(
    pdb_path: str,
    databases: list[str] | None = None,
    mode: str = "3diaa",
    max_attempts: int = 20,
    poll_interval: int = 30,
    exclude_pattern: str | None = None,
    verbose: bool = True,
) -> dict[str, list[FoldseekHit]]:
    """
    Submit a structure to Foldseek and get results.

    Args:
        pdb_path: Path to PDB file
        databases: List of databases to search (default: afdb50, pdb100)
        mode: "3diaa" (fast) or "tmalign" (sensitive)
        max_attempts: Maximum polling attempts (default: 20 = 10 minutes)
        poll_interval: Seconds between status checks (default: 30)
        exclude_pattern: Pattern to filter from results (e.g., "TEP1", "Q99973")
        verbose: Print progress messages

    Returns:
        Dict mapping database names to lists of FoldseekHit objects

    Raises:
        Exception: On API errors, rate limiting, or timeout
    """
    if databases is None:
        databases = DEFAULT_DATABASES

    # Validate databases
    for db in databases:
        if db not in DATABASES:
            raise ValueError(f"Unknown database: {db}. Available: {list(DATABASES.keys())}")

    # Submit job
    with open(pdb_path, "rb") as f:
        response = requests.post(
            f"{API_BASE}/ticket",
            files={"q": f},
            data=[("mode", mode)] + [("database[]", db) for db in databases],
        )

    if response.status_code == 429:
        raise Exception("Rate limited by Foldseek. Wait 5-10 minutes and retry.")

    if response.status_code != 200:
        raise Exception(f"API error: {response.status_code} - {response.text}")

    result = response.json()
    ticket_id = result["id"]
    if verbose:
        print(f"Submitted job: {ticket_id}")

    # Poll for completion
    for attempt in range(max_attempts):
        status_response = requests.get(f"{API_BASE}/ticket/{ticket_id}")
        status = status_response.json()

        if status["status"] == "COMPLETE":
            if verbose:
                print("Search complete!")
            break
        elif status["status"] == "ERROR":
            raise Exception(f"Foldseek error: {status}")

        if verbose:
            print(f"Status: {status['status']} (attempt {attempt + 1}/{max_attempts})")
        time.sleep(poll_interval)
    else:
        raise Exception(f"Timeout after {max_attempts * poll_interval} seconds")

    # Download results
    result_response = requests.get(f"{API_BASE}/result/download/{ticket_id}")

    # Parse tar.gz results
    results: dict[str, list[FoldseekHit]] = {}
    with tarfile.open(fileobj=io.BytesIO(result_response.content), mode="r:gz") as tar:
        for member in tar.getmembers():
            if member.name.endswith(".m8"):
                content = tar.extractfile(member).read().decode()
                # Extract database name from path (e.g., "afdb50/alis_pdb.m8")
                db_name = member.name.split("/")[0]
                hits = parse_m8(content, database=db_name)

                # Apply exclusion filter
                if exclude_pattern:
                    hits = [h for h in hits if not h.matches_pattern(exclude_pattern)]

                results[db_name] = hits

    return results


def search_batch(
    pdb_paths: list[str],
    databases: list[str] | None = None,
    mode: str = "3diaa",
    exclude_pattern: str | None = None,
    delay: int = 5,
    verbose: bool = True,
) -> dict[str, dict[str, list[FoldseekHit]]]:
    """
    Search multiple PDB files sequentially.

    Args:
        pdb_paths: List of paths to PDB files
        databases: Databases to search
        mode: Alignment mode
        exclude_pattern: Pattern to filter from results
        delay: Seconds to wait between searches (rate limiting)
        verbose: Print progress

    Returns:
        Dict mapping filename to search results
    """
    all_results = {}

    for i, pdb_path in enumerate(pdb_paths):
        name = Path(pdb_path).stem
        if verbose:
            print(f"\n[{i + 1}/{len(pdb_paths)}] Searching {name}...")

        try:
            results = search(
                pdb_path,
                databases=databases,
                mode=mode,
                exclude_pattern=exclude_pattern,
                verbose=verbose,
            )
            all_results[name] = results
        except Exception as e:
            print(f"Error searching {name}: {e}")
            all_results[name] = {"error": str(e)}

        # Rate limiting delay between searches
        if i < len(pdb_paths) - 1:
            if verbose:
                print(f"Waiting {delay}s before next search...")
            time.sleep(delay)

    return all_results


def summarize_results(
    results: dict[str, list[FoldseekHit]],
    top_n: int = 10,
    evalue_threshold: float = 1e-3,
) -> None:
    """
    Print a summary of search results.

    Args:
        results: Dict from search()
        top_n: Number of top hits to show per database
        evalue_threshold: Only show hits below this E-value
    """
    for db, hits in results.items():
        significant = [h for h in hits if h.evalue < evalue_threshold]
        print(f"\n=== {db} ({len(significant)} significant hits) ===")

        for hit in significant[:top_n]:
            uniprot = f" [UniProt: {hit.uniprot_id}]" if hit.uniprot_id else ""
            pdb = f" [PDB: {hit.pdb_id}]" if hit.pdb_id else ""
            print(f"  {hit.target}{uniprot}{pdb}")
            print(f"    E-value: {hit.evalue:.2e}, Identity: {hit.identity:.1f}%")


if __name__ == "__main__":
    # Example usage
    import sys

    if len(sys.argv) < 2:
        print("Usage: python foldseek_client.py <pdb_file> [exclude_pattern]")
        print("\nAvailable databases:")
        for db, desc in DATABASES.items():
            print(f"  {db}: {desc}")
        sys.exit(1)

    pdb_file = sys.argv[1]
    exclude = sys.argv[2] if len(sys.argv) > 2 else None

    results = search(pdb_file, exclude_pattern=exclude)
    summarize_results(results)
