---
name: family-adjudication-rubric
description: >
  Use whenever assigning survey verdicts (PROMOTE / PARK / KILL / CONTROL)
  to candidate accessory families — the calibrated evidence bars from the
  453-family Cas13 adjudication. Prevents verdict drift between workers and
  runs; every verdict must cite which criterion decided it.
---

# Family adjudication rubric

Four verdicts, exhaustive and exclusive. Cite the deciding criterion in the
verdict's reason field.

## CONTROL — known biology, called as such
Family is an established member of the system (core machinery, published
accessory, known regulator class) OR a universal co-resident (RM, common TA,
transposase). Rediscovering it validates the pipeline; it is NEVER a finding
and NEVER gets a deep report — one line in the survey.

## PROMOTE — plausible dedicated partner, earns depth
ALL of:
1. Passes clonality-vs-independence (≥3 non-identical p90 / ≥3 contigs /
   ≥2 anchor lineages).
2. Operonic signal (passes gates, or a quantified rescue per
   operonic-gate-scoring).
3. NOT explainable as: core machinery, known accessory, mobile element
   (transposase/integrase/phage structural), or generic co-resident defence.
4. Survives the novelty-kill-test (not already published for this system).
Rank promotions by (independence breadth × operonic strength × annotation
tractability) — a dark family you can fold beats a dark family you can't.

## PARK — real signal, not actionable now
Passes 1-2 but fails 3 ambiguously (e.g. defence-adjacent but could be
co-resident), or passes weakly near the bars. State what evidence would
promote it. PARK is not a soft KILL: the list must be re-checkable.

## KILL — no dedicated association
Fails independence (clonal), or clearly mobile/bystander, or operonic signal
absent with no rescue argument. One-line reason naming the failed criterion.

## Discipline
- Never promote on annotation alone ("interesting domain") without the
  independence + operonic evidence.
- Never kill on "no annotation" — darkness is not evidence of absence;
  darkness + independence + operonic signal is a canonical PROMOTE.
- Controls are decided FIRST (before looking at scores) to avoid
  criteria-shopping.
