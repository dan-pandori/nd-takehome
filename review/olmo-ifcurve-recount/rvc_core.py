"""Reviewer kit for run olmo-ifcurve: shared loaders (written by the reviewer; no executor module is imported).

Adapted from my olmo-ifladder kit (review/olmo-ifladder-recount/rvl_core.py). Raw inputs are read read-only from the
phase-1 workspace ~/review/olmo-ifcurve (hard links into the run's worktree: never write there). Stored source
samples reused by the run (olmo-ifomega F_*_ifb, olmo-iffu T4 / T4b) are my own bucket copies in
~/review/oifc_rv/src (F_dpo_ifb / F_s2300_ifb are links to my olmo-transplant review's copies). Scratch (upstream
checker fetch, tokenizer files, hand-check item texts, reader output) is ~/review/oifc_rv; outputs go to out/.
"""
import base64
import csv
import gzip
import hashlib
import json
import struct
import zlib
from pathlib import Path

RAW = Path.home() / "review" / "olmo-ifcurve"
ART = RAW / "artifacts" / "olmo_ifcurve"
CODE = RAW / "olmo_ifcurve"
SCR = Path.home() / "review" / "oifc_rv"
SRC = SCR / "src"
KIT = Path(__file__).resolve().parent
OUT = KIT / "out"
OUT.mkdir(exist_ok=True)
TOKJ = SCR / "tok" / "allenai_Olmo-3-32B-Think-DPO" / "tokenizer.json"

# sampling jobs of this run (samples in ART/samples) and reused stored jobs (my copies in SRC)
NEW_JOBS = sorted(p.name[:-len(".jsonl.gz")] for p in (ART / "samples").glob("*.jsonl.gz"))
OLD_JOBS = ["F_dpo_ifb", "F_s0100_ifb", "F_s0750_ifb", "F_s2300_ifb", "T4_s0750", "T4b_s0750"]
ALL_JOBS = OLD_JOBS + NEW_JOBS
STEP = {"dpo": 0, "s0050": 50, "s0100": 100, "s0200": 200, "s0350": 350, "s0500": 500, "s0750": 750,
        "s1100": 1100, "s1600": 1600, "s2300": 2300}
NEVER = 9999


def job_path(job):
    return (SRC if job in OLD_JOBS else ART / "samples") / f"{job}.jsonl.gz"


def iter_gz(path, report=None):
    """Stream complete JSON rows of a gzip JSONL file; a truncated tail or bad line is counted, never hidden."""
    rep = report if report is not None else {}
    rep.update({"rows": 0, "bad_lines": 0, "truncated_tail": False})
    try:
        with gzip.open(path, "rt", encoding="utf-8") as f:
            for ln in f:
                if not ln.strip():
                    continue
                try:
                    r = json.loads(ln)
                except json.JSONDecodeError:
                    rep["bad_lines"] += 1
                    continue
                rep["rows"] += 1
                yield r
    except (EOFError, gzip.BadGzipFile, zlib.error):
        rep["truncated_tail"] = True


def iter_job(job, report=None, with_ids=False):
    for r in iter_gz(job_path(job), report):
        if not with_ids:
            r.pop("ids", None)
        yield r


def load_jsonl(path):
    with open(path) as f:
        return [json.loads(ln) for ln in f if ln.strip()]


def load_csv(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def unb64(s):
    b = base64.b64decode(s)
    return list(struct.unpack(f"<{len(b) // 4}i", b))


def sha_int32(ids):
    """sha256 of the ids as little-endian int32 bytes (the sampler's prompt-hash convention, re-implemented)."""
    return hashlib.sha256(struct.pack(f"<{len(ids)}i", *ids)).hexdigest()


def sha_text(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def answer_of(text):
    """Pre-registered answer: the text after the LAST '</think>', stripped; None without '</think>'."""
    k = text.rfind("</think>")
    if k < 0:
        return None
    return text[k + len("</think>"):].strip()


def thinking_of(text):
    """Text before the FIRST '</think>' (None without one)."""
    k = text.find("</think>")
    return None if k < 0 else text[:k]


def wsnorm(s):
    return " ".join(s.split())


def upstream_ifbench():
    """IFBench (allenai/IFBench @ cd189a9c) records from my own fetch, keyed by key."""
    return {str(r["key"]): r for r in load_jsonl(SCR / "upstream" / "ifbench" / "IFBench_test.jsonl")}


def upstream_ifeval():
    """IFEval (google-research instruction_following_eval @ e6890f85 data/input_data.jsonl), keyed by key."""
    return {str(r["key"]): r for r in load_jsonl(SCR / "upstream" / "ife" / "input_data.jsonl")}


def upstream_record(pid, _cache={}):
    if not _cache:
        for k, r in upstream_ifbench().items():
            _cache[f"ifbench_{k}"] = ("ifbench", r)
        for k, r in upstream_ifeval().items():
            _cache[f"ifeval_{k}"] = ("ifeval", r)
    return _cache[pid]


# ---------------------------------------------------------------- my own byte-level BPE piece table
def _bytes_to_unicode():
    """GPT-2 byte <-> unicode map (written from the algorithm's definition)."""
    keep = list(range(0x21, 0x7F)) + list(range(0xA1, 0xAD)) + list(range(0xAE, 0x100))
    mp, extra = {}, 0
    for b in range(256):
        if b in keep:
            mp[b] = chr(b)
        else:
            mp[b] = chr(256 + extra)
            extra += 1
    return {v: k for k, v in mp.items()}


class Pieces:
    def __init__(self, path=TOKJ):
        tj = json.load(open(path))
        inv = _bytes_to_unicode()
        self.piece = {}
        for s, i in tj["model"]["vocab"].items():
            self.piece[i] = bytes(inv[c] for c in s)
        self.special = set()
        for a in tj["added_tokens"]:
            self.piece[a["id"]] = a["content"].encode()
            if a["special"]:
                self.special.add(a["id"])

    def bytes_of(self, ids, skip_special=True):
        return b"".join(self.piece[i] for i in ids if not (skip_special and i in self.special))

    def text(self, ids, skip_special=True):
        return self.bytes_of(ids, skip_special).decode("utf-8", errors="replace")

    def first_close(self, ids, marker=b"</think>"):
        """Smallest k such that the bytes of ids[:k] (special tokens dropped) contain the marker; None if absent."""
        acc = bytearray()
        for k, i in enumerate(ids, 1):
            if i in self.special:
                continue
            before = len(acc)
            acc += self.piece[i]
            if marker in acc[max(0, before - len(marker) + 1):]:
                return k
        return None


def dump(obj, name):
    p = OUT / name
    with open(p, "w") as f:
        json.dump(obj, f, indent=1, sort_keys=True, default=str)
    return p


class Tee:
    """print to stdout and to out/<name>"""

    def __init__(self, name):
        self.f = open(OUT / name, "w")

    def __call__(self, *a):
        s = " ".join(str(x) for x in a)
        print(s)
        self.f.write(s + "\n")
        self.f.flush()
