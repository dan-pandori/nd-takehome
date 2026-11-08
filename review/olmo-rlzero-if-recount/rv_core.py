"""Reviewer kit, run olmo-rlzero-if (2026-11-08): paths, loaders, RL's answer extraction. Independent of olmo_rlzero_if/.

Reads the executor's raw files read-only from the phase-1 workspace ~/review/olmo-rlzero-if (hard links: never write
there); writes only under this directory (out/) or the scratch ~/review/rzi_rv/ (not committed)."""
import ast
import base64
import gzip
import json
import os
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.expanduser("~/review/olmo-rlzero-if")          # phase-1 workspace
ART = os.path.join(WS, "artifacts", "olmo_rlzero_if")
SAMPLES = os.path.join(ART, "samples")
OUT = os.path.join(HERE, "out")
BIG = os.path.expanduser("~/review/rzi_rv")                  # scratch
UP = os.path.join(BIG, "upstream")
CAP = 16384
TURN_IDS = (100257, 100264, 100265)                          # <|endoftext|> <|im_start|> <|im_end|> (both tokenizers)
THINK_OPEN, THINK_CLOSE, ANS_OPEN, ANS_CLOSE = 100268, 100269, 100274, 100275   # RL-Zero-IF tokenizer names


def load_problems(stage0=False):
    fn = "stage0_problems.jsonl" if stage0 else "problems.jsonl"
    return {r["pid"]: r for r in map(json.loads, open(os.path.join(WS, "olmo_rlzero_if", fn)))}


def iter_gz_lines(path, bs=1 << 20):
    """Complete decoded lines of a (possibly multi-member, possibly truncated) gzip file; damage recorded in
    iter_gz_lines.damage[path]."""
    damage, members = [], 1
    d = zlib.decompressobj(16 + zlib.MAX_WBITS)
    buf = b""
    started = False
    with open(path, "rb") as f:
        pending = f.read(bs)
        while pending:
            try:
                out = d.decompress(pending)
                started = True
            except zlib.error as e:
                damage.append(f"zlib error in member {members}: {e}")
                break
            buf += out
            *lines, buf = buf.split(b"\n")
            for ln in lines:
                yield ln.decode("utf-8")
            if d.eof:
                rest = d.unused_data
                d = zlib.decompressobj(16 + zlib.MAX_WBITS)
                started = False
                pending = rest or f.read(bs)
                if pending:
                    members += 1
                continue
            pending = f.read(bs)
        else:
            if started and not d.eof:
                damage.append(f"truncated member {members}")
    if buf:
        damage.append(f"partial last line ({len(buf)} bytes)")
    damage.append(f"members={members}")
    iter_gz_lines.damage[path] = damage


iter_gz_lines.damage = {}


def iter_rows(job):
    path = os.path.join(SAMPLES, f"{job}.jsonl.gz")
    for ln in iter_gz_lines(path):
        try:
            yield json.loads(ln)
        except json.JSONDecodeError:
            iter_gz_lines.damage.setdefault(path, []).append("undecodable line")


def jobs():
    return sorted(f[: -len(".jsonl.gz")] for f in os.listdir(SAMPLES) if f.endswith(".jsonl.gz"))


def ids_of(row):
    import numpy as np
    return np.frombuffer(base64.b64decode(row["ids"]), dtype=np.int32).tolist()


def _upstream_fn(path, name):
    src = open(path).read()
    node = next(n for n in ast.parse(src).body if isinstance(n, ast.FunctionDef) and n.name == name)
    ns = {}
    exec(ast.get_source_segment(src, node), ns)
    return ns[name]


# open-instruct ground_truth_utils.remove_thinking_section at d928a7c, executed from my own fetch of the file
remove_thinking_section = _upstream_fn(os.path.join(UP, "oi_d928a7c", "open_instruct", "ground_truth_utils.py"),
                                       "remove_thinking_section")


def load_regrade(job):
    fn = os.path.join(OUT, "regrade", f"{job}.jsonl")
    if os.path.exists(fn):
        return [json.loads(x) for x in open(fn)]
    with gzip.open(os.path.join(OUT, "regrade_all.jsonl.gz"), "rt") as f:
        return [r for r in map(json.loads, f) if r["job"] == job]
