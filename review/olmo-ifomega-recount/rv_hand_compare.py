"""Phase 2: the executor's hand-check table (olmo_ifomega/handcheck.csv) joined to my blinded items on (job, pid, chunk,
i). Reports coverage (items both read / only theirs / only mine), label agreement on shared items (my final label =
reader or my override; theirs = final_label), the disagreements with both evidences, and per-prompt good counts under
their labels vs mine. Output: out/hand_compare.txt, out/hand_compare.json"""
import csv
import glob
import json
import os
from collections import Counter, defaultdict

import rv_core as C

H = os.path.join(C.HERE, "hand")
GOOD = {"genuine", "sound"}


def main():
    key = {}
    for f in sorted(glob.glob(os.path.join(H, "key_r*.json"))):
        key.update(json.load(open(f)))
    lab = {}
    for f in sorted(glob.glob(os.path.join(H, "reader_labels", "*.json"))):
        for x in json.load(open(f)):
            lab[x["id"]] = x
    conf = json.load(open(os.path.join(H, "confirm.json")))
    mine = {}
    for i, k in key.items():
        if k["kind"] != "real" or i not in lab:
            continue
        L = conf[i]["label"] if i in conf else lab[i]["label"]
        mine[(k["job"], k["pid"], int(k["chunk"]), int(k["i"]))] = (i, L, lab[i].get("reason", ""), k)
    theirs = {}
    for r in csv.DictReader(open(os.path.join(C.HERE, "..", "..", "olmo_ifomega", "handcheck.csv"))):
        theirs[(r["job"], r["pid"], int(r["chunk"]), int(r["i"]))] = r
    both = set(mine) & set(theirs)
    txt = [f"my real items {len(mine)}, theirs {len(theirs)}, shared {len(both)}, only mine {len(set(mine) - set(theirs))},"
           f" only theirs {len(set(theirs) - set(mine))}"]
    agree = Counter()
    dis = []
    for k in sorted(both):
        a = mine[k][1]
        b = theirs[k]["final_label"]
        task = "omega" if k[1].startswith("omega") else "if"
        ga, gb = (a in GOOD), (b in GOOD)
        agree[(task, "exact" if a == b else ("good/notgood agree" if ga == gb else "DIFFER"))] += 1
        if ga != gb or (a != b and task == "omega"):
            dis.append({"key": k, "mine": a, "theirs": b, "my_item": mine[k][0], "their_item": theirs[k]["item"],
                        "my_reason": mine[k][2][:500], "their_evidence": theirs[k]["reader_evidence"][:500],
                        "their_note": theirs[k]["my_note"][:300], "role": theirs[k]["role"]})
    txt.append("agreement on shared items: " + json.dumps({f"{a}|{b}": v for (a, b), v in sorted(agree.items())}))
    for d in dis:
        txt.append(f"-- {d['key']} mine={d['mine']} theirs={d['theirs']} role={d['role']}")
        txt.append(f"   mine : {d['my_reason']}")
        txt.append(f"   their: {d['their_evidence']}")
        txt.append(f"   their note: {d['their_note']}")
    # per prompt good counts, theirs vs mine (over each side's own reads)
    per = defaultdict(lambda: {"mine": Counter(), "theirs": Counter()})
    for k, (i, L, _, kk) in mine.items():
        per[(k[1], kk["model"])]["mine"]["read"] += 1
        per[(k[1], kk["model"])]["mine"]["good"] += L in GOOD
    for k, r in theirs.items():
        per[(k[1], r["model"])]["theirs"]["read"] += 1
        per[(k[1], r["model"])]["theirs"]["good"] += r["final_label"] in GOOD
    json.dump({"agree": {f"{a}|{b}": v for (a, b), v in agree.items()}, "disagreements": dis,
               "per_prompt": {f"{p}|{m}": {"mine": dict(v["mine"]), "theirs": dict(v["theirs"])}
                              for (p, m), v in per.items()}},
              open(os.path.join(C.OUT, "hand_compare.json"), "w"), indent=1, default=str)
    open(os.path.join(C.OUT, "hand_compare.txt"), "w").write("\n".join(txt) + "\n")
    print("\n".join(txt[:2]))
    print(f"{len(dis)} disagreements (good vs not good, plus OMEGA label differences)")


if __name__ == "__main__":
    main()
