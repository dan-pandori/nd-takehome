#!/usr/bin/env python3
"""Seeded prompt subsets of run olmo-iffu (pre-registration preregistration/olmo-iffu.md, Design).

REACH43: the review's 43 IFBench hand-reach prompts (review_olmo-ifomega.md, "IFBench hand-reach prompts (strict
mapping, 43)"), sorted by IFBench index. Test 2 draws 10 with random.Random(SEED2) from REACH43 minus HINT_CONFLICT
(prompts whose complete answer needs more than the hint's 60 words); test 3 draws 10 with random.Random(SEED3) from the
33 prompts of REACH43 not in test 2's subset (disjoint by construction). Writes olmo_iffu/manifest.csv.
"""
import csv
import random
from pathlib import Path

REACH43 = sorted("""ifbench_0 ifbench_1 ifbench_128 ifbench_133 ifbench_136 ifbench_154 ifbench_166 ifbench_169 ifbench_170
ifbench_173 ifbench_179 ifbench_186 ifbench_187 ifbench_188 ifbench_189 ifbench_19 ifbench_203 ifbench_204 ifbench_206
ifbench_207 ifbench_209 ifbench_211 ifbench_217 ifbench_220 ifbench_226 ifbench_248 ifbench_252 ifbench_253 ifbench_264
ifbench_267 ifbench_268 ifbench_269 ifbench_271 ifbench_280 ifbench_281 ifbench_284 ifbench_290 ifbench_3 ifbench_4
ifbench_64 ifbench_67 ifbench_78 ifbench_79""".split(), key=lambda s: int(s.split("_")[1]))
HINT_CONFLICT = ["ifbench_281"]  # "List the countries of Africa in reverse alphabetical order, each on a new line": 54 names
IFEVAL3 = ["ifeval_2350", "ifeval_2447", "ifeval_3478"]  # the three letter-avoidance IFEval hand-reach prompts
GEO3 = ["omega_out_geometry_perpendicular_intersection_test_out_055",
        "omega_out_geometry_perpendicular_intersection_test_out_068",
        "omega_out_geometry_perpendicular_intersection_test_out_069"]
SEED2, SEED3 = 20261106, 20261107


def subsets():
    assert len(REACH43) == 43 == len(set(REACH43))
    elig2 = [p for p in REACH43 if p not in HINT_CONFLICT]
    t2 = random.Random(SEED2).sample(elig2, 10)
    rest = [p for p in REACH43 if p not in t2]
    t3 = random.Random(SEED3).sample(rest, 10)
    return t2, t3


def main():
    t2, t3 = subsets()
    rows = [("test1", p, "", i) for i, p in enumerate(GEO3)]
    rows += [("test2", p, "", i) for i, p in enumerate(IFEVAL3)]
    rows += [("test2", p, SEED2, i) for i, p in enumerate(t2)]
    rows += [("test3", p, SEED3, i) for i, p in enumerate(t3)]
    rows += [("test4", p, "", i) for i, p in enumerate(REACH43)]
    with open(Path(__file__).parent / "manifest.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["test", "pid", "seed", "draw_rank"])
        w.writerows(rows)
    print("test2 IFBench:", " ".join(t2))
    print("test3 IFBench:", " ".join(t3))


if __name__ == "__main__":
    main()
