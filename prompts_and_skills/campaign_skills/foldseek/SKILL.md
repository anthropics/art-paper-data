---
name: foldseek
description: Fast protein structure search using Foldseek. Search PDB files against AlphaFold DB, PDB100, and other structural databases to find remote homologs. Supports both web API (quick searches) and local CLI (batch operations).
---

# Foldseek Skill

Foldseek enables fast structural similarity searches, finding remote homologs that sequence-based methods miss. It encodes structures as 3Di alphabet sequences for rapid comparison.

## Quick Reference

| Method    | Best For                               | Setup Required    |
| --------- | -------------------------------------- | ----------------- |
| Web API   | Quick single searches, no setup        | None              |
| Local CLI | Batch operations, large-scale searches | Database download |

## Web API (Recommended for Quick Searches)

The Foldseek web server at `search.foldseek.com` provides free API access.

### Submit a Search

```python
import requests
import time
import tarfile
import io
import json

def foldseek_search(pdb_path: str, databases: list[str] = None, mode: str = "3diaa") -> dict:
    """
    Submit a structure to Foldseek and get results.

    Args:
        pdb_path: Path to PDB file
        databases: List of databases to search. Options:
            - "afdb50" (AlphaFold DB 50% clustered - recommended)
            - "afdb-swissprot" (AlphaFold Swiss-Prot)
            - "afdb-proteome" (AlphaFold proteomes)
            - "pdb100" (PDB 100% identity clustered)
            - "mgnify_esm30" (ESM Metagenomic Atlas)
            - "gmgcl_id" (Global Microbial Gene Catalog)
        mode: "3diaa" (fast, default) or "tmalign" (slower, more sensitive)

    Returns:
        Dict with hits per database
    """
    API_BASE = "https://search.foldseek.com/api"

    if databases is None:
        databases = ["afdb50", "pdb100"]

    # Submit job
    with open(pdb_path, "rb") as f:
        files = {"q": f}
        data = {"mode": mode}
        for db in databases:
            data.setdefault("database[]", []).append(db)

        # Handle multiple database[] params
        response = requests.post(
            f"{API_BASE}/ticket",
            files=files,
            data=[("mode", mode)] + [("database[]", db) for db in databases]
        )

    if response.status_code == 429:
        raise Exception("Rate limited. Wait a few minutes and retry.")

    result = response.json()
    ticket_id = result["id"]
    print(f"Submitted job: {ticket_id}")

    # Poll for completion
    for attempt in range(20):  # 10 minutes max
        status = requests.get(f"{API_BASE}/ticket/{ticket_id}").json()
        if status["status"] == "COMPLETE":
            break
        elif status["status"] == "ERROR":
            raise Exception(f"Foldseek error: {status}")
        print(f"Status: {status['status']} (attempt {attempt + 1})")
        time.sleep(30)
    else:
        raise Exception("Timeout waiting for results")

    # Download results
    result_response = requests.get(f"{API_BASE}/result/download/{ticket_id}")

    # Parse tar.gz results
    results = {}
    with tarfile.open(fileobj=io.BytesIO(result_response.content), mode="r:gz") as tar:
        for member in tar.getmembers():
            if member.name.endswith(".m8"):
                # TSV format with alignments
                content = tar.extractfile(member).read().decode()
                db_name = member.name.split("/")[0]
                results[db_name] = parse_m8(content)

    return results


def parse_m8(content: str) -> list[dict]:
    """Parse Foldseek m8 (BLAST tabular) format."""
    hits = []
    for line in content.strip().split("\n"):
        if not line or line.startswith("#"):
            continue
        fields = line.split("\t")
        if len(fields) >= 12:
            hits.append({
                "query": fields[0],
                "target": fields[1],
                "identity": float(fields[2]),
                "alignment_length": int(fields[3]),
                "mismatches": int(fields[4]),
                "gap_opens": int(fields[5]),
                "query_start": int(fields[6]),
                "query_end": int(fields[7]),
                "target_start": int(fields[8]),
                "target_end": int(fields[9]),
                "evalue": float(fields[10]),
                "bitscore": float(fields[11]),
            })
    return hits
```

