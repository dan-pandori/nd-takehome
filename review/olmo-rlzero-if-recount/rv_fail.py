"""Format-check summary (Design 6) from my blind readers' classes (hand/fail_labels/*.json) and hand/fail_key.json.
Sets: `reach` = my six hand-reach prompts (headline); `strict_only` = the other strict-reach prompts (base 0 strict in
256, main open by gaming), labelled apart. Reports class shares for base and main failures, per prompt, mechanical tags
(cut at the cap, '</think>' present) and the prompts where >= 50 % of the base's sampled failures are (u).
Output: out/fail.json, out/fail.txt"""
import glob
import json
import os
from collections import Counter, defaultdict

import rv_core as C

REACH = ["ifbench_100", "ifbench_102", "ifbench_103", "ifbench_104", "ifbench_274", "ifeval_3272"]


def main():
    key = json.load(open(os.path.join(C.HERE, "hand", "fail_key.json")))
    lab = {}
    for f in sorted(glob.glob(os.path.join(C.HERE, "hand", "fail_labels", "*.json"))):
        for x in json.load(open(f)):
            lab[x["item"]] = x
    conf = {}
    cp = os.path.join(C.HERE, "hand", "fail_confirm.json")
    if os.path.exists(cp):
        conf = json.load(open(cp))
    res, lines = {"share": {}, "sets": {}}, []
    by = defaultdict(list)
    for iid, k in key.items():
        cls = conf.get(iid, {}).get("class") or lab.get(iid, {}).get("class")
        s = "reach" if k["pid"] in REACH else "strict_only"
        by[(s, k["model"])].append((k["pid"], cls, k["finish"] == "length"))
    for (s, m), xs in sorted(by.items()):
        c = Counter(x[1] for x in xs)
        n = len(xs)
        res["sets"][f"{s}|{m}"] = {"n": n, "classes": dict(c), "cut": sum(x[2] for x in xs)}
        lines.append(f"{s:11s} {m:5s} n {n:3d} " + " ".join(f"({k}) {c.get(k, 0)} = {c.get(k, 0) / n:.0%}"
                                                          for k in "uabcd") + f" | unlabelled {c.get(None, 0)} | cut {sum(x[2] for x in xs)}")
    base_reach = by[("reach", "base")]
    c = Counter(x[1] for x in base_reach)
    res["share"] = {k: c.get(k, 0) / max(1, len(base_reach)) for k in "uabcd"}
    lines.append("per prompt, base failures (classes):")
    pp = defaultdict(list)
    for (s, m), xs in by.items():
        if m == "base":
            for pid, cls, cut in xs:
                pp[pid].append(cls)
    res["per_prompt"] = {}
    for pid in sorted(pp):
        cc = Counter(pp[pid])
        res["per_prompt"][pid] = dict(cc)
        flag = "  >= 50 % (u)" if cc.get("u", 0) / len(pp[pid]) >= 0.5 else ""
        lines.append(f"   {pid:12s} {'reach' if pid in REACH else 'strict-only':11s} {dict(cc)}{flag}")
    json.dump(res, open(os.path.join(C.OUT, "fail.json"), "w"), indent=1)
    open(os.path.join(C.OUT, "fail.txt"), "w").write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
