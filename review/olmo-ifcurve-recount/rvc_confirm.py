"""Write my confirmations (hand/confirm.json) from the adjudicator proposals I accept.

usage: rvc_confirm.py ROUND [--reject item,item,...] [--set item=label:reason ...]
Every proposal of ROUND (adjudicator JSON in ~/review/oifc_rv/adjud/<ROUND>_*.json) is written as my confirmation
with its rule and reason, unless rejected (then the reader majority stands) or replaced by --set (my own label and
reason after reading the item myself). Each entry records the reads it overrides.
"""
import json
import sys

import rvc_hand as H
from rvc_core import SCR

ADJ = SCR / "adjud"


def main():
    rnd = sys.argv[1]
    rej = set()
    sets = {}
    args = sys.argv[2:]
    for i, a in enumerate(args):
        if a == "--reject":
            rej |= set(args[i + 1].split(","))
        if a == "--set":
            for s in args[i + 1:]:
                if s.startswith("--"):
                    break
                it, v = s.split("=", 1)
                lab, reason = v.split(":", 1)
                sets[it] = (lab, reason)
    rd = H.reads()
    byitem = {}
    for g, rs in rd.items():
        for r in rs:
            byitem[r[4]] = (g, rs)
    cf = H.HAND / "confirm.json"
    conf = json.load(open(cf)) if cf.exists() else {}
    n = {"accepted": 0, "rejected": 0, "set": 0}
    for f in sorted(ADJ.glob(f"{rnd}_*.json")):
        for x in json.load(open(f)):
            g, rs = byitem[x["item"]]
            key = json.dumps(list(g))
            reads = [r[1] for r in rs]
            if x["item"] in sets:
                lab, reason = sets[x["item"]]
                conf[key] = {"label": lab, "reason": f"reviewer read: {reason}", "reads": reads, "round": rnd}
                n["set"] += 1
            elif x["item"] in rej:
                n["rejected"] += 1
                conf.pop(key, None)
            else:
                conf[key] = {"label": x["proposed"], "reason": f"rule {x.get('rules')} ({x.get('confidence')}): "
                             f"{x.get('reason')}", "reads": reads, "round": rnd}
                n["accepted"] += 1
    json.dump(conf, open(cf, "w"), indent=1)
    print(rnd, n, "total confirmations", len(conf))


if __name__ == "__main__":
    main()
