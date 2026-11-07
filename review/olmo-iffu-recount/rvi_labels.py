"""My own answers for the three OMEGA perpendicular-diagonal prompts of test 1 (two independent ways).

(a) chord rule: in a regular n-gon, chords {i,j} and {k,l} are perpendicular iff (i + j - k - l) = n/2 (mod n);
    they meet inside the polygon iff their endpoints interleave on the circle, on the boundary iff they share a vertex.
(b) float geometry: vertices on the unit circle, |cos angle| < 1e-9, and the segments' intersection point lies on both
    segments (interior crossing or a shared endpoint).
The reference pair set (both ways must agree) is written for the hand gate's crux check.
-> out/labels.json, out/labels.txt
"""
import itertools
import json
import math
import re

import rvi_core as C

PIDS = ["omega_out_geometry_perpendicular_intersection_test_out_055",
        "omega_out_geometry_perpendicular_intersection_test_out_068",
        "omega_out_geometry_perpendicular_intersection_test_out_069"]


def parse(prompt):
    n = int(re.search(r"have a (\d+)-gon", prompt).group(1))
    diags = [(int(a), int(b)) for a, b in re.findall(r"from vertex (\d+) to vertex (\d+)", prompt)]
    return n, diags


def interleave(a, b, c, d, n):
    def between(x, lo, hi):  # strictly inside the arc lo -> hi counterclockwise
        return 0 < (x - lo) % n < (hi - lo) % n
    return between(c, a, b) != between(d, a, b) and len({a, b, c, d}) == 4


def rule_pairs(n, diags):
    out = set()
    for (i, (a, b)), (j, (c, d)) in itertools.combinations(enumerate(diags), 2):
        if (a + b - c - d) % n != (n // 2) % n or n % 2:
            continue
        shared = len({a, b} & {c, d}) == 1
        if shared or interleave(a, b, c, d, n):
            out.add((i, j))
    return out


def geo_pairs(n, diags):
    P = {v: (math.cos(2 * math.pi * (v - 1) / n), math.sin(2 * math.pi * (v - 1) / n)) for v in range(1, n + 1)}
    out = set()
    for (i, (a, b)), (j, (c, d)) in itertools.combinations(enumerate(diags), 2):
        (x1, y1), (x2, y2), (x3, y3), (x4, y4) = P[a], P[b], P[c], P[d]
        ux, uy, vx, vy = x2 - x1, y2 - y1, x4 - x3, y4 - y3
        cos = (ux * vx + uy * vy) / math.hypot(ux, uy) / math.hypot(vx, vy)
        if abs(cos) > 1e-9:
            continue
        den = ux * vy - uy * vx
        t = ((x3 - x1) * vy - (y3 - y1) * vx) / den
        s = ((x3 - x1) * uy - (y3 - y1) * ux) / den
        eps = 1e-9
        if -eps <= t <= 1 + eps and -eps <= s <= 1 + eps:
            out.add((i, j))
    return out


def main():
    probs = {r["pid"]: r for r in C.load_jsonl(C.RAW / "olmo_iffu" / "problems_geo.jsonl")}
    res, lines = {"label": {}, "pairs": {}, "run_file": {}}, []
    for pid in PIDS:
        n, diags = parse(probs[pid]["prompt"])
        assert len(set(map(frozenset, diags))) == len(diags), "duplicate diagonal"
        assert all((b - a) % n not in (1, n - 1) for a, b in diags), "a side, not a diagonal"
        a, b = rule_pairs(n, diags), geo_pairs(n, diags)
        assert a == b, (pid, a ^ b)
        res["label"][pid] = str(len(a))
        res["pairs"][pid] = [[list(diags[i]), list(diags[j])] for i, j in sorted(a)]
        res["run_file"][pid] = {k: probs[pid].get(k) for k in ("answer", "answer_stored")}
        inside = sum(1 for i, j in a if len(set(diags[i]) & set(diags[j])) == 0)
        lines.append(f"{pid[-3:]}: n={n}, {len(diags)} diagonals; perpendicular meeting pairs {len(a)} "
                     f"({inside} crossing inside, {len(a) - inside} at a shared vertex); rule == geometry; "
                     f"run file answer {probs[pid].get('answer')} (stored {probs[pid].get('answer_stored')})")
        lines.append("   " + ", ".join(f"{diags[i][0]}-{diags[i][1]} x {diags[j][0]}-{diags[j][1]}" for i, j in sorted(a)))
    C.dump(res, "labels.json")
    (C.OUT / "labels.txt").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
