"""Reader sensitivity of my hand gate: every (arm, prompt) outcome recomputed under three label sources.
  A      first readers only (rounds r1-r3);
  B      second readers where they read the item, else A;
  final  agreement of A and B, else my adjudication (hand/confirm.json) - the labels the outcomes use.
The walk is the gate's: strict successes in draw order until 2 genuine (none left -> the count so far); an
unread item that the walk reaches makes the outcome "open" (more reads needed). Rule 6 strict reading as in rvi_hand.
Also lists every A/B disagreement with my adjudication.  -> out/sensitivity.txt, out/sensitivity.json
"""
import glob
import json
import os

import rvi_core as C
from rvi_hand_items import successes

H = C.KIT / "hand"


def main():
    keys = {}
    for f in glob.glob(str(H / "key_r*.json")):
        keys.update(json.load(open(f)))
    # first and second reader of each item, in read order: rounds r1..r6 (a round's `_b` file after its first
    # reader), then the B pass (b_*), then the third readers (c_*)
    def order(n):
        kind = 2 if n.startswith("c_") else (1 if n.startswith("b_") else 0)
        return (kind, n.replace("_b.json", "~.json"))
    reads = {}
    for f in sorted(glob.glob(str(H / "reader_labels" / "*.json")), key=lambda f: order(os.path.basename(f))):
        for x in json.load(open(f)):
            reads.setdefault(x["item"], []).append(x)
    A = {i: r[0] for i, r in reads.items()}
    B = {i: r[1] for i, r in reads.items() if len(r) > 1}
    conf = {k: v for k, v in json.load(open(H / "confirm.json")).items() if not k.startswith("_")} if (H / "confirm.json").exists() else {}
    by_rank = {(k["arm"], k["pid"], k["rank"]): i for i, k in keys.items()}

    def lab(src, iid):
        if iid is None:
            return None, False
        a, b = A.get(iid), B.get(iid)
        caps = any(x and x.get("all_caps_title_case") for x in (a, b))
        if src == "A":
            return (a["label"] if a else None), caps
        if src == "B":
            return ((b or a)["label"] if (b or a) else None), caps
        if iid in conf:
            return conf[iid]["label"], conf[iid].get("all_caps_title_case", caps)
        if a and b and a["label"] != b["label"]:
            return "unsure", caps
        return ((b or a)["label"] if (b or a) else None), caps

    succ = successes()
    out, lines = {}, []
    for (arm, pid), rs in sorted(succ.items()):
        if arm == "T1_dpo":
            continue
        row = {}
        for src in ("A", "B", "final"):
            g = gs = 0
            state = "done"
            for rank in range(len(rs)):
                if g >= 2 and gs >= 2:
                    break
                l, caps = lab(src, by_rank.get((arm, pid, rank)))
                if l in (None, "unsure"):
                    state = "open" if l is None else "unsure"
                    break
                if l == "genuine":
                    if g < 2:
                        g += 1
                    gs += not caps
            row[src] = {"genuine": g, "genuine_strict": min(gs, 2), "state": state}
        out[f"{arm}|{pid}"] = row
        vals = {s: (min(v["genuine"], 2), v["state"]) for s, v in row.items()}
        if len(set(vals.values())) > 1:
            lines.append(f"{arm}|{pid}: A {row['A']}, B {row['B']}, final {row['final']}")
    dis = []
    for iid in sorted(set(A) & set(B)):
        if A[iid]["label"] != B[iid]["label"]:
            k = keys[iid]
            dis.append({"item": iid, "arm": k["arm"], "pid": k["pid"], "rank": k["rank"], "A": A[iid]["label"],
                        "B": B[iid]["label"], "final": conf.get(iid, {}).get("label"), "note": conf.get(iid, {}).get("note")})
    agree = sum(1 for i in set(A) & set(B) if A[i]["label"] == B[i]["label"])
    n3 = sum(len(r) >= 3 for r in reads.values())
    head = [f"items read once or more: {len(A)}; twice or more: {len(B)}; three times: {n3}; first/second agree {agree}; "
            f"disagree {len(dis)} (adjudicated {sum(d['final'] is not None for d in dis)})",
            "(arm, prompt) whose outcome (genuine count capped at 2, state) differs between label sources:"]
    C.dump({"outcomes": out, "disagreements": dis}, "sensitivity.json")
    txt = head + lines + ["", "disagreements:"] + [
        f"  {d['item']} {d['arm']} {d['pid']} rank {d['rank']}: A {d['A']}, B {d['B']} -> {d['final']}  {d['note'] or ''}"
        for d in dis]
    (C.OUT / "sensitivity.txt").write_text("\n".join(txt) + "\n")
    print("\n".join(txt))


if __name__ == "__main__":
    main()
