"""
HMMER Web Service client for protein homology search and domain annotation.

This module provides a Python interface to the EBI HMMER REST API v1 at
https://www.ebi.ac.uk/Tools/hmmer/api/v1/. Supports all four HMMER algorithms:
phmmer, hmmscan, hmmsearch, and jackhmmer.
"""

import argparse
import time
from dataclasses import dataclass, field
from typing import Any

import requests

API_BASE = "https://www.ebi.ac.uk/Tools/hmmer/api/v1"

ALGORITHMS = ["phmmer", "hmmscan", "hmmsearch", "jackhmmer"]

# Sequence databases (for phmmer, hmmsearch, jackhmmer)
SEQUENCE_DATABASES = {
    "refprot": "Reference Proteomes (default)",
    "uniprot": "Full UniProt",
    "swissprot": "SwissProt — manually reviewed, high quality",
    "pdb": "PDB — sequences with solved structures",
    "rp15": "Representative Proteomes 15% co-membership",
    "rp35": "Representative Proteomes 35%",
    "rp55": "Representative Proteomes 55%",
    "rp75": "Representative Proteomes 75%",
}

# Profile HMM databases (for hmmscan)
HMM_DATABASES = {
    "pfam": "Pfam protein families (default)",
}

# Default databases per algorithm
DEFAULT_DATABASES = {
    "phmmer": "refprot",
    "hmmscan": "pfam",
    "hmmsearch": "refprot",
    "jackhmmer": "refprot",
}


@dataclass
class HmmerDomain:
    """A single domain hit within a sequence match."""

    ienv: int
    jenv: int
    iali: int
    jali: int
    bitscore: float
    cevalue: float
    ievalue: float
    bias: float = 0.0
    alimodel: str = ""
    alimline: str = ""
    aliaseq: str = ""

    @property
    def alignment_length(self) -> int:
        return self.jali - self.iali + 1

    @property
    def envelope_length(self) -> int:
        return self.jenv - self.ienv + 1


@dataclass
class HmmerHit:
    """A single HMMER sequence hit."""

    name: str
    acc: str
    desc: str
    evalue: float
    score: float
    bias: float
    ndom: int
    domains: list[HmmerDomain] = field(default_factory=list)

    @classmethod
    def from_api(cls, hit_data: dict) -> "HmmerHit":
        """Parse a hit from the API JSON response."""
        domains = []
        for dom in hit_data.get("domains", []):
            domains.append(
                HmmerDomain(
                    ienv=dom.get("ienv", 0),
                    jenv=dom.get("jenv", 0),
                    iali=dom.get("iali", 0),
                    jali=dom.get("jali", 0),
                    bitscore=dom.get("bitscore", 0.0),
                    cevalue=dom.get("cevalue", 0.0),
                    ievalue=dom.get("ievalue", 0.0),
                    bias=dom.get("bias", 0.0),
                    alimodel=dom.get("alimodel", ""),
                    alimline=dom.get("alimline", ""),
                    aliaseq=dom.get("aliaseq", ""),
                )
            )
        return cls(
            name=hit_data.get("name", ""),
            acc=hit_data.get("acc", ""),
            desc=hit_data.get("desc", ""),
            evalue=hit_data.get("evalue", 999.0),
            score=hit_data.get("score", 0.0),
            bias=hit_data.get("bias", 0.0),
            ndom=hit_data.get("ndom", 0),
            domains=domains,
        )


