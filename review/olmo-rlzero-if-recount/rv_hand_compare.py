"""Phase 2: the executor's handcheck.csv joined to my hand items on (job, pid, chunk, i) (real items only; my
base_btok rows carry job D_base_btok*). Coverage, agreement of final labels (mine after overrides vs the executor's
final_label), every disagreement with both evidences, and agreement on the first-read set.
Output: out/hand_compare.{txt,json}"""
import csv
import glob
import json
import os
from collections import Counter

import rv_core as C
from rv_hand import final_label

HAND = os.path.join(C.HERE, "hand")


def main():
    keys = {}
    for f in sorted(glob.glob(os.path.join(HAND, "key_r*.json"))):
        keys.update(json.load(open(f)))
    lab = {}
    for f in sorted(glob.glob(os.path.join(HAND, "reader_labels", "*.json"))):
        for x in json.load(open(f)):
            lab[x["item"]] = x
    conf = json.load(open(os.path.join(HAND, "confirm.json")))
    ex = {(r["job"], r["pid"], int(r["chunk"]), int(r["i"])): r
          for r in csv.DictReader(open(os.path.join(C.WS.replace("review/olmo-rlzero-if", "work/olmo-rlzero-if"),
                                                    "olmo_rlzero_if", "handcheck.csv")))}
    lines, out = [], {"pairs": []}
    c = Counter()
    for iid, k in sorted(keys.items()):
        if k["kind"] != "real":
            continue
        e = ex.get((k["job"], k["pid"], k["chunk"], k["i"]))
        mine = final_label(iid, lab, conf)
        c["mine"] += 1
        if e is None:
            c["not_read_by_executor"] += 1
            continue
        c["both"] += 1
        agree = mine == e["final_label"]
        c["agree"] += agree
        if k["model"] == "main" and k.get("read_rank", 9) <= 2 and k["side"] == "R_main":
            c["first_both"] += 1
            c["first_agree"] += agree
        if not agree:
            out["pairs"].append({"item": iid, "pid": k["pid"], "model": k["model"], "rank": k.get("read_rank"),
                                 "job": k["job"], "chunk": k["chunk"], "i": k["i"], "mine": mine,
                                 "mine_reader": lab.get(iid, {}).get("label"), "mine_note": conf.get(iid, {}).get("note"),
                                 "mine_evidence": lab.get(iid, {}).get("evidence"), "exec": e["final_label"],
                                 "exec_reader": e["reader_label"], "exec_overturned": e["overturned"],
                                 "exec_evidence": e["reader_evidence"], "exec_note": e["my_note"], "exec_item": e["item"]})
    c["exec_rows"] = len(ex)
    lines.append(" ".join(f"{a}={b}" for a, b in sorted(c.items())))
    lines.append(f"agreement on items both read: {c['agree']}/{c['both']}; first-read set: {c['first_agree']}/{c['first_both']}")
    for p in out["pairs"]:
        lines.append(f"- {p['item']} ({p['exec_item']}) {p['pid']} {p['model']} rank {p['rank']}: mine {p['mine']} "
                     f"(reader {p['mine_reader']}) vs executor {p['exec']} (reader {p['exec_reader']}, overturned "
                     f"{p['exec_overturned']})")
        lines.append(f"    mine: {p['mine_evidence']}")
        lines.append(f"    exec: {p['exec_evidence']} | note: {p['exec_note']}")
    out["counts"] = dict(c)
    json.dump(out, open(os.path.join(C.OUT, "hand_compare.json"), "w"), indent=1)
    open(os.path.join(C.OUT, "hand_compare.txt"), "w").write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
