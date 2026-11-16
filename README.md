# Data for "Autonomous AI agents discover reverse transcriptases with tandem repeat arrays"

This repository is not maintained: it is a static release alongside the paper.

**`benchmarks/fixed_input_benchmark/` The fixed-input benchmark.** `inputs/` Loci and predicted structures given to the models (96 GenBank and 1,131 mmCIF files). `levels/` Prompt and configuration of each of the five levels of input. `tools/`, `environment/`, and `agent/` Tools, container, and agent settings. `code/` MCP server of the submission tool. `results/` Graded claims for every attempt (seven models, n = 100 attempts per model and level). `README.md` Steps to rebuild the benchmark.

**`benchmarks/fixed_input_benchmark_grading/` Answer key of the benchmark.** `grading/rubric.md` The ten claims. `grading/judge.yaml` Prompt and settings of the language-model judge. `grading/keyword_screen_patterns.json` Patterns of the keyword screen.

**`original_campaign_reports/` Reports written by the agents.** `ART_report/` Report on the array-associated RT (ART) lineage. `other_reports/` The other 18 reports from the original campaign. Black boxes mark internal names, internal file paths, and task, job, and run identifiers that were removed. Protein labels of 22 characters (followed by `#` and the protein length) are hashes of the protein sequences, kept so that proteins can be told apart. Contig labels of the same form, and labels cut short in text, figures, and file names, are kept likewise.

**`prompts_and_skills/` Research brief and skills.** `research_brief_supplementary_note1.md` Research brief given to the agents (Supplementary Note 1). `campaign_skills/` Skills consulted by the agents during original campaign (n = 15 of the 139 available) and one skill listed in a task plan (`scientific-visualization`). Words in square brackets such as [database], [harness], and [size], names and numbers that were replaced.

**`structure_models_and_inputs/` Structure models and prediction inputs.** AlphaFold2 and Boltz-2 models of ART, NART, and retron RTs and of ART partners, with input alignments and scores.