def search(
    algo: str,
    input_data: str,
    database: str | None = None,
    max_attempts: int = 60,
    poll_interval: int = 5,
    verbose: bool = True,
    **params: Any,
) -> dict:
    """
    Submit an HMMER search and return results.

    Args:
        algo: Algorithm — "phmmer", "hmmscan", "hmmsearch", or "jackhmmer"
        input_data: Protein sequence (FASTA or raw), MSA, or HMM profile
        database: Target database name (defaults vary by algorithm)
        max_attempts: Maximum polling attempts before timeout
        poll_interval: Seconds between status checks
        verbose: Print progress messages
        **params: Additional API parameters (E, domE, incE, incdomE, popen, pextend, mx, iterations)

    Returns:
        Parsed JSON response dict with "result" containing "stats" and "hits"

    Raises:
        ValueError: Invalid algorithm or database
        RuntimeError: API errors or timeout
    """
    if algo not in ALGORITHMS:
        raise ValueError(f"Unknown algorithm: {algo}. Must be one of {ALGORITHMS}")

    if database is None:
        database = DEFAULT_DATABASES[algo]

    # Validate database
    valid_dbs = HMM_DATABASES if algo == "hmmscan" else SEQUENCE_DATABASES
    if database not in valid_dbs:
        raise ValueError(
            f"Unknown database '{database}' for {algo}. Available: {list(valid_dbs.keys())}"
        )

    # Build JSON request body
    body: dict[str, Any] = {
        "input": input_data,
        "database": database,
    }
    # Add optional parameters
    for key, value in params.items():
        if value is not None:
            body[key] = value

    # Submit search
    url = f"{API_BASE}/search/{algo}"
    headers = {"Accept": "application/json", "Content-Type": "application/json"}

    if verbose:
        print(f"Submitting {algo} search against {database}...")

    response = requests.post(url, json=body, headers=headers, timeout=120)

    if response.status_code != 200:
        raise RuntimeError(f"HMMER API error: HTTP {response.status_code} — {response.text[:500]}")

    data = response.json()
    job_id = data.get("id")
    if not job_id:
        raise RuntimeError(f"No job ID in response: {data}")

    if verbose:
        print(f"Job submitted: {job_id}")

    # Poll for completion
    return _poll_results(job_id, max_attempts, poll_interval, verbose)


def _poll_results(
    job_id: str,
    max_attempts: int,
    poll_interval: int,
    verbose: bool,
) -> dict:
    """Poll for job completion and return results."""
    status_url = f"{API_BASE}/search/{job_id}"
    results_url = f"{API_BASE}/result/{job_id}"
    headers = {"Accept": "application/json"}

    for attempt in range(max_attempts):
        # Check job status
        response = requests.get(status_url, headers=headers, timeout=60)

        if response.status_code != 200:
            if response.status_code >= 500:
                if verbose:
                    print(f"  Server error ({response.status_code}), retrying...")
                time.sleep(poll_interval)
                continue
            if response.status_code == 404 and attempt < 5:
                time.sleep(poll_interval)
                continue
            raise RuntimeError(
                f"Status check failed: HTTP {response.status_code} — {response.text[:500]}"
            )

        data = response.json()
        task = data.get("task", {})
        status = task.get("status", data.get("status", ""))

        if status == "SUCCESS":
            if verbose:
                print("Search complete!")
            # Fetch full results
            result_response = requests.get(results_url, headers=headers, timeout=60)
            if result_response.status_code == 200:
                return result_response.json()
            # Fall back to the status response if it contains results
            if "result" in data:
                return data
            raise RuntimeError(f"Failed to fetch results: HTTP {result_response.status_code}")

        if status == "FAILURE":
            raise RuntimeError(f"HMMER search failed: {data}")

        if verbose:
            print(f"  Status: {status} (attempt {attempt + 1}/{max_attempts})")
        time.sleep(poll_interval)

    raise RuntimeError(
        f"Timeout after {max_attempts * poll_interval}s waiting for HMMER results (job: {job_id})"
    )


def _extract_hits(results: dict) -> list[HmmerHit]:
    """Extract HmmerHit objects from API response.

    The API returns results under "result.hits" or sometimes directly under "hits".
    """
    # Try result.hits (standard v1 API response)
    result = results.get("result", {})
    if isinstance(result, dict):
        hits_data = result.get("hits", [])
        if hits_data:
            return [HmmerHit.from_api(h) for h in hits_data]

    # Fall back to top-level hits
    hits_data = results.get("hits", [])
    return [HmmerHit.from_api(h) for h in hits_data]


