"""Shared loaders (reviewer). Rows come from MY re-grade (out/regrade_*.jsonl), which re-read every stored text."""
import glob, json, os
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
MODELS = ["dpo", "s0100", "s0750", "s2300"]
JOB_ORDER = ["F", "E1a", "E1", "C1", "C2", "C3", "C4"]   # fixed phase first, then extension jobs in order


def problems():
    return [json.loads(ln) for ln in open(os.path.join(ROOT, "olmo32", "problems.jsonl"))]


def excluded():
    """Exclusions as pre-registered: aime2026_01 (carried over from the pilot); B2 found no other."""
    return {"aime2026_01"}


def rows():
    out = []
    for f in sorted(glob.glob(os.path.join(HERE, "out", "regrade_*.jsonl"))):
        out += [json.loads(ln) for ln in open(f)]
    for r in out:
        r["doubly"] = bool(r["rl"] and r["final"])
    return out


def job_rank(job):
    return JOB_ORDER.index(job.split("_")[0])


def draws(rs, model, pid):
    """All evaluation samples of (model, pid) in the pre-registered draw order: job order, then (chunk, i)."""
    sel = [r for r in rs if r["model"] == model and r["pid"] == pid and not r["job"].startswith("s0_")]
    return sorted(sel, key=lambda r: (job_rank(r["job"]), r["chunk"], r["i"]))
