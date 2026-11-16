---
name: novelty-kill-test
description: >
  Use before calling any family "novel" or "previously uncharacterized" in a
  report. A systematic attempt to prove the family is already known — via
  homolog annotations, structure matches, and targeted literature search.
  "Novel" survives only if this test fails to kill it.
---

# Novelty kill-test

Claiming novelty is a strong claim; run the kill sequence and report the
outcome of EACH step.

1. **Member annotation sweep** — pull database annotations for ALL cluster
   members (not the representative): one informatively-annotated member
   anywhere kills "dark". Modal desc "hypothetical protein" across members
   is necessary but not sufficient.
2. **Best-characterized homolog** — take the family's best non-self
   sequence/profile hit at ANY threshold and read what its source paper
   says. A 25%-identity homolog characterized in another system means your
   finding is "a divergent X in a new context", not "novel protein".
3. **Structure-space check** — Foldseek top hits (dark-family-annotation
   step 3): a strong fold match to a characterized protein reframes the
   claim the same way.
4. **Targeted literature** — search the system's accessory literature by
   FUNCTION CLASS, not protein name (novel proteins have no name):
   "Cas13 membrane accessory", "Type VI CRISPR toxin-antitoxin", recent
   reviews and their supplementary tables. Check the 2-3 latest systematic
   accessory screens for the system — your family may be in a supplement
   under a locus tag.
5. **Locus-tag trace** — pick 2 members from cultured/named organisms (not
   metagenome bins) and search their locus tags / protein accessions
   directly.

## Verdict language (use exactly one)

- **known**: identified as X in [ref] — cite it; verdict likely CONTROL.
- **divergent known**: fold/homology places it in family X, uncharacterized
  in THIS context — say both halves.
- **novel candidate**: steps 1-5 all negative — state that explicitly
  ("no annotated member (n=241), no profile hit <1, best TM 0.31, absent
  from [the 2-3 screens checked by name]").

A report that says "novel" without the per-step negative results is
unreviewable and will be bounced.
