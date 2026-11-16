# EBI HMMER Web Service API Reference

Base URL: `https://www.ebi.ac.uk/Tools/hmmer/api/v1`

## Endpoints

### Submit Search

```
POST /search/{algo}
```

Where `{algo}` is one of: `phmmer`, `hmmscan`, `hmmsearch`, `jackhmmer`.

**Content-Type**: `application/json`

**Headers**:

- `Accept: application/json`
- `Content-Type: application/json`

**Request body** (JSON):

```json
{
  "input": "MKWMFKEDHSLEHR...",
  "database": "pfam"
}
```

**Response** (200):

```json
{
  "id": "4cf6d4f2-98a6-4fd2-a3f2-92e8afc0fc3d"
}
```

### Check Job Status

```
GET /search/{job_id}
```

**Response** (200):

```json
{
  "task": {
    "status": "SUCCESS",
    "date_created": "2026-02-10T05:09:06.776Z",
    "date_done": "2026-02-10T05:09:06.917Z"
  },
  "id": "4cf6d4f2-...",
  "algo": "hmmscan",
  "database": { "id": "pfam", "type": "hmm", "name": "Pfam", "version": "37.2" }
}
```

Task status values: `PENDING`, `STARTED`, `SUCCESS`, `FAILURE`

### Get Results

```
GET /result/{job_id}
```

**Response** (200):

```json
{
  "status": "SUCCESS",
  "result": {
    "stats": { ... },
    "hits": [ ... ]
  },
  "page_count": 1
}
```

### List Available Databases

```
GET /search/databases
```

Returns array of database objects with `id`, `type` ("seq" or "hmm"), `name`, `version`.

## Request Parameters

### Common Parameters (all algorithms)

| Parameter  | Type   | Default      | Description                                                           |
| ---------- | ------ | ------------ | --------------------------------------------------------------------- |
| `input`    | string | **required** | Protein sequence (FASTA or raw), MSA, or HMM profile                  |
| `database` | string | varies       | Target database ID                                                    |
| `E`        | float  | 1.0          | Sequence E-value reporting threshold                                  |
| `domE`     | float  | 1.0          | Domain E-value reporting threshold                                    |
| `incE`     | float  | 0.01         | Sequence E-value inclusion threshold                                  |
| `incdomE`  | float  | 0.03         | Domain E-value inclusion threshold                                    |
| `popen`    | float  | 0.02         | Gap open probability                                                  |
| `pextend`  | float  | 0.4          | Gap extend probability                                                |
| `mx`       | string | BLOSUM62     | Scoring matrix (BLOSUM45, BLOSUM62, BLOSUM80, BLOSUM90, PAM30, PAM70) |

### Algorithm-Specific Parameters

| Parameter    | Algorithm | Type | Description                 |
| ------------ | --------- | ---- | --------------------------- |
| `iterations` | jackhmmer | int  | Number of search iterations |

## Available Databases

Retrieved from `GET /search/databases`:

### Sequence Databases (phmmer, hmmsearch, jackhmmer)

| ID          | Description                   |
| ----------- | ----------------------------- |
| `refprot`   | Reference Proteomes (default) |
| `uniprot`   | Full UniProt                  |
| `swissprot` | SwissProt (manually reviewed) |
| `pdb`       | PDB sequences                 |
| `rp15`      | Representative Proteomes 15%  |
| `rp35`      | Representative Proteomes 35%  |
| `rp55`      | Representative Proteomes 55%  |
| `rp75`      | Representative Proteomes 75%  |

### Profile HMM Databases (hmmscan)

| ID     | Description                  |
| ------ | ---------------------------- |
| `pfam` | Pfam protein family profiles |

## Response Schema

### Result Wrapper

```json
{
  "status": "SUCCESS",
  "result": {
    "stats": {
      "nhits": 42,
      "Z": 100000,
      "domZ": 100000
    },
    "hits": [ ... ]
  },
  "page_count": 1
}
```

| Field                | Type   | Description                         |
| -------------------- | ------ | ----------------------------------- |
| `status`             | string | Job status ("SUCCESS")              |
| `result.stats.nhits` | int    | Total number of hits                |
| `result.stats.Z`     | int    | Effective database size (sequences) |
| `result.stats.domZ`  | int    | Effective database size (domains)   |
| `result.hits`        | array  | Array of hit objects                |

### Hit Object

```json
{
  "name": "sp|P12345|EXAMPLE_HUMAN",
  "acc": "P12345",
  "desc": "Example protein OS=Homo sapiens",
  "evalue": 1.2e-72,
  "pvalue": 5.6e-78,
  "score": 245.3,
  "bias": 3.2,
  "ndom": 2,
  "domains": [ ... ]
}
```

| Field     | Type   | Description                                                |
| --------- | ------ | ---------------------------------------------------------- |
| `name`    | string | Target sequence name                                       |
| `acc`     | string | Accession identifier (UniProt, Pfam, etc.)                 |
| `desc`    | string | Sequence/family description                                |
| `evalue`  | float  | E-value of the overall sequence score                      |
| `pvalue`  | float  | P-value                                                    |
| `score`   | float  | Bit score (sum over all domains, without null2 correction) |
| `bias`    | float  | Composition bias correction                                |
| `ndom`    | int    | Number of domains found                                    |
| `domains` | array  | Array of domain match objects                              |

