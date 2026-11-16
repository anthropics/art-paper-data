# Fixed-input benchmark

Inputs, configuration, and results of the fixed-input benchmark in "Autonomous AI agents discover reverse transcriptases with tandem repeat arrays". The answer key is in `fixed_input_benchmark_grading`.

## Results

`results/results_by_attempt.csv` has one row per attempt (seven models, five levels, 100 attempts per model and level).

| Column | Description |
|---|---|
| `tract_*`, `rt_*`, `partner_*` | The ten claims (1 = asserted, 0 = not). The answer key maps each column to its claim. |
| `claims_asserted` | Number of asserted claims |

## Rebuilding the benchmark

1. Build the container and the reference databases (`environment/`).
2. For each level, provide the inputs, tools, programs, and databases listed in `levels/level_<n>.yaml` (tool definitions in `tools/`, server of the submission tool in `code/`).
3. Run each attempt as one agent session with the settings and limits in `agent/` and the prompt in `levels/prompts/level_<n>.txt`.
4. Grade the last valid submission with the answer key.
5. Run 100 attempts per model and level.

## Not included

- Source code, apart from the server of the submission tool in `code/`.
- Model identifiers.
- Operational settings of the infrastructure that ran the attempts, and the rules for excluding and replacing attempts.
