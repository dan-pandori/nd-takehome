#!/usr/bin/env python3
"""Problems files of run olmo-iffu (pre-registration preregistration/olmo-iffu.md), from olmo_ifomega/problems.jsonl.

problems_geo.jsonl   test 1: the three perpendicular-diagonal reach prompts; perp_055's label corrected 17 -> 15
                     (olmo_iffu/label_check.py), the stored one kept as answer_stored.
problems_hint.jsonl  test 2 / 2b: the 16 IF prompts with prompt_sample = prompt + "\\n\\n" + HINT (the user turn sent);
                     prompt and kwargs unchanged, so grading is the official checker on the original item.
Tests 3 and 4 sample olmo_ifomega/problems.jsonl itself (the original prompts).
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from subsets import GEO3, IFEVAL3, subsets  # noqa: E402

HINT = "Answer in at most 60 words."
IFEVAL_CAPS3 = ["ifeval_1314", "ifeval_2247", "ifeval_2563"]  # test 2b (beyond the brief): the all-caps reach prompts
CORRECTED = {"omega_out_geometry_perpendicular_intersection_test_out_055": "15"}


def main():
    probs = {r["pid"]: r for r in map(json.loads, open(HERE.parent / "olmo_ifomega" / "problems.jsonl"))}
    with open(HERE / "problems_geo.jsonl", "w") as f:
        for pid in GEO3:
            r = dict(probs[pid])
            if pid in CORRECTED:
                r["answer_stored"], r["answer"] = r["answer"], CORRECTED[pid]
            f.write(json.dumps(r) + "\n")
    t2, _ = subsets()
    with open(HERE / "problems_hint.jsonl", "w") as f:
        for pid in IFEVAL3 + IFEVAL_CAPS3 + t2:
            r = dict(probs[pid])
            r["prompt_sample"] = r["prompt"] + "\n\n" + HINT
            r["hint"] = HINT
            f.write(json.dumps(r) + "\n")
    print("wrote problems_geo.jsonl (3), problems_hint.jsonl", len(IFEVAL3 + IFEVAL_CAPS3 + t2))


if __name__ == "__main__":
    main()