### Domain Object

```json
{
  "ienv": 1,
  "jenv": 150,
  "iali": 5,
  "jali": 148,
  "bitscore": 120.5,
  "cevalue": 3.4e-35,
  "ievalue": 6.8e-35,
  "bias": 0.5,
  "alimodel": "alignment string...",
  "alimline": "match line...",
  "aliaseq": "target alignment...",
  "alippline": "posterior probability..."
}
```

| Field       | Type   | Description                                                |
| ----------- | ------ | ---------------------------------------------------------- |
| `ienv`      | int    | Envelope start coordinate                                  |
| `jenv`      | int    | Envelope end coordinate                                    |
| `iali`      | int    | Alignment start coordinate on target                       |
| `jali`      | int    | Alignment end coordinate on target                         |
| `bitscore`  | float  | Domain bit score                                           |
| `cevalue`   | float  | Conditional E-value (given the sequence was found)         |
| `ievalue`   | float  | Independent E-value (this domain's score alone)            |
| `bias`      | float  | Domain composition bias                                    |
| `alimodel`  | string | Query profile consensus                                    |
| `alimline`  | string | Match annotation line (+ = positive, uppercase = identity) |
| `aliaseq`   | string | Target sequence alignment                                  |
| `alippline` | string | Posterior probability annotation                           |

### Coordinate Fields Explained

- **Envelope** (`ienv`-`jenv`): Broader region where the domain match likely exists. Used for defining domain boundaries.
- **Alignment** (`iali`-`jali`): Exact coordinates of the aligned region within the target sequence.
- The envelope is always >= the alignment range.

## Input Formats

### Protein Sequences (phmmer, hmmscan, jackhmmer)

Raw amino acid sequence:

```
MKWMFKEDHSLEHRCVESAKIRAKYPDRVPVIVEKVSGSQIVDIDKRKYLVPS
```

FASTA format:

```
>my_protein
MKWMFKEDHSLEHRCVESAKIRAKYPDRVPVIVEKVSGSQIVDIDKRKYLVPS
```

### Multiple Sequence Alignments (hmmsearch)

Supported formats: Stockholm, A2M, AFA (aligned FASTA), PSI-BLAST, Clustal, Phylip.

Stockholm example:

```
# STOCKHOLM 1.0
seq1  MKWMFKEDHSLEHR
seq2  MKWLFKEDHSLEHR
seq3  MKWMFKEDNSLEHR
//
```

### Profile HMMs (hmmsearch)

HMMER3 format only. HMMER2 format is NOT supported.

## Scoring Thresholds

### E-value Types

| E-value                             | Description                                         | When to Use                           |
| ----------------------------------- | --------------------------------------------------- | ------------------------------------- |
| **Sequence E-value** (`evalue`)     | Statistical significance of the full sequence score | Primary filter for hit significance   |
| **Conditional E-value** (`cevalue`) | Domain significance given the sequence is a hit     | Compare domains within same hit       |
| **Independent E-value** (`ievalue`) | Domain significance evaluated independently         | Compare domains across different hits |

### Threshold Parameters

| Parameter | Type      | Default | Description                                  |
| --------- | --------- | ------- | -------------------------------------------- |
| `E`       | Reporting | 1.0     | Include sequences with E <= this in output   |
| `domE`    | Reporting | 1.0     | Include domains with E <= this in output     |
| `incE`    | Inclusion | 0.01    | Sequences with E <= this are "significant"   |
| `incdomE` | Inclusion | 0.03    | Domains with E <= this are "significant"     |
| `T`       | Reporting | --      | Bit score threshold (alternative to E-value) |
| `domT`    | Reporting | --      | Domain bit score threshold                   |

## CORS and Authentication

- The API supports cross-origin requests (CORS headers included).
- No authentication required -- the API is free and open.
- No explicit rate limits documented, but large batch submissions should include delays between requests.

## Example curl Commands

```bash
# Submit hmmscan: sequence vs Pfam (JSON body)
curl -s -X POST \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{"input":"MKWMFKEDHSLEHRCVESAKIRAKYPDRVPVIVEKVSGSQIVDIDKRKYLVPS","database":"pfam"}' \
  https://www.ebi.ac.uk/Tools/hmmer/api/v1/search/hmmscan

# Submit phmmer: sequence vs SwissProt
curl -s -X POST \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{"input":"MKWMFKEDHSLEHRCVESAKIRAKYPDRVPVIVEKVSGSQIVDIDKRKYLVPS","database":"swissprot"}' \
  https://www.ebi.ac.uk/Tools/hmmer/api/v1/search/phmmer

# Check job status
curl -s -H "Accept: application/json" \
  https://www.ebi.ac.uk/Tools/hmmer/api/v1/search/{job_id}

# Get results
curl -s -H "Accept: application/json" \
  https://www.ebi.ac.uk/Tools/hmmer/api/v1/result/{job_id}
```