### Example: Search a Domain

```python
# Search a single domain
results = foldseek_search("domain_4_4_TROVE.pdb", databases=["afdb50", "pdb100"])

# Filter out self-hits (e.g., TEP1)
for db, hits in results.items():
    print(f"\n=== {db} ===")
    for hit in hits[:10]:
        # Skip TEP1 hits
        if "TEP1" in hit["target"] or "Q99973" in hit["target"]:
            continue
        print(f"{hit['target']}: E={hit['evalue']:.2e}, identity={hit['identity']:.1f}%")
```

### Batch Search Multiple Domains

```python
import asyncio
from pathlib import Path

async def search_all_domains(domain_dir: str, exclude_pattern: str = None) -> dict:
    """Search all domain PDB files and aggregate results."""
    all_results = {}

    for pdb_file in Path(domain_dir).glob("domain_*.pdb"):
        domain_name = pdb_file.stem
        print(f"\nSearching {domain_name}...")

        try:
            results = foldseek_search(str(pdb_file))

            # Filter excluded patterns
            if exclude_pattern:
                for db in results:
                    results[db] = [h for h in results[db]
                                   if exclude_pattern not in h["target"]]

            all_results[domain_name] = results
        except Exception as e:
            print(f"Error searching {domain_name}: {e}")
            all_results[domain_name] = {"error": str(e)}

        # Rate limiting - be nice to the server
        await asyncio.sleep(5)

    return all_results

# Run batch search
results = asyncio.run(search_all_domains("/workspace", exclude_pattern="TEP1"))
```

## Local CLI (For Batch/Offline Use)

For large-scale searches, install Foldseek locally.

### Installation

```bash
# Download latest release
wget https://mmseqs.com/foldseek/foldseek-linux-avx2.tar.gz
tar xzf foldseek-linux-avx2.tar.gz
export PATH="$(pwd)/foldseek/bin:$PATH"

# Or use conda
conda install -c conda-forge -c bioconda foldseek
```

### Download Databases

```bash
# PDB100 (~2GB) - fast
foldseek databases PDB100 pdb100_db tmp

# AlphaFold DB 50% (~35GB) - comprehensive
foldseek databases Alphafold/UniProt50 afdb50_db tmp

# Swiss-Prot subset (~1GB) - curated
foldseek databases Alphafold/Swiss-Prot afdb_swissprot_db tmp
```

### Search Command

```bash
# Basic search
foldseek easy-search query.pdb pdb100_db result.m8 tmp

# With HTML output
foldseek easy-search query.pdb pdb100_db result.html tmp --format-mode 3

# Multiple queries
foldseek easy-search domains/ pdb100_db results/ tmp

# Sensitive search (slower)
foldseek easy-search query.pdb afdb50_db result.m8 tmp \
    --alignment-type 2 \
    -e 0.001 \
    --max-seqs 1000
```

### Output Formats

| Format   | Flag              | Description               |
| -------- | ----------------- | ------------------------- |
| m8 (TSV) | default           | BLAST tabular format      |
| HTML     | `--format-mode 3` | Interactive visualization |
| JSON     | `--format-mode 4` | Structured data           |

### Parse Local Results

```python
def parse_foldseek_results(m8_file: str) -> list[dict]:
    """Parse local Foldseek m8 output."""
    return parse_m8(open(m8_file).read())

# Example
hits = parse_foldseek_results("result.m8")
for hit in hits[:10]:
    print(f"{hit['target']}: E={hit['evalue']:.2e}")
```

## Interpreting Results

### Key Metrics

| Metric       | Good Value | Meaning                  |
| ------------ | ---------- | ------------------------ |
| E-value      | < 1e-5     | Statistical significance |
| 3Di identity | > 30%      | Structural similarity    |
| TM-score     | > 0.5      | Same fold                |
| Coverage     | > 70%      | Extent of alignment      |

