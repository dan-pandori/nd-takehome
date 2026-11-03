#!/usr/bin/env python3
"""Reviewer-owned core for the olmo-rlzero-pilot recount (independent of the executor's olmo_pilot/*.py).

- `verify_*`: AI2's MathVerifier.__call__ at open-instruct bb58c664, executed from the upstream source text
  (extracted by `ast` from upstream/bb58_open_instruct_ground_truth_utils.py) over upstream math_utils.py
  (only the logger import is swapped). `grade_rl` runs it through `loop.run_in_executor(None, ...)`, exactly as
  VerifierFunction.async_call does in RL; `grade_main` runs it in the main thread (sympy's is_equiv live).
- `my_int`: my own format-robust integer read-out (last "Answer:" occurrence, else last \\boxed{...}).
- data loaders for problems, graded rows and (possibly truncated) gzip sample files.
"""
import ast
import asyncio
import base64
import gzip
import json
import re
import textwrap
import types
import zlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = Path.home() / "review" / "olmo-rlzero-pilot"      # phase-1 copy (hard links to the run's files)
ART = ROOT / "artifacts" / "olmo_pilot"
OUT = HERE / "out"

# ---------------------------------------------------------------- upstream verifier
_mu_src = (HERE / "upstream" / "bb58_open_instruct_math_utils.py").read_text()
_mu_src = _mu_src.replace("from open_instruct import logger_utils", "import logging").replace(
    'logger_utils.setup_logger("math_utils")', 'logging.getLogger("math_utils")')
MU = types.ModuleType("upstream_math_utils")
exec(compile(_mu_src, "upstream_math_utils", "exec"), MU.__dict__)

_g_src = (HERE / "upstream" / "bb58_open_instruct_ground_truth_utils.py").read_text()
_tree = ast.parse(_g_src)
_cls = next(n for n in _tree.body if isinstance(n, ast.ClassDef) and n.name == "MathVerifier")
_fn = next(n for n in _cls.body if isinstance(n, ast.FunctionDef) and n.name == "__call__")
_lines = _g_src.splitlines()[_fn.lineno - 1:_fn.end_lineno]
_call_src = textwrap.dedent("\n".join(_lines))


class VerificationResult:  # stub of open_instruct's dataclass (only .score is used)
    def __init__(self, score, cost=0.0, reasoning=None):
        self.score = score


_ns = {"re": re, "VerificationResult": VerificationResult, "Any": object}
for _name in ("last_boxed_only_string", "remove_boxed", "normalize_final_answer", "get_unnormalized_answer",
              "is_equiv", "hendrycks_is_equiv"):
    _ns[_name] = getattr(MU, _name)
exec(compile(_call_src, "upstream_MathVerifier.__call__", "exec"), _ns)
_CALL = _ns["__call__"]
CALL_SRC = _call_src


def verify(pred: str, label: str) -> bool:
    return _CALL(None, [], pred, label).score > 0


_LOOP = asyncio.new_event_loop()


def grade_rl_many(items):
    """items: list of (pred, label). Each runs via run_in_executor(None, ...) (a worker thread), as in RL."""
    async def go():
        loop = asyncio.get_event_loop()
        return await asyncio.gather(*[loop.run_in_executor(None, lambda p=p, l=l: verify(p, l)) for p, l in items])
    return _LOOP.run_until_complete(go())


def grade_rl(pred, label):
    return grade_rl_many([(pred, label)])[0]


def grade_main(pred, label):
    return verify(pred, label)


# ---------------------------------------------------------------- my own integer read-out (diagnostic)
_NUM = re.compile(r"-?\d+(?:,\d{3})*")


def my_int(text: str):
    """The final stated integer answer: whichever comes LAST in the text among (a) an integer following 'answer:'
    (case-insensitive) on the same line and (b) the integer inside a \\boxed{...}. None if neither exists.
    Written independently of the executor's `ansline` (diagnostic only)."""
    cands = []
    low = text.lower()
    for m in re.finditer(r"answer:", low):
        eol = text.find("\n", m.end())
        seg = text[m.end(): eol if eol >= 0 else len(text)]
        seg = seg.replace("\\,", "").replace("{,}", "")
        n = _NUM.search(seg)
        if n:
            cands.append((m.start(), int(n.group(0).replace(",", ""))))
    for m in re.finditer(r"\\boxed\{", text):
        depth, j, buf = 1, m.end(), []
        while j < len(text) and depth:
            ch = text[j]
            depth += ch == "{"
            depth -= ch == "}"
            if depth:
                buf.append(ch)
            j += 1
        n = _NUM.search("".join(buf).replace("{,}", "").replace("\\,", ""))
        if n:
            cands.append((m.start(), int(n.group(0).replace(",", ""))))
    return max(cands)[1] if cands else None


# ---------------------------------------------------------------- data
def problems(with_probe=True):
    d = {r["pid"]: r for r in map(json.loads, open(ROOT / "olmo_pilot" / "problems.jsonl"))}
    if with_probe:  # phase P samples Dolci prompts (olmo_pilot/probe_prompts.jsonl); used for lengths only
        d.update({r["pid"]: r for r in map(json.loads, open(ROOT / "olmo_pilot" / "probe_prompts.jsonl"))})
    return d


def graded(job):
    f = ART / "graded" / f"{job}.jsonl"
    return [json.loads(l) for l in open(f)] if f.exists() else None


def samples(job):
    """Yield sample rows of a gzip JSONL; tolerate a truncated tail (killed job)."""
    f = ART / "samples" / f"{job}.jsonl.gz"
    if not f.exists():
        return
    with gzip.open(f, "rt") as g:
        while True:
            try:
                ln = g.readline()
            except (EOFError, zlib.error, OSError):
                return
            if not ln:
                return
            try:
                yield json.loads(ln)
            except json.JSONDecodeError:
                return


def ids_of(row):
    import numpy as np
    return np.frombuffer(base64.b64decode(row["ids"]), dtype=np.int32).tolist()


# pid -> paper position (1..15); AIME problems are numbered 1-15 within each paper
def paper_pos(pid):
    n = int(pid.rsplit("_", 1)[1])
    return (n - 1) % 15 + 1


HEADLINE_SETS = ("aime2024", "aime2025", "aime2026")
