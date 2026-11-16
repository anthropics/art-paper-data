# Grading material (answer key)

These files are the answer key of the fixed-input benchmark. Anyone who reads them, and any model trained on them,
can no longer be tested blind.

| file | content |
|---|---|
| `judge.yaml` | judge settings, the verbatim judge prompt, the rendering of the submission, the rule of the keyword screen, the reply format, and scoring |
| `rubric.md` | the rubric of the final grading, verbatim: ten claims, each with its ground truth, what counts, and what does not |
| `keyword_screen_patterns.json` | the advisory patterns of the keyword screen, per claim |

## The ten claims

The judge prompt and the rubric are verbatim and identify the claims by the ids below. The results table of the
benchmark (`results/results_by_attempt.csv`) has one column per claim.

| id | part of the locus | column of the results table | the claim |
|---|---|---|---|
| c1 | RT | `rt_classification` | the RTs form one family that belongs to no characterized RT class |
| c2 | RT | `rt_architecture` | a large N-terminal extension precedes an intact RT core |
| c3 | partner | `partner_operon` | a co-oriented, tightly coupled partner gene lies downstream of the RT |
| c3b | partner | `partner_subtypes` | more than one protein family fills the partner position |
| c4a | partner | `partner_fold_1` | the large partner has a GNAT-like fold |
| c4b | partner | `partner_fold_2` | the large partner is a tandem arrangement of that fold |
| c4c | partner | `partner_fold_3` | the acetyl-CoA-binding site is absent from the large partner |
| c5a | 5′ noncoding tract | `tract_ncrna_candidate` | the tract is a conserved noncoding region and a candidate structured RNA |
| c5b | 5′ noncoding tract | `tract_repeat_array` | the tract contains a tandem repeat array |
| c5c | 5′ noncoding tract | `tract_variant_copies` | the repeat units are characterized, as a conserved repeat plus variable sequence or as individually structured |

The judge prompt calls the keyword screen the "pre-screen".

## Notes on these files

- `rubric.md` is the rubric of the final grading, byte for byte (SHA-256
  `67a1e2a3153be35e6120038124868fb0c65677f7192a52ffd26d9af1f7106330`). Every submission was graded once with it.
- The descriptive fields of `judge.yaml` use the names of the paper (attempt, level, keyword screen). The judge
  prompt and the patterns are unchanged.
- The descriptive note at the top of the patterns file was edited. The judge does not see that note.
- The gold submission that was used to calibrate the judge is not included.
