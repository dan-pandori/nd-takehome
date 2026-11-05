#!/usr/bin/env python3
"""Repair a samples file that a resumed job appended to after a truncated gzip member.

A sampler killed mid-write leaves its gzip member without its final block; sample.py resumed from such a file (it read
the complete rows) and appended a new member after the broken one, so plain gzip readers stop with "invalid block
type" at the junction. This recovers every complete JSON row from the broken member (decompressed up to the cut) and
from each later member, checks that every (pid, chunk) group is whole and appears once, and writes a clean file.
Usage: repair_gz.py <in.jsonl.gz> <out.jsonl.gz> [chunk]
"""
import gzip
import json
import sys
import zlib
from collections import Counter


def members(raw):
    """Split raw bytes into gzip members: a member ends where zlib reports end of stream; a truncated member is
    followed by the next b'\\x1f\\x8b\\x08' at which a full decompression succeeds."""
    out, pos = [], 0
    while pos < len(raw):
        d = zlib.decompressobj(wbits=31)
        try:
            data = d.decompress(raw[pos:])
            if d.eof:
                out.append(data)
                pos = len(raw) - len(d.unused_data)
                continue
            out.append(data)  # stream ran out without an end marker: the last member, truncated
            break
        except zlib.error:
            # broken member: keep what decompresses before the cut, then resume at the next member that decodes
            d2 = zlib.decompressobj(wbits=31)
            good = b""
            step = 1 << 16
            for k in range(pos, len(raw), step):
                saved = d2.copy()
                try:
                    good += d2.decompress(raw[k:k + step])
                except zlib.error:
                    d2 = saved  # re-feed the failing block byte by byte: keep every byte decoded before the cut
                    for b in range(k, min(k + step, len(raw))):
                        try:
                            good += d2.decompress(raw[b:b + 1])
                        except zlib.error:
                            break
                    break
            out.append(good)
            nxt = pos + 1
            while True:
                nxt = raw.find(b"\x1f\x8b\x08", nxt)
                if nxt < 0:
                    return out
                try:
                    zlib.decompressobj(wbits=31).decompress(raw[nxt:nxt + (1 << 20)])
                    break
                except zlib.error:
                    nxt += 1
            pos = nxt
    return out


def main():
    src, dst = sys.argv[1], sys.argv[2]
    chunk = int(sys.argv[3]) if len(sys.argv) > 3 else 4
    rows = []
    for data in members(open(src, "rb").read()):
        for ln in data.decode("utf-8", errors="strict").split("\n"):
            if not ln.strip():
                continue
            try:
                rows.append(json.loads(ln))
            except json.JSONDecodeError:
                pass  # the cut line of a truncated member
    cnt = Counter((r["pid"], r["chunk"]) for r in rows)
    seen = Counter((r["pid"], r["chunk"], r["i"]) for r in rows)
    dup = sum(v > 1 for v in seen.values())
    bad = {k: v for k, v in cnt.items() if v != chunk}
    print(f"{len(rows)} rows, {len(cnt)} chunks, {dup} duplicated (pid, chunk, i), {len(bad)} chunks not of size "
          f"{chunk}: {list(bad.items())[:5]}")
    if dup:
        raise SystemExit("duplicate rows: not writing")
    with gzip.open(dst, "wt") as g:
        for r in rows:
            g.write(json.dumps(r) + "\n")
    print("wrote", dst)


if __name__ == "__main__":
    main()
