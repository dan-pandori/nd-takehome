"""Reviewer kit for run olmo-transplant: shared loaders (written by the reviewer; no executor module is imported).

Raw inputs are read read-only from the phase-1 workspace ~/review/olmo-transplant (hard links into the run's
worktree: never write there). Scratch (bucket copies of the olmo-ifomega source samples, upstream checker fetch,
tokenizer files, hand-check item texts) is ~/review/otr_rv; outputs go to out/.
"""
import base64
import gzip
import hashlib
import json
import struct
import zlib
from pathlib import Path

RAW = Path.home() / "review" / "olmo-transplant"
ART = RAW / "artifacts" / "olmo_transplant"
SCR = Path.home() / "review" / "otr_rv"
KIT = Path(__file__).resolve().parent
OUT = KIT / "out"
OUT.mkdir(exist_ok=True)
TOKJ = SCR / "tok" / "allenai_Olmo-3-32B-Think-DPO" / "tokenizer.json"

JOBS = ["R_dpo", "R_s2300", "C_dpo", "C_s2300", "F_s2300"]
SRC_JOBS = ["F_s2300_ifb", "C1_s2300_ifb", "C2_s2300_ifb", "F_dpo_ifb"]


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


def load_jsonl(path):
    with open(path) as f:
        return [json.loads(ln) for ln in f if ln.strip()]


def unb64(s):
    b = base64.b64decode(s)
    return list(struct.unpack(f"<{len(b) // 4}i", b))


def sha_int32(ids):
    """sha256 of the ids as little-endian int32 bytes (the sampler's input_sha256 convention, re-implemented)."""
    return hashlib.sha256(struct.pack(f"<{len(ids)}i", *ids)).hexdigest()


def sha_json(ids):
    """sha256 of json.dumps(list of ints) (traces.csv's ids_sha256 / prefix_sha256 convention)."""
    return hashlib.sha256(json.dumps([int(x) for x in ids]).encode()).hexdigest()


def answer_of(text):
    """Pre-registered answer: the text after the LAST '</think>', stripped; None without '</think>'."""
    k = text.rfind("</think>")
    if k < 0:
        return None
    return text[k + len("</think>"):].strip()


def wsnorm(s):
    return " ".join(s.split())


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
        self.vocab_size = len(self.piece)

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
            # a first occurrence must end inside the piece just added
            if marker in acc[max(0, before - len(marker) + 1):]:
                return k
        return None


def dump(obj, name):
    p = OUT / name
    with open(p, "w") as f:
        json.dump(obj, f, indent=1, sort_keys=True, default=str)
    return p


class Tee:
    """print to stdout and to out/<name>.txt"""

    def __init__(self, name):
        self.f = open(OUT / name, "w")

    def __call__(self, *a):
        s = " ".join(str(x) for x in a)
        print(s)
        self.f.write(s + "\n")
        self.f.flush()