# ─── Convenience wrappers ────────────────────────────────────────────────────


def phmmer(
    sequence: str,
    database: str = "refprot",
    verbose: bool = True,
    **params: Any,
) -> dict:
    """
    Search a protein sequence against a sequence database.

    Args:
        sequence: Protein sequence (FASTA or raw amino acids)
        database: Target database (default: refprot)
        verbose: Print progress
        **params: Additional parameters (E, domE, etc.)

    Returns:
        API response dict with hits
    """
    return search("phmmer", sequence, database=database, verbose=verbose, **params)


def hmmscan(
    sequence: str,
    database: str = "pfam",
    verbose: bool = True,
    **params: Any,
) -> dict:
    """
    Search a protein sequence against profile HMM databases (e.g., Pfam).

    Args:
        sequence: Protein sequence (FASTA or raw amino acids)
        database: HMM database (default: pfam)
        verbose: Print progress
        **params: Additional parameters

    Returns:
        API response dict with domain hits
    """
    return search("hmmscan", sequence, database=database, verbose=verbose, **params)


def hmmsearch(
    alignment_or_hmm: str,
    database: str = "refprot",
    verbose: bool = True,
    **params: Any,
) -> dict:
    """
    Search a profile (MSA or HMM) against a sequence database.

    Args:
        alignment_or_hmm: Multiple sequence alignment or HMMER3-format HMM
        database: Target sequence database (default: refprot)
        verbose: Print progress
        **params: Additional parameters

    Returns:
        API response dict with hits
    """
    return search("hmmsearch", alignment_or_hmm, database=database, verbose=verbose, **params)


def jackhmmer(
    sequence: str,
    database: str = "refprot",
    iterations: int = 5,
    verbose: bool = True,
    **params: Any,
) -> dict:
    """
    Iterative search — finds remote homologs by refining a profile over iterations.

    Args:
        sequence: Protein sequence (FASTA or raw amino acids)
        database: Target database (default: refprot)
        iterations: Number of iterations (default: 5)
        verbose: Print progress
        **params: Additional parameters

    Returns:
        API response dict with hits
    """
    return search(
        "jackhmmer",
        sequence,
        database=database,
        iterations=iterations,
        verbose=verbose,
        **params,
    )


def get_domain_annotations(
    sequence: str,
    database: str = "pfam",
    evalue_threshold: float = 1e-3,
    verbose: bool = False,
) -> list[dict]:
    """
    Quick helper: annotate domains in a protein sequence using hmmscan.

    Args:
        sequence: Protein sequence
        database: HMM database (default: pfam)
        evalue_threshold: Only return domains below this E-value
        verbose: Print progress

    Returns:
        List of domain annotation dicts with name, acc, description,
        evalue, score, ali_from, ali_to, env_from, env_to
    """
    results = hmmscan(sequence, database=database, verbose=verbose)
    hits = _extract_hits(results)

    annotations = []
    for hit in hits:
        if hit.evalue > evalue_threshold:
            continue
        for dom in hit.domains:
            if dom.ievalue > evalue_threshold:
                continue
            annotations.append(
                {
                    "name": hit.name,
                    "acc": hit.acc,
                    "description": hit.desc,
                    "evalue": hit.evalue,
                    "score": hit.score,
                    "domain_evalue": dom.ievalue,
                    "domain_score": dom.bitscore,
                    "ali_from": dom.iali,
                    "ali_to": dom.jali,
                    "env_from": dom.ienv,
                    "env_to": dom.jenv,
                }
            )

    return sorted(annotations, key=lambda x: x["domain_evalue"])


