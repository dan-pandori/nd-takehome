"""Reviewer kit for run olmo-iffu: shared loaders (written by the reviewer; no executor code imported).

Raw inputs are read read-only from the phase-1 workspace ~/review/olmo-iffu (hard links into the run's worktree:
never write there). Scratch (upstream fetches, tokenizer files, item texts) is ~/review/oiffu_rv; outputs are out/.
"""
import base64
import gzip
import json
import struct
import zlib
from pathlib import Path

RAW = Path.home() / "review" / "olmo-iffu"
ART = RAW / "artifacts" / "olmo_iffu"
SCR = Path.home() / "review" / "oiffu_rv"
KIT = Path(__file__).resolve().parent
OUT = KIT / "out"
OUT.mkdir(exist_ok=True)

JOBS = ["T1_dpo", "T2_dpo", "T2_s2300", "T3_dpo", "T4_s0750", "T4b_s0750", "T2c_dpo", "T2c_s2300"]


def iter_rows(job, with_ids=True, report=None):
    """Stream the complete rows of a job's samples file in file order (gzip handles multi-member files).
    A truncated tail or an unparsable line is counted in `report` (a dict), never silently skipped."""
    rep = report if report is not None else {}
    rep.update({"rows": 0, "bad_lines": 0, "truncated_tail": False})
    try:
        with gzip.open(ART / "samples" / f"{job}.jsonl.gz", "rt", encoding="utf-8") as f:
            for ln in f:
                if not ln.strip():
                    continue
                try:
                    r = json.loads(ln)
                except json.JSONDecodeError:
                    rep["bad_lines"] += 1
                    continue
                if not with_ids:
                    r.pop("ids", None)
                rep["rows"] += 1
                yield r
    except (EOFError, gzip.BadGzipFile, zlib.error):
        rep["truncated_tail"] = True


def load_rows(job, with_ids=False):
    rep = {}
    rows = list(iter_rows(job, with_ids=with_ids, report=rep))
    return rows, rep


def ids_of(row):
    b = base64.b64decode(row["ids"])
    return list(struct.unpack(f"<{len(b) // 4}i", b))


def answer_of(text):
    """Pre-registered answer: the text after the LAST '</think>', stripped; None when there is no '</think>'."""
    k = text.rfind("</think>")
    if k < 0:
        return None
    return text[k + len("</think>"):].strip()


def draw_key(row):
    """Draw order within a job and prompt: (chunk, index in chunk)."""
    return (row["chunk"], row["i"])


def load_jsonl(path):
    with open(path) as f:
        return [json.loads(ln) for ln in f if ln.strip()]


def dump(obj, name):
    p = OUT / name
    with open(p, "w") as f:
        json.dump(obj, f, indent=1, sort_keys=True, default=str)
    return p


def upstream_ifbench():
    """IFBench (allenai/IFBench @ cd189a9c) records from my own fetch, keyed by key."""
    return {str(r["key"]): r for r in load_jsonl(SCR / "upstream" / "ifbench" / "IFBench_test.jsonl")}


def upstream_ifeval():
    """IFEval (google-research instruction_following_eval @ e6890f85 data/input_data.jsonl), keyed by key."""
    return {str(r["key"]): r for r in load_jsonl(SCR / "upstream" / "ife" / "input_data.jsonl")}
