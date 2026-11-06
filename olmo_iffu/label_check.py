#!/usr/bin/env python3
"""Recompute the answers of the three OMEGA perpendicular-diagonal reach prompts (run olmo-iffu, test 1).

Regular n-gon, vertices 1..n counterclockwise. Chord (i, j) has direction angle pi(i + j)/n + pi/2 (+ a constant), so
chords (i, j), (k, l) are perpendicular iff (i + j - k - l) = n/2 (mod n). Two drawn diagonals "meet within the interior
or on the boundary" iff their endpoints interleave (interior crossing) or they share an endpoint (a vertex). A second,
independent float computation (segment intersection + dot product) must agree. Prints one line per prompt;
--pairs also lists each prompt's reference set of pairs.
"""
import itertools
import json
import math
import re
import sys

PIDS = ["omega_out_geometry_perpendicular_intersection_test_out_055",
        "omega_out_geometry_perpendicular_intersection_test_out_068",
        "omega_out_geometry_perpendicular_intersection_test_out_069"]


def parse(prompt):
    n = int(re.search(r"a (\d+)-gon", prompt).group(1))
    segs = [tuple(map(int, m)) for m in re.findall(r"from vertex (\d+) to vertex (\d+)", prompt)]
    return n, segs


def exact_pairs(n, segs):
    S = sorted({tuple(sorted(s)) for s in segs})
    out = []
    for (a, b), (c, d) in itertools.combinations(S, 2):
        if (a + b - c - d) % n != (n // 2) % n or n % 2:
            continue
        share = len({a, b} & {c, d}) > 0
        inter = (a < c < b) != (a < d < b) and not share
        if share or inter:
            out.append(((a, b), (c, d), "vertex" if share else "interior"))
    return out


def exact(n, segs):
    return len(exact_pairs(n, segs)), len({tuple(sorted(s)) for s in segs}), len(segs)


def flt(n, segs):
    P = {k: (math.cos(2 * math.pi * (k - 1) / n), math.sin(2 * math.pi * (k - 1) / n)) for k in range(1, n + 1)}
    S = sorted({tuple(sorted(s)) for s in segs})

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    def meet(p1, p2, p3, p4, eps=1e-9):
        d1, d2, d3, d4 = cross(p3, p4, p1), cross(p3, p4, p2), cross(p1, p2, p3), cross(p1, p2, p4)
        if ((d1 > eps and d2 < -eps) or (d1 < -eps and d2 > eps)) and ((d3 > eps and d4 < -eps) or (d3 < -eps and d4 > eps)):
            return True
        return any(math.dist(x, y) < 1e-9 for x in (p1, p2) for y in (p3, p4))

    cnt = 0
    for (a, b), (c, d) in itertools.combinations(S, 2):
        u = (P[b][0] - P[a][0], P[b][1] - P[a][1]); v = (P[d][0] - P[c][0], P[d][1] - P[c][1])
        if abs(u[0] * v[0] + u[1] * v[1]) < 1e-9 and meet(P[a], P[b], P[c], P[d]):
            cnt += 1
    return cnt


def main(*argv):
    pairs = "--pairs" in argv
    problems = next((a for a in argv if not a.startswith("--")), "olmo_ifomega/problems.jsonl")
    probs = {r["pid"]: r for r in map(json.loads, open(problems))}
    for pid in PIDS:
        n, segs = parse(probs[pid]["prompt"])
        e, nd, ns = exact(n, segs)
        print(f"{pid[-3:]} n={n} drawn={ns} distinct={nd} exact={e} float={flt(n, segs)} stored_label={probs[pid]['answer']}")
        if pairs:
            for (a, b), (c, d), where in exact_pairs(n, segs):
                print(f"    {a}-{b} _|_ {c}-{d}  ({where})")


if __name__ == "__main__":
    main(*sys.argv[1:])
