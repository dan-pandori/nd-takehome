"""Hand-gate statistics for my repeat: reads by round type, label sources, reader agreement, confirmations, screen and
identity-inheritance counts, rule-6 flags. Writes out/hand_report.txt / .json."""
import collections
import json

import rvc_hand as H
from rvc_core import Tee, dump


def main():
    T = Tee("hand_report.txt")
    rd = H.reads()
    L = H.labels()
    lab = H.lab_fn(L)
    kind = lambda r: {"A": "first (walk / arm C / s2300 rule f)", "D": "first (rule d, first four)", "B": "second",
                      "C": "third"}[r[0][0]]
    reads = collections.Counter()
    for g, rs in rd.items():
        for r in rs:
            reads[kind(r)] += 1
    T("reads by type:", dict(reads), "total", sum(reads.values()))
    T("label groups read:", len(rd), "| by number of reads:", dict(collections.Counter(len(v) for v in rd.values())))
    two = [(rs[0][1], rs[1][1]) for rs in rd.values() if len(rs) >= 2]
    agree = sum(a == b for a, b in two)
    T(f"first vs second read agreement: {agree}/{len(two)} = {agree / max(1, len(two)):.3f}; "
      f"table {dict(collections.Counter(two))}")
    conf = json.load(open(H.HAND / "confirm.json"))
    changed = sum(1 for g, c in conf.items() if c["reads"] and c["label"] != collections.Counter(c["reads"][:3]).most_common(1)[0][0]
                  and not (len(c["reads"]) == 2 and c["reads"][0] != c["reads"][1]))
    T(f"confirmations: {len(conf)} (labels {dict(collections.Counter(c['label'] for c in conf.values()))}); "
      f"changing the reader majority / single read: {changed}")
    for g, c in conf.items():
        if c["reads"] and c["label"] != collections.Counter(c["reads"][:3]).most_common(1)[0][0] and not (
                len(c["reads"]) == 2 and c["reads"][0] != c["reads"][1]):
            T(f"   {json.loads(g)[0]} reads {c['reads']} -> {c['label']}: {c['reason'][:150]}")
    rej = json.load(open(H.HAND / "adj_rejected.json"))
    lists = {k: v for k, v in rej.items() if isinstance(v, list)}
    items = [i for k, v in lists.items() if k.startswith("ADJ") for i in v]
    T(f"low-confidence adjudicator proposals not accepted (against two agreeing reads or a 2-1 majority): "
      f"{sum(len(v) for k, v in lists.items() if k.startswith('ADJ'))} proposals "
      f"({ {k: len(v) for k, v in lists.items()} }); distinct items {len(set(items))}")
    r6 = [g for g, c in conf.items() if c["label"] == "genuine" and "6" in c["reason"].split(" (", 1)[0].replace("rule ", "").split(";")]
    T(f"rule-6 (ALL-CAPS title case, genuine on the primary reading) groups: {len(r6)} {[json.loads(g)[0] for g in r6]}")
    cfa = collections.Counter((r[1], r[2]) for rs in rd.values() for r in rs)
    T("reads by (label, checker_agrees):", dict(cfa))
    # every draw my kit can label: source of its label
    allk = set()
    for c in H.CK:
        for p in H.REACH:
            allk |= set(H.B[c][p])
    for p, d in H.X.items():
        for c, ks in d.items():
            allk |= set(ks)
    for c in H.CKA:
        allk |= set(H.ARMC[c])
    readkeys = {r[5] for rs in rd.values() for r in rs}
    src = collections.Counter()
    for k in allk:
        v = lab(k)
        if v is None:
            src["unlabelled"] += 1
        elif k in readkeys:
            src["read"] += 1
        elif H.gkey(k) in L:
            src["inherited (identical answer read)"] += 1
        else:
            src["screen"] += 1
    T("labelled draws by source (arm-B base / extension / my arm-C sample):", dict(src))
    dump({"reads": dict(reads), "agree": [agree, len(two)], "confirm": len(conf), "rule6": len(r6), "src": dict(src)},
         "hand_report.json")


if __name__ == "__main__":
    main()