### Extracting Functional Annotations

```python
import re

def extract_uniprot_info(target_id: str) -> dict:
    """Extract UniProt accession from Foldseek hit ID."""
    # Format: AF-P12345-F1-model_v4 or AFDB:AF-P12345-F1
    match = re.search(r"AF-([A-Z0-9]+)-F\d+", target_id)
    if match:
        return {"uniprot": match.group(1), "source": "alphafold"}

    # PDB format: 1abc_A
    match = re.search(r"^(\w{4})_(\w)$", target_id)
    if match:
        return {"pdb": match.group(1), "chain": match.group(2), "source": "pdb"}

    return {"raw": target_id}


def annotate_hits(hits: list[dict]) -> list[dict]:
    """Add UniProt/PDB annotations to hits."""
    for hit in hits:
        hit["annotation"] = extract_uniprot_info(hit["target"])
    return hits
```

## Common Patterns

### Domain Function Inference

```python
def infer_domain_function(domain_hits: dict, exclude_terms: list[str] = None) -> str:
    """Synthesize functional inference from structural homologs."""
    from collections import Counter

    exclude_terms = exclude_terms or []
    all_targets = []

    for db, hits in domain_hits.items():
        for hit in hits:
            # Skip excluded terms (e.g., the query protein itself)
            target = hit["target"]
            if any(term in target for term in exclude_terms):
                continue
            if hit["evalue"] < 1e-3:  # Significant hits only
                all_targets.append(target)

    # Count most common protein families
    families = Counter()
    for target in all_targets:
        # Extract protein name/family from ID
        info = extract_uniprot_info(target)
        families[info.get("uniprot", target)] += 1

    return families.most_common(10)
```

### Multi-Domain Protein Analysis

```python
def analyze_multidomain_protein(domain_results: dict,
                                 exclude_self: str = None) -> dict:
    """
    Analyze a multi-domain protein by searching each domain separately
    and synthesizing functional annotations.

    Args:
        domain_results: Dict mapping domain names to Foldseek results
        exclude_self: Pattern to exclude (e.g., "Q99973" for TEP1)

    Returns:
        Summary with per-domain and whole-protein annotations
    """
    summary = {"domains": {}, "synthesis": []}

    for domain, results in domain_results.items():
        if "error" in results:
            summary["domains"][domain] = {"status": "error", "message": results["error"]}
            continue

        # Aggregate hits across databases
        all_hits = []
        for db, hits in results.items():
            for hit in hits:
                if exclude_self and exclude_self in hit["target"]:
                    continue
                hit["database"] = db
                all_hits.append(hit)

        # Sort by E-value
        all_hits.sort(key=lambda x: x["evalue"])

        summary["domains"][domain] = {
            "top_hits": all_hits[:5],
            "hit_count": len(all_hits),
            "best_evalue": all_hits[0]["evalue"] if all_hits else None,
        }

    return summary
```

## Databases Reference

| Database       | Size             | Description                    |
| -------------- | ---------------- | ------------------------------ |
| pdb100         | ~340K structures | PDB clustered at 100% identity |
| afdb50         | ~54M structures  | AlphaFold DB clustered at 50%  |
| afdb-swissprot | ~540K structures | AlphaFold Swiss-Prot subset    |
| afdb-proteome  | ~23M structures  | AlphaFold reference proteomes  |
| mgnify_esm30   | ~200M structures | ESM Metagenomic Atlas          |

## Troubleshooting

| Issue               | Solution                                               |
| ------------------- | ------------------------------------------------------ |
| Rate limited (429)  | Wait 5-10 minutes, reduce batch size                   |
| Timeout             | Increase polling attempts, use smaller databases       |
| No hits             | Try TM-align mode (`mode="tmalign"`), expand databases |
| Memory issues (CLI) | Use `--sort-by-structure-bits 0`, reduce threads       |
