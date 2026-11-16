# Dispatching heavy compute (GPU / long CPU) mid-run

When a task needs compute the sandbox doesn't have — a GPU, hours of
CPU, or a tool too heavy to install locally — dispatch it via the
`[harness]-compute` MCP. The job runs on Modal; you get the result
back as a tarball.

**Do NOT** try to install CUDA / pull GPU containers / spawn cloud
VMs from the sandbox shell. The sandbox is CPU-only and has no cloud
credentials. Use this MCP instead.

## When to use it

- "Fold these 50 sequences" — but the existing `[database]-fold` /
  `[database]-of3` MCPs only do one at a time and you need a custom loop
- "Run this MSA across 100k sequences" — too long for the sandbox's
  wall clock
- "Train / fine-tune a small model on this data"
- Any script that needs `torch.cuda` and the dedicated GPU MCPs
  don't cover it

If a dedicated MCP already does what you need (`[database]-fold`,
`[database]-boltz2`, `[database]-foldseek-afdb`), use that — it's faster and
cached. This is for the ad-hoc cases.

## The contract

Every call needs the **`project_handle`** — a secret the relay
registered for this run. Read it once and reuse it:

```bash
HANDLE=$(cat "[path]")
```

If that file doesn't exist, this run has `[compute] budget_usd = 0`
in its config — compute is disabled; **don't try to work around it.**

## Logging a request when you can't submit

If [file] doesn't exist, OR `compute_submit` returns
"budget exhausted": don't silently drop the work. Append one JSON
line to `COMPUTE_REQUESTS.jsonl` at the project root describing what
you'd have run — `{task_id, image, gpu, timeout_s, estimate_usd,
why}` — then carry on with the best CPU-only fallback you have. The
owner sees these requests in the viewer and can top up the budget.

Estimate `estimate_usd` from `compute_capabilities()` rates ×
`timeout_s` (the same cap-based reservation `compute_submit` would
have charged).

```bash
printf '{"task_id":"%s","image":"gpu-bio","gpu":"H100","timeout_s":1800,"estimate_usd":2.40,"why":"%s"}\n' "$[harness]_TASK_ID" "fold 50 candidates" >> "$[harness]_PROJECT_DIR/COMPUTE_REQUESTS.jsonl"
```

Submit: a list of small files (your script + configs + tiny inputs)
and an argv. Anything written to `../out/` plus `stdout.txt` /
`stderr.txt` comes back.

```
compute_capabilities()
  → {"images": {"cpu-bio": {…}, "gpu-bio": {gpu_allowed: ["L4","A100-40GB","A100-80GB","H100"], …}},
     "rates_usd_hr": {cpu_per_vcpu, mem_per_gib, gpu: {...}}}

compute_budget(project_handle)
  → {"project": "...", "budget_usd": 50.0, "reserved_usd": 12.40, "n_jobs": 3}

compute_submit(
  project_handle=HANDLE,
  argv=["python3", "fold_batch.py"],
  files={"fold_batch.py": <base64>, "seqs.fasta": <base64>},
  image="gpu-bio", gpu="A100-40GB", timeout_s=1800)
  → {"job_id": "[id]", "sandbox_id": "[id]",
     "cost_estimate_usd": 1.64, "reserved_usd": 14.04, "budget_usd": 50.0}

compute_status(job_id, project_handle=HANDLE)
  → {"phase": "running" | "done" | "pending", "exit_code": 0, …}

compute_result(job_id, project_handle=HANDLE)
  → {"download_url": "https://…", "[field]": "[path]"}
```

**Cost is reserved at submit time** from the timeout cap (not actual
runtime), so the budget is a hard ceiling — check `compute_budget`
before submitting if you're near the limit, and prefer the smallest
`timeout_s` that's realistic.

## Practical pattern

1. Write the script locally in your worktree (so it's reviewable):
   `analysis/fold_batch.py`. Make it write outputs to `../out/`.
2. Base64 the files and call `compute_submit`. Pass the run's project
   name so `compute_list(project)` works for cleanup.
3. Poll `compute_status` (every ~30 s for GPU jobs; they take minutes
   to cold-start). Do other work between polls.
4. On `phase == "done"`, fetch `compute_result`, download the tar,
   unpack into your worktree.
5. **Always check `exit_code`** and read `stderr.txt` before trusting
   outputs.

## Limits and gotchas

- **Inputs are for code, not data.** Practical wire limit is
  ~20 MiB ([service] + base64). For anything larger:
  ```
  s = compute_stage_input(project_handle=HANDLE, suffix=".fasta")
  # → {put_url, get_url, [field]}
  ```
  Upload with `curl -X PUT -H "Content-Type: application/octet-stream" --upload-file data.fasta "<put_url>"`
  then pass `s["get_url"]` in your script's argv — the Modal box
  fetches it with plain `curl -o` (no [storage] creds needed; signed URLs
  are self-authorizing). Don't try a [storage] copy from the
  sandbox or the Modal box: neither has [storage] credentials.
- **`image` is a capability NAME** (`cpu-bio` / `gpu-bio`), not a
  Docker tag. The toolchain matches the [harness] sandbox (PyMOL,
  hmmer, samtools, libGL, …). If something's missing, that's a PR to
  the image, not a `pip install` in your script.
- **No state between jobs.** Each `compute_submit` is a fresh box.
- **Clean up**: `compute_cancel(job_id)` if you give up on a job;
  Modal's timeout is the backstop for orphans.
- The result tarball comes via a signed URL that expires in ~1 h —
  download it promptly.

## Building your own image

If no capability has the toolchain you need, build one:

```
out = compute_build_image(
  project_handle=HANDLE,
  base="debian-slim",            # or "gpu-bio", "colabfold", …
  pip=["torch==2.5.1","pandas==2.2.3","pyarrow"],
  apt=["build-essential"],
  commands=["pip install --no-deps somepkg"])
# → {"image_id": "im-…"}
```

Then `compute_submit(image=out["image_id"], …)`. Modal caches by
spec, so the second call with identical args is instant. Only IDs
this project built are accepted.

## Persistent volumes (datasets, checkpoints)

For data too big to inline AND that should survive across jobs
(training checkpoints, multi-GB datasets):

```
v = compute_volume(HANDLE, "data")  # → {"name": "[id]-data"}
compute_submit(…, volumes={"/data": v["name"]})
```

The script reads/writes `/data/…`; it persists between jobs.

## Multi-GPU

`gpu="H100:8"` requests 8× H100 (1..8). Use with `torchrun
--standalone --nproc_per_node=8` for DDP. Cost is reserved ×count.

## Capability catalog

`cpu-bio`, `gpu-bio` (the [harness] sandbox toolchains),
`debian-slim` (build-only base), plus pre-built tool images:
`colabfold`, `esmfold`, `boltz`, `proteinmpnn`, `diffdock`,
`rfdiffusion`, `scvi`, `scgpt`, `chai`, `protenix`, `evo2`,
`borzoi`, `bindcraft`, `esm2-embed`. For anything not covered, build it via
`compute_build_image`.
`compute_capabilities()` lists what's available with limits and rates.

## Reliability (fixed 2026-07-01)

`compute_status` / `compute_result` / `compute_list` are now backed by
durable [storage] job records + a done-marker the job uploads from inside
the sandbox — they work during AND after the sandbox's lifetime, so
poll and fetch at your leisure. A `compute_submit` that returns a
job_id has verifiably started (the dispatcher re-checks and refunds
otherwise). `compute_cancel` refunds the unused reservation tail.
`compute_capabilities().note` documents Modal's slower vCPUs — probe
before batch-sizing timeouts.
