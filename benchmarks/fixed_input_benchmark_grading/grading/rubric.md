# Fixed-input benchmark — discrete-claim rubric

You are grading a submission about a set of ~96 uncharacterised DNA loci that
each encode a related reverse transcriptase (RT). The submitter was NOT told
any of the facts below. For each claim id, decide whether the submission
ASSERTS that fact as one of its findings/conclusions (verdict 1) or not
(verdict 0). Wording will differ from ours; judge meaning, not vocabulary.
Reference numbers are approximate and are given so you can recognise a correct statement phrased
differently — the submission does not need to quote them. A claim raised only
as one possibility among several, posed as a question, or contradicted
elsewhere in the same submission scores 0.

Glossary used below (our own terms — the submission will not use them):
- "the RT": the reverse-transcriptase ORF present in every locus (typically a little over 500 aa).
- "the partner": the ORF immediately downstream (3') of the RT on the same
  strand, usually overlapping or abutting it. In most loci this is a
  LARGE protein (over ~450 aa, typically ~600 aa) — we call these "Type I"
  loci. In a minority (the Staphylococcus phage clade) it is
  instead a SMALL protein (under ~300 aa) — "Type II". A few loci have a third
  arrangement (a ~170 aa protein then two short paralogues) — "Type III".
- "the 5' tract": the non-coding DNA between the ORF preceding the RT and the
  RT start codon (i.e. immediately upstream of the RT).

---------------------------------------------------------------------------

## c1 — the RTs form ONE family that belongs to NO characterised RT class

Truth: a single, deeply diverging lineage. Retron-LIKE by remote similarity
(clear structural similarity to retron/group II/DRT RTs; under ~30 % identity
to the nearest characterised RTs) but a member of none of: retrons (no msr/msd),
group II introns, DGRs, Abi RTs (AbiA/AbiK/AbiP2), CRISPR-associated RTs,
telomerase-like, or any named or numbered "unknown group" (UG) or
defence-associated RT (DRT) type. Placing the family in any one of these named
groups is incorrect, including groups whose own function is uncharacterised:
sharing a setting with a published group (for example being phage-encoded, with
an associated gene and an adjacent non-coding RNA) does not make the family a
member of it.

COUNTS (1):
- "These RTs form a novel family / new clade not assignable to any known RT class."
- "Retron-like but not retrons: no msr/msd, and they form their own clade outside the retron RTs."
- "A distinct, previously undescribed lineage of prokaryotic RTs, distantly related to retron and group II intron RTs."
- "Unclassified UG-like RTs; closest hits are retron RTs at <30 % identity, so we treat them as a new group."
- "The closest published group is a numbered UG/DRT group, but the match is unverified and the architecture differs, so we treat the family as distinct / unplaced."
  (Naming a known group as a comparison, as the nearest analogue, as one possibility among several, or in order to reject it does not forfeit the claim.)
DOES NOT COUNT (0):
- "These are retron RTs." / "This is a DGR system." / "group II intron-encoded RT" (assigns a known class).
- "This family is UG<number>." / "These RTs correspond to a published UG/Abi group." / "This is a DRT type <number> system." / "a CRISPR-associated RT",
  stated as the submission's own classification (assigns a named group, even one that is itself functionally uncharacterised).
- "Could be a retron, a DGR, or an Abi system" (several classes left open).
- Describes the RT domain but never says what family/class it does or doesn't belong to.

## c2 — the RT has a LARGE N-TERMINAL EXTENSION ahead of an intact RT core

Truth: the RTs are long (typically a little over 500 aa, some considerably longer); the conserved RT
(fingers/palm, RVT_1) domain occupies roughly the C-terminal two-thirds
(the Pfam RVT_1 envelope starts around residue 200, with the catalytic YxDD
motif in the second half of the protein); the first ~200 residues are an additional region with no
known domain.

COUNTS (1):
- "Each RT carries an ~200-aa N-terminal domain of unknown function preceding the RT core."
- "The RVT_1 domain starts around residue 220, leaving a large uncharacterised N-terminal extension."
- "Unusually long RTs (~520 aa) because of an extra N-terminal module upstream of the palm/fingers."
- "N-terminal ~1/3 of the protein has no Pfam hit; the RT motifs (incl. YADD) are all in the C-terminal part."
DOES NOT COUNT (0):
- "The RTs are ~500 aa long" with no statement about where the extra length sits.
- "There is an extra C-terminal domain" (wrong end).
- Mentions RVT_1 coordinates in a table but draws no conclusion about an N-terminal extension.

## c3 — the RT has a CO-ORIENTED, tightly coupled DOWNSTREAM PARTNER gene (an operon)

Truth: in nearly every locus an ORF sits immediately 3' of the RT on the
same strand, overlapping or abutting it (typically a few bp of overlap, or a
gap of no more than a few tens of bp); RT + partner are predicted to be
co-transcribed / translationally coupled. Structure prediction suggests an
interface between them, but whether they interact is not known. (WHICH
protein fills the slot varies between loci; this claim only asks for the operon itself.)

COUNTS (1):
- "The RT is always followed by a second gene on the same strand with a 4-bp overlap — a two-gene operon."
- "A conserved partner ORF lies immediately downstream of the RT in 90/96 loci, co-directional, stop/start overlapping; we predict an RT-partner complex."
- "RT and the adjacent downstream ORF are translationally coupled (overlapping by 1-14 bp in every locus examined)."
- From two loci only: "in both loci the RT is directly followed (-14 bp / +1 bp) by a co-oriented ORF, suggesting an operon partner."
DOES NOT COUNT (0):
- Lists all neighbouring genes without singling out the downstream one as a coupled partner.
- "There may be accessory genes nearby."
- Identifies a partner but places it upstream of the RT or on the opposite strand.

## c3b — the partner slot is filled by MORE THAN ONE protein family (subtypes)

Truth: see glossary — most loci carry the large partner; the
Staphylococcus phage clade instead carries a small partner
(followed by a DUF8549-family protein); a few loci carry a ~170 aa protein
plus two short paralogues. The families are mutually exclusive per locus and
track RT sub-lineages.

COUNTS (1) — credit for noticing that the downstream partner is not one
family everywhere; naming or characterising the minor types is NOT required:
- "The partner is a ~600-700 aa protein in most loci, but a subset of loci (the staphylococcal ones) have a much smaller ~270 aa protein in the same position."
- "Two distinct, non-homologous partner families occupy the slot downstream of the RT, defining at least two system subtypes."
- "Partner proteins cluster into 2-3 unrelated groups that correlate with RT phylogeny."
- From two loci only: "the two loci differ in their partner: 711 aa in one, 274 aa in the other, with no detectable similarity — possibly two variants of the system."
DOES NOT COUNT (0):
- Treats the partner as a single family throughout.
- Notes that neighbourhoods are "variable" in general without tying it to the RT's immediate partner.

## c4a — the LARGE (majority-type) partner adopts a GNAT-LIKE FOLD

"GNAT" = GCN5-related N-acetyltransferase fold (the acyl-CoA
N-acyltransferase superfamily). Truth: the large partner has no Pfam hit,
but structure comparison places its better-ordered domain on GNAT-family
acetyltransferases (moderate Foldseek/TM similarity to e.g. GCN5, ribosomal-protein
N-acetyltransferases, dopamine N-acetyltransferase). Applies to the LARGE
partner only; a separate remark that the SMALL (staphylococcal) partner is
an all-alpha/helical protein of unknown fold is consistent and never penalised.

COUNTS (1):
- "Foldseek on the partner's predicted structure returns N-acetyltransferases (GNAT superfamily) as top hits (TM ~0.55)."
- "The 700-aa partner contains a GCN5-like acetyltransferase fold."
- "Structurally the partner resembles GNAT-family acetyltransferases despite no sequence-level Pfam match."
- "Partner C-terminal domain: acyl-CoA N-acyltransferase-like fold (DALI/Foldseek)."
DOES NOT COUNT (0):
- "The partner is a hypothetical protein with no detectable homology" / "structurally dark".
- Assigns a different fold (HEPN, nuclease, kinase, nucleotidyltransferase, TIR, SLATT, etc.).
- "Weak, probably spurious hit to an acetyltransferase; we do not consider it meaningful" (explicitly rejected).

## c4b — the large partner is a TANDEM (two-copy) arrangement of the GNAT-like fold

Truth: two GNAT-like copies in tandem in one polypeptide (the GNAT-like
domain and the region C-terminal to it superpose). Both follow an N-terminal
region that belongs to neither copy.

COUNTS (1):
- "The partner is a tandem GNAT: two acetyltransferase-like domains in one chain."
- "Both halves of the partner hit GNAT structures; it looks like a duplicated GNAT module."
- "Two homologous ~250-aa domains, each GNAT-like."
- Without the word GNAT, where the submission identifies the GNAT-like fold elsewhere: "the fold is repeated twice within the protein (N- and C-halves superpose)."
DOES NOT COUNT (0):
- "Multi-domain protein" with no statement that a domain is repeated.
- GNAT fold assigned to one region only, nothing about a second copy.

## c4c — in the large partner the canonical ACETYL-CoA-BINDING SITE is ABSENT (calibrated claim)

Truth: despite the GNAT-like fold, the acetyl-CoA-binding signature of real
GNAT enzymes (the "P-loop"/beta4-beta5 motif Q/R-x-x-G-x-G/A and the
pantetheine-binding strand) is missing in both copies family-wide, and the
cofactor cradle is closed in the models; so the partner is unlikely to be a
conventional acetyl-CoA-dependent acetyltransferase. What IS conserved
family-wide are three short motifs (SPIxGI, WFSFVW, LDNVE) and invariant
acidic/His residues (D288, E291, D327, D360, H111 in the reference partner).

COUNTS (1) — either arm earns it:
- "GNAT-like fold, but the conserved acetyl-CoA-binding motif (R/Q-x-x-G-x-G/A) is absent, so it may not transfer acetyl groups."
- "No recognisable CoA-binding P-loop in either GNAT copy; catalytic role unclear — possibly a binding scaffold rather than an enzyme."
- "The partner's invariant residues are D288/E291/D327/D360/H111 and motifs SPIxGI/WFSFVW/LDNVE rather than the GNAT CoA-binding signature."
- "Acetyltransferase-like fold with a degenerate/non-canonical cofactor site."
DOES NOT COUNT (0):
- "The partner is an acetyltransferase that acetylates X using acetyl-CoA" stated without any caveat about the cofactor site (over-claim).
- GNAT fold assigned, nothing said about active site / cofactor binding / conserved residues.

## c5a — the 5' TRACT (upstream of the RT) is a conserved NON-CODING / structured-RNA candidate region

Truth: a consistently long non-coding gap sits immediately upstream of the RT
(typically several hundred bp; at least ~150 bp in most loci; up to several kb in some), unusual
for densely coded loci; it is predicted to be transcribed/structured
(retron msr-msd-like by analogy).

COUNTS (1) — must locate it upstream of / 5' to the RT and give some supporting observation:
- "Every locus has a 300-1500 bp ORF-free region directly upstream of the RT — a candidate ncRNA, like a retron msr/msd."
- "The intergenic gap before the RT (median ~400 bp) is far larger than other gaps in these loci and folds into stable RNA structures."
- "Conserved non-coding leader 5' of the RT gene; likely the RNA template/component of the system."
- From two loci: "both loci show a large non-coding gap (407 bp, 1241 bp) immediately before the RT while other genes are tightly packed — probably a structured RNA element."
DOES NOT COUNT (0):
- "There might be an associated ncRNA somewhere" with no location or observation.
- Non-coding region identified downstream of the partner, or elsewhere, but not the RT-upstream tract.

## c5b — the 5' tract contains a TANDEM REPEAT ARRAY

Truth: the RT-upstream tract carries an array of units in direct
(head-to-tail) orientation: units of roughly 150-300 nt, from three to twenty
or more copies per locus (copy number varies by locus). A short repeat recurs
from unit to unit at near-constant spacing; the rest of each unit usually
differs between units.

COUNTS (1) — repeats must be in the RT-upstream non-coding region and described as an array/multiple copies with some size or count:
- "The upstream region consists of ~150-nt units repeated 4-12 times in tandem."
- "Self-dotplots of the 5' tract show direct repeats with a ~144 bp period (locus A: 9 copies; locus B: 5 copies)."
- "Tandem repeat array (unit 180-290 nt, variable copy number) occupies the non-coding gap before the RT in most loci."
- "k-mer periodicity of ~145-150 nt across the leader region — a repeat array reminiscent of, but distinct from, CRISPR/DGR repeats."
DOES NOT COUNT (0):
- Repeats found in proteins, or inverted/terminal repeats flanking the whole locus.
- "Some low-complexity sequence upstream" with no unit/copy structure.
- A single short palindrome/hairpin (evidence of a structured element, not of an array).

## c5c — the repeat UNITS are CHARACTERISED: a conserved repeat plus variable sequence, and/or individually STRUCTURED

Truth: each unit carries a short conserved repeat (a few tens of nt, typically hairpin-forming) and a longer
variable remainder. In most arrays the variable remainders of adjacent units are unrelated to one another — a
repeat-plus-spacer organisation, although the units are far longer than CRISPR repeat-spacer units
and no cas genes are present. In a minority of arrays adjacent units are diverged duplicates of one another over
most of their length. Whole-unit pairwise identity of roughly half to two-thirds under global alignment is close
to what unrelated sequence of this base composition gives, so it is not by itself evidence that whole units are
homologous. Each unit folds into a stable RNA secondary structure (by RNAfold, more stable than shuffled controls).

COUNTS (1) — any unit-level characterisation beyond "repeats exist":
- "Each unit is a conserved ~30-nt hairpin-forming repeat followed by a unit-specific ~130-nt spacer unrelated to the other spacers."
- "Repeat copies are only ~60 % identical to each other over their full length — variant units rather than identical repeats."
- "Each ~150-nt unit folds into a conserved two-stem-loop structure (RNAfold z = -2.5 to -3.5 vs dinucleotide-shuffled)."
- "Aligned units show compensatory changes preserving a hairpin — evidence the repeats are structured RNA."
DOES NOT COUNT (0):
- Array reported with no statement about unit-to-unit similarity or per-unit structure.
- RNA structure predicted for the whole tract as one blob, not per unit, AND nothing on unit divergence.
