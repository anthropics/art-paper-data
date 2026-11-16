---
name: literature-access
description: Fetch and search scientific literature via the [harness]-literature MCP tools — open-access full text by DOI (with figures), PubMed search, and the citation-integrity rules that go with them.
---

# Literature access

The `[harness]-literature` MCP server gives every worker (and the editor)
first-class literature tools. Prefer these over hand-rolled
E-utilities/requests code — they are cached, rate-limit-coordinated
across all parallel workers, and store articles where everyone
(including the editor) can read them.

## Tools

- `mcp__[harness]-literature__article_search(query, limit)` — PubMed
  search; Boolean/MeSH syntax works (`"CRISPR"[Title] AND 2024[PDAT]`).
  Returns pmid/doi/title/journal/authors.
- `mcp__[harness]-literature__article_fetch(doi)` — open-access full text
  via Unpaywall → Semantic Scholar → PMC → CrossRef. Saves under
  `[workspace]/resources/articles/<doi-slug>/`:
  - `article.txt` — structured text (JATS sections as headings)
  - `article.xml` / `article.pdf` — originals when available
  - `figures/` — PMC figures with captions (biology results often
    live in the figures; read them)
  - `meta.json` — title/year/journal/abstract/paths
  Cached: repeat fetches are free. Check `article_status(doi)` first
  if unsure.

## Citation integrity (binding)

- `found: false` means NO open-access copy exists. You may use the
  returned abstract (attributed as abstract-only), but **never cite
  the body content of a paper you could not read** — write "(not
  accessible; abstract only)" in your notes and downgrade any claim
  that depended on it.
- Every DOI you cite in a report should either be fetched (so the
  editor can open it) or explicitly marked abstract-only/inaccessible.
- The editor spot-checks cited sources against the fetched copies —
  a claim attributed to a paper that its text contradicts is an
  automatic failure.
