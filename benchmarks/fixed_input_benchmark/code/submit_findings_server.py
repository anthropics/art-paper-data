"""MCP server of the submit_findings tool of the fixed-input benchmark.

To add it to Claude Code (requires the MCP Python SDK, `pip install mcp`):

    claude mcp add tools -- python /path/to/submit_findings_server.py

With the server named `tools`, the model sees the tool as mcp__tools__submit_findings, as in the benchmark.
The last valid submission is written to submission/submission.json in the working directory of the server
(set SUBMISSION_OUT to change the path). Use a new directory for each attempt.

The tool is the code of the benchmark. The imports, the server object, `_current`, and the two paths were
adapted so that the file runs outside the container of the benchmark.
"""
import json
import os
from pathlib import Path
from types import SimpleNamespace

import anyio
from pydantic import BaseModel, Field

try:
    from mcp.server.fastmcp import FastMCP  # MCP Python SDK, version 1
except ImportError:
    from mcp.server import MCPServer as FastMCP  # version 2

mcp = FastMCP("tools")

# The attempt to which a stored submission belongs.
_current = SimpleNamespace(id="attempt")

# Private copy of the last valid submission, and the copy that is graded.
STATE_DIR = Path(os.environ.get("SUBMISSION_STATE_DIR", "submission/state"))
SUBMISSION_OUT = Path(os.environ.get("SUBMISSION_OUT", "submission/submission.json"))

MIN_REPORT_CHARS = 500
MAX_REPORT_CHARS = 150_000
# No cap on the number of findings (a count would hint at the expected scope); the
# structured payload is bounded by size only, like the report.
MAX_FINDINGS_CHARS = 200_000


def _store_path() -> Path:
    return STATE_DIR / "submission.json"


def _empty_store() -> dict:
    return {"problem_id": None, "submission": None, "n_submissions": 0}


def _load_store() -> dict:
    p = _store_path()
    if not p.exists():
        return _empty_store()
    try:
        return json.loads(p.read_text())
    except (OSError, ValueError):
        return _empty_store()


def _save_store(store: dict) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    os.chmod(STATE_DIR, 0o700)
    tmp = _store_path().with_suffix(".tmp")
    tmp.write_text(json.dumps(store))
    os.chmod(tmp, 0o600)
    os.replace(tmp, _store_path())


def _publish_submission(store: dict) -> None:
    SUBMISSION_OUT.parent.mkdir(parents=True, exist_ok=True)
    os.chmod(SUBMISSION_OUT.parent, 0o755)
    tmp = SUBMISSION_OUT.with_suffix(".tmp")
    tmp.write_text(json.dumps(store))
    os.chmod(tmp, 0o644)
    os.replace(tmp, SUBMISSION_OUT)


class Finding(BaseModel):
    claim: str = Field(description="One specific, committed statement (1-3 sentences)")
    evidence: str = Field(description="The observations/statistics from your analysis that support it")
    confidence: float = Field(description="Your probability (0-1) that the claim is correct")


def _as_findings(v: list[Finding] | list[dict] | str) -> list[dict]:
    # Some models emit arrays as one JSON string; accept that too.
    if isinstance(v, str):
        v = json.loads(v)
    out = []
    for f in v:
        d = f.model_dump() if isinstance(f, Finding) else dict(f)
        out.append({"claim": str(d.get("claim", "")),
                    "evidence": str(d.get("evidence", "")), "confidence": float(d.get("confidence", 0.0))})
    return out


@mcp.tool()
async def submit_findings(
    findings: list[Finding] | str = Field(description="Your findings, most important first. A JSON list of objects, or that list as one JSON string."),
    report_markdown: str = Field(description=f"Full Markdown report with the evidence chain. {MIN_REPORT_CHARS}-{MAX_REPORT_CHARS} characters."),
    follow_up: str = Field(description="The experiment(s) that would test your main prediction, and how impactful confirmation would be"),
) -> str:
    """Submit your findings. A valid resubmission replaces the previous one; malformed submissions are rejected and not recorded."""
    await anyio.sleep(0)
    if _current is None:
        return "ERROR: no problem is set up yet."
    try:
        items = _as_findings(findings)
    except (ValueError, TypeError) as e:
        return f"ERROR: findings could not be parsed ({type(e).__name__}). Pass a JSON list of {{claim, evidence, confidence}} objects. Nothing was recorded."
    if not items:
        return "ERROR: give at least one finding. Nothing was recorded."
    if len(json.dumps(items)) > MAX_FINDINGS_CHARS:
        return f"ERROR: findings too long (maximum {MAX_FINDINGS_CHARS} characters in total). Nothing was recorded."
    for i, f in enumerate(items, 1):
        if not f["claim"].strip():
            return f"ERROR: finding {i} has an empty claim. Nothing was recorded."
        if not (0.0 <= f["confidence"] <= 1.0):
            return f"ERROR: finding {i} confidence must be in [0, 1]. Nothing was recorded."
    if len(report_markdown.strip()) < MIN_REPORT_CHARS:
        return f"ERROR: report too short (minimum {MIN_REPORT_CHARS} characters). Nothing was recorded."
    if len(report_markdown) > MAX_REPORT_CHARS:
        return f"ERROR: report too long (maximum {MAX_REPORT_CHARS}). Nothing was recorded."
    store = _load_store()
    replaced = store.get("problem_id") == _current.id and store.get("submission")
    new_store = {"problem_id": _current.id, "submission": {"findings": items, "report_markdown": report_markdown, "follow_up": follow_up},
                 "n_submissions": int(store.get("n_submissions", 0)) + 1}
    _save_store(new_store)
    _publish_submission(new_store)
    return ("Replaced the previous submission" if replaced else "Recorded the submission") + ". The task is complete. You may resubmit to replace it; the last valid submission is graded."


if __name__ == "__main__":
    mcp.run()
