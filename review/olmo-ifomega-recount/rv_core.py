"""Reviewer kit, run olmo-ifomega (2026-11-06): loaders and the answer split. Independent of olmo_ifomega/.

Reads the executor's raw sample files (read-only) from the phase-1 workspace; writes only under this directory or
~/review/oif_rv/."""
import gzip
import json
import os
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.expanduser("~/review/olmo-ifomega")           # phase-1 workspace (hard links: never write there)
ART = os.path.join(WS, "artifacts", "olmo_ifomega")
SAMPLES = os.path.join(ART, "samples")
OUT = os.path.join(HERE, "out")
BIG = os.path.expanduser("~/review/oif_rv")                # scratch, not committed
CAP = 32768


def load_problems(stage0=False):
    fn = "stage0_problems.jsonl" if stage0 else "problems.jsonl"
    return {r["pid"]: r for r in map(json.loads, open(os.path.join(WS, "olmo_ifomega", fn)))}


def iter_gz_lines(path, bs=1 << 20):
    """Stream complete decoded lines of a (possibly multi-member, possibly truncated) gzip file; record damage in
    iter_gz_lines.damage[path] (members, truncation, partial last line)."""
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


def answer_of(text):
    """Pre-registered answer: the text after the last '</think>', whitespace-stripped; None when there is none."""
    k = text.rfind("</think>")
    if k < 0:
        return None
    return text[k + len("</think>"):].strip()


def load_regrade(job):
    """My re-graded rows of one job: out/regrade/<job>.jsonl (local), else the committed out/regrade_all.jsonl.gz."""
    fn = os.path.join(OUT, "regrade", f"{job}.jsonl")
    if os.path.exists(fn):
        return [json.loads(x) for x in open(fn)]
    with gzip.open(os.path.join(OUT, "regrade_all.jsonl.gz"), "rt") as f:
        return [r for r in map(json.loads, f) if r["job"] == job]
