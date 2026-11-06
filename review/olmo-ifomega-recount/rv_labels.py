"""Independent answers for every OMEGA test_out candidate problem (reach / reverse under omega or rl), compared with
the official ground truth. Output: out/labels.txt

geometry_perpendicular_intersection: regular n-gon, vertex k at angle 2*pi*k/n (orientation is irrelevant). Chords
  (a,b), (c,d) are perpendicular iff (a+b) - (c+d) = n/2 (mod n). Counted two ways: every perpendicular pair
  ("all"), and only pairs whose segments meet in the closed polygon: a shared endpoint or a proper crossing ("meet").
combinatory: exact enumeration over draws of 5 letter instances (all C(N,5) subsets equally likely), every order of
  the drawn word equally likely, then a uniformly random permutation of positions; letter-level 'stays in place'
  (position i holds the letter both before and after).
func_intersection_coords: dense bisection of f - g on [-10, 10] (mpmath, 50 digits near roots).
geometry_basic: direct construction with numpy (rotations counterclockwise).
"""
import itertools
import json
import math
import os
from fractions import Fraction

import numpy as np

import rv_core as C

lines = []


def say(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    lines.append(s)


def perp_counts(n, chords):
    chords = [tuple(sorted(c)) for c in chords]
    assert len(set(chords)) == len(chords)

    def cross(c1, c2):
        a, b = c1
        c, d = c2
        if len({a, b, c, d}) < 4:
            return "shared"
        inside = lambda x: a < x < b  # noqa: E731
        return "cross" if inside(c) != inside(d) else "apart"

    allp = meet = 0
    for c1, c2 in itertools.combinations(chords, 2):
        if ((c1[0] + c1[1]) - (c2[0] + c2[1])) % n * 2 == n:  # difference = n/2 mod n
            allp += 1
            if cross(c1, c2) in ("shared", "cross"):
                meet += 1
    # numeric check of the perpendicularity criterion
    ang = lambda k: 2 * math.pi * k / n  # noqa: E731
    num = 0
    for c1, c2 in itertools.combinations(chords, 2):
        v1 = np.array([math.cos(ang(c1[1])) - math.cos(ang(c1[0])), math.sin(ang(c1[1])) - math.sin(ang(c1[0]))])
        v2 = np.array([math.cos(ang(c2[1])) - math.cos(ang(c2[0])), math.sin(ang(c2[1])) - math.sin(ang(c2[0]))])
        if abs(v1 @ v2) < 1e-9 * np.linalg.norm(v1) * np.linalg.norm(v2):
            num += 1
    assert num == allp, (num, allp)
    return allp, meet


def parse_geom(prompt):
    import re
    n = int(re.search(r"have a (\d+)-gon", prompt).group(1))
    ch = [(int(a), int(b)) for a, b in re.findall(r"from vertex (\d+) to vertex (\d+)", prompt)]
    return n, ch


def comb_prob(ms, k, event):
    """ms: dict letter -> count; draw k instances; event(word, perm_word) -> bool."""
    inst = [l for l, c in ms.items() for _ in range(c)]
    tot = Fraction(0)
    nsub = 0
    for sub in itertools.combinations(range(len(inst)), k):
        nsub += 1
        letters = [inst[i] for i in sub]
        orders = list(itertools.permutations(range(k)))
        acc = Fraction(0)
        for o in orders:  # the formed word (every order equally likely)
            w = [letters[i] for i in o]
            hit = sum(1 for p in orders if event(w, [w[i] for i in p]))
            acc += Fraction(hit, len(orders))
        tot += acc / len(orders)
    return tot / nsub


def fixed_count(w, v, letter):
    return sum(1 for a, b in zip(w, v) if a == letter and b == letter)


def lte_qr(p, e):
    mod = p ** e
    sols = [m for m in range(1, mod + 1) if (m * m * m * m + 1) % mod == 0]
    return len(sols), min(sols)


def func_coords_011():
    import mpmath as mp
    mp.mp.dps = 50

    def f(x):
        c = mp.cos(3 * mp.pi * (2 * abs(x + 2) - 3) + 3)
        return 5 * (1 * (1 * c + 1) ** 2 + 3 * (1 * c + 1) + 2) + 2

    def g(x):
        h = (-1 * (-2 * x + 3) - 2) / (-3 * (-2 * x + 3) - 1)
        return 2 * h ** 2 + 3 * h + 5

    xs = np.linspace(-10, 10, 2_000_001)
    roots = []
    # vectorised float scan, then refine sign changes away from the pole with mpmath bisection
    with np.errstate(divide="ignore", invalid="ignore"):
        c = np.cos(3 * np.pi * (2 * np.abs(xs + 2) - 3) + 3)
        F = 5 * ((c + 1) ** 2 + 3 * (c + 1) + 2) + 2
        h = (-1 * (-2 * xs + 3) - 2) / (-3 * (-2 * xs + 3) - 1)
        G = 2 * h ** 2 + 3 * h + 5
        D = F - G
    pole = 5 / 3
    for i in range(len(xs) - 1):
        if not (np.isfinite(D[i]) and np.isfinite(D[i + 1])):
            continue
        if (xs[i] - pole) * (xs[i + 1] - pole) <= 0:
            continue
        if D[i] == 0 or D[i] * D[i + 1] < 0:
            a, b = mp.mpf(xs[i]), mp.mpf(xs[i + 1])
            for _ in range(80):
                m = (a + b) / 2
                if (f(a) - g(a)) * (f(m) - g(m)) <= 0:
                    b = m
                else:
                    a = m
            roots.append(float((a + b) / 2))
    return roots


def geometry_basic_010():
    def rot(p, c, a):
        d = p - c
        return c + np.array([d[0] * math.cos(a) - d[1] * math.sin(a), d[0] * math.sin(a) + d[1] * math.cos(a)])

    def refl_point(p, c):
        return 2 * c - p

    def refl_line(p, a, b):  # reflect p across line through a, b
        d = (b - a) / np.linalg.norm(b - a)
        q = p - a
        return a + 2 * (q @ d) * d - q

    def inter(p1, p2, p3, p4):
        A = np.array([p2 - p1, -(p4 - p3)]).T
        t = np.linalg.solve(A, p3 - p1)
        return p1 + t[0] * (p2 - p1)

    out = {}
    for U in (np.array([0.0, 0.0]),):
        K = U + np.array([4.0, 0.0])
        J = (U + K) / 2
        D = rot(J, K, 3 * math.pi / 4)
        # bisector of angle JKD at K: direction = unit(KJ) + unit(KD)
        u1 = (J - K) / np.linalg.norm(J - K)
        u2 = (D - K) / np.linalg.norm(D - K)
        G1, G2 = K, K + (u1 + u2)
        M1, M2 = refl_point(G1, U), refl_point(G2, U)  # reflection of line G through point U
        N = K - U
        W = refl_point(J, K)
        B = rot(D, K, 5 * math.pi / 12)
        V = (J + D) / 2
        T = B + N
        Q = rot(W, U, math.pi / 6)
        Z = refl_point(T, U)
        A = refl_line(Q, G1, G2)
        L = W + N
        O = rot(Q, Z, math.pi / 6)
        Pv = W - U
        I = rot(O, D, math.pi / 12)
        R = J + Pv
        H = refl_line(I, M1, M2)
        Cc = inter(Q, L, A, K)
        E = refl_line(H, R, V)
        Y = (K + H) / 2
        F = (Y + Cc) / 2
        out["FE"] = float(np.linalg.norm(F - E))
    return out


def main():
    P = C.load_problems()
    S = json.load(open(os.path.join(C.OUT, "stats.json")))
    k = "omega_out|headline"
    pids = sorted(set(S[k]["omega"]["R"]) | set(S[k]["rl"]["R"]) | set(S[k]["omega"]["V"]) | set(S[k]["rl"]["V"]))
    res = {}
    for p in pids:
        r = P[p]
        fam = r["family"]
        lab = r["answer"]
        if fam == "geometry_perpendicular_intersection":
            n, ch = parse_geom(r["prompt"])
            a, m = perp_counts(n, ch)
            res[p] = {"label": lab, "all_perpendicular_pairs": a, "meeting_in_closed_polygon": m}
        elif fam == "combinatory_probability_exactly_n_specific_fixed":
            import re
            ms = {a: int(b) for a, b in re.findall(r"(\w): (\d+)", r["prompt"].split("{")[1].split("}")[0])}
            mm = re.search(r"exact (\d+) letter '(\w)'", r["prompt"])
            kk, let = int(mm.group(1)), mm.group(2)
            pr = comb_prob(ms, 5, lambda w, v: fixed_count(w, v, let) == kk)
            res[p] = {"label": lab, "prob": str(pr), "m+n": pr.numerator + pr.denominator}
        elif fam == "combinatory_probability_no_specific_letter_fixed":
            import re
            ms = {a: int(b) for a, b in re.findall(r"(\w): (\d+)", r["prompt"].split("{")[1].split("}")[0])}
            let = re.search(r"no letter '(\w)'", r["prompt"]).group(1)
            pr = comb_prob(ms, 5, lambda w, v: fixed_count(w, v, let) == 0)
            res[p] = {"label": lab, "prob": str(pr), "m+n": pr.numerator + pr.denominator}
        elif fam == "numbertheory_lte_qr":
            n_, m_ = lte_qr(41, 3)
            res[p] = {"label": lab, "N": n_, "M": m_, "N+M": n_ + m_}
        elif fam == "arithmetic_list_prime_factors":
            x = 738015871
            fs, d, y = [], 2, x
            while d * d <= y:
                while y % d == 0:
                    fs.append(d)
                    y //= d
                d += 1
            if y > 1:
                fs.append(y)
            ps = sorted(set(fs))
            res[p] = {"label": lab, "factors": fs, "second_largest": ps[-2]}
        elif fam == "algebra_func_intersection_coords":
            roots = func_coords_011()
            res[p] = {"label": lab, "n_roots": len(roots), "first_roots": [round(x, 6) for x in roots[:4]],
                      "first_rounded": round(roots[0])}
        elif fam == "geometry_basic":
            res[p] = {"label": lab, **geometry_basic_010()}
        say(p.replace("omega_out_", ""), json.dumps(res[p]))
    json.dump(res, open(os.path.join(C.OUT, "labels.json"), "w"), indent=1)
    open(os.path.join(C.OUT, "labels.txt"), "w").write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
