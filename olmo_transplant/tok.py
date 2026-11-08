"""Torch-free decoder for the Olmo 3 tokenizer (byte-level BPE; tokenizer.json read directly), used on the VPS to
locate `</think>` in stored token ids and to check inserted prefixes without transformers."""
import base64
import json
import os

import numpy as np

TOKJ = os.environ.get("OLMO_TOKJ", "/home/dan/.cache/huggingface/hub/models--allenai--Olmo-3-32B-Think-DPO/snapshots/"
                      "97604023f2602a7dfe6d31b1fc229985e0002022/tokenizer.json")


def _byte_decoder():
    bs = list(range(ord("!"), ord("~") + 1)) + list(range(ord("¡"), ord("¬") + 1)) + list(range(ord("®"), ord("ÿ") + 1))
    cs = bs[:]
    n = 0
    for b in range(256):
        if b not in bs:
            bs.append(b)
            cs.append(256 + n)
            n += 1
    return {chr(c): b for b, c in zip(bs, cs)}


class Tok:
    def __init__(self, path=TOKJ):
        tj = json.load(open(path))
        bd = _byte_decoder()
        self.special = {a["id"] for a in tj["added_tokens"] if a["special"]}
        self.piece = {}
        for s, i in tj["model"]["vocab"].items():
            self.piece[i] = bytes(bd[ch] for ch in s)
        for a in tj["added_tokens"]:
            self.piece[a["id"]] = a["content"].encode()

    def bytes_of(self, ids, skip_special=True):
        return b"".join(self.piece[i] for i in ids if not (skip_special and i in self.special))

    def decode(self, ids, skip_special=True):
        return self.bytes_of(ids, skip_special).decode("utf-8", errors="replace")


def ids_of(rec):
    return np.frombuffer(base64.b64decode(rec["ids"]), dtype=np.int32).tolist()


def think_end(tok, ids, marker=b"</think>"):
    """First occurrence of the marker in the bytes of ids: (k, clean, tail) with k the smallest token count whose
    bytes contain it, clean = the k-th token ends exactly at the marker, tail = bytes after it inside that token.
    None if absent."""
    pieces = [b"" if i in tok.special else tok.piece[i] for i in ids]
    j = b"".join(pieces).find(marker)
    if j < 0:
        return None
    end = j + len(marker)
    pos = 0
    for k, pc in enumerate(pieces, 1):
        pos += len(pc)
        if pos >= end:
            return k, pos == end, b"".join(pieces[:k])[end:]
    return None