def summarize_results(results: dict, top_n: int = 20, evalue_threshold: float = 10.0) -> None:
    """
    Print a summary of HMMER search results.

    Args:
        results: Response dict from search()
        top_n: Number of top hits to display
        evalue_threshold: Only show hits below this E-value
    """
    hits = _extract_hits(results)
    significant = [h for h in hits if h.evalue <= evalue_threshold]

    # Stats may be under result.stats or top-level stats
    result = results.get("result", results)
    stats = result.get("stats", {})
    nhits = stats.get("nhits", len(hits))
    print(f"\n{'=' * 70}")
    print(f"HMMER Results: {nhits} total hits, {len(significant)} shown (E <= {evalue_threshold})")
    print(f"{'=' * 70}")

    for i, hit in enumerate(significant[:top_n], 1):
        print(f"\n{i:3d}. {hit.name}")
        if hit.acc:
            print(f"     Accession: {hit.acc}")
        if hit.desc:
            print(f"     {hit.desc}")
        print(
            f"     E-value: {hit.evalue:.2e}  Score: {hit.score:.1f}  Bias: {hit.bias:.1f}  Domains: {hit.ndom}"
        )

        for j, dom in enumerate(hit.domains, 1):
            print(
                f"       Domain {j}: ali {dom.iali}-{dom.jali}, "
                f"env {dom.ienv}-{dom.jenv}, "
                f"score {dom.bitscore:.1f}, "
                f"cE {dom.cevalue:.2e}, iE {dom.ievalue:.2e}"
            )

    if len(significant) > top_n:
        print(f"\n... and {len(significant) - top_n} more hits (use top_n to show more)")


def get_databases(algo: str = "phmmer") -> dict[str, str]:
    """
    Return available databases for a given algorithm.

    Args:
        algo: Algorithm name

    Returns:
        Dict mapping database ID to description
    """
    if algo == "hmmscan":
        return dict(HMM_DATABASES)
    return dict(SEQUENCE_DATABASES)


# ─── CLI entry point ─────────────────────────────────────────────────────────


def main() -> None:
    parser = argparse.ArgumentParser(description="HMMER Web Service client")
    parser.add_argument(
        "--algo",
        choices=ALGORITHMS,
        default="phmmer",
        help="HMMER algorithm (default: phmmer)",
    )
    parser.add_argument("--sequence", help="Protein sequence (raw amino acids or FASTA)")
    parser.add_argument("--input-file", help="Read sequence/MSA/HMM from file")
    parser.add_argument("--database", help="Target database (default depends on algorithm)")
    parser.add_argument(
        "--iterations", type=int, default=5, help="Jackhmmer iterations (default: 5)"
    )
    parser.add_argument("--evalue", type=float, help="E-value threshold for reporting")
    parser.add_argument(
        "--top-n", type=int, default=20, help="Number of top hits to show (default: 20)"
    )
    parser.add_argument(
        "--list-databases",
        action="store_true",
        help="List available databases and exit",
    )
    parser.add_argument("--quiet", action="store_true", help="Suppress progress messages")

    args = parser.parse_args()

    if args.list_databases:
        print("Sequence databases (phmmer, hmmsearch, jackhmmer):")
        for db_id, desc in SEQUENCE_DATABASES.items():
            print(f"  {db_id:20s} {desc}")
        print("\nHMM databases (hmmscan):")
        for db_id, desc in HMM_DATABASES.items():
            print(f"  {db_id:20s} {desc}")
        return

    # Get input data
    input_data = args.sequence
    if args.input_file:
        with open(args.input_file) as f:
            input_data = f.read().strip()
    if not input_data:
        parser.error("Provide --sequence or --input-file")

    # Build search params
    extra_params: dict[str, Any] = {}
    if args.evalue is not None:
        extra_params["E"] = args.evalue
        extra_params["domE"] = args.evalue
    if args.algo == "jackhmmer":
        extra_params["iterations"] = args.iterations

    # Run search
    results = search(
        algo=args.algo,
        input_data=input_data,
        database=args.database,
        verbose=not args.quiet,
        **extra_params,
    )

    # Display results
    summarize_results(results, top_n=args.top_n)


if __name__ == "__main__":
    main()
