"""Second, independent blinded reader (B) on every deciding IF item of my hand gate (after all A rounds).

Deciding items, per (arm, prompt) in draw order:
  - outcome >= 2 genuine (primary reading): every item read up to and including the 2nd genuine (the counted
    genuine items, and the gamed ones before them); under the strict reading (rule 6) the same up to its 2nd genuine;
  - outcome < 2 genuine: every strict success (all were read).
  - T3_prior: olmo-ifomega's strict success on a test-3 prompt.
Items reuse the A round's item files (same text, same blinding); the B batches are shuffled with a new seed and
written to ~/review/oiffu_rv/batches/b_if_<nn>.txt; the list goes to hand/batches_b.json.
"""
import glob
import json
import os
import random

import rvi_core as C

H = C.KIT / "hand"


def main():
    hand = json.load(open(C.OUT / "hand.json"))["if"]
    keys = {}
    for f in sorted(glob.glob(str(H / "key_r*.json"))):
        r = os.path.basename(f)[5:-5]
        for iid, k in json.load(open(f)).items():
            keys[iid] = dict(k, round=int(r))
    want = []
    for k, v in hand.items():
        assert not v["pending"], k
        items = v["items"]
        if v["genuine"] >= 2:
            g = gs = 0
            for x in items:
                if x["label"] is None:
                    break
                want.append(x["item"])
                if x["label"] == "genuine":
                    g += 1
                    gs += not x["caps"]
                if g >= 2 and (gs >= 2 or not any(y["caps"] for y in items)):
                    break
        else:
            want += [x["item"] for x in items if x["label"] is not None]
    want += [iid for iid, k in keys.items() if k["arm"] == "T3_prior"]
    want = sorted(set(want))
    rng = random.Random("oiffu-review-B")
    rng.shuffle(want)
    per = 22
    batches = {f"b_if_{i:02d}": want[i * per:(i + 1) * per] for i in range((len(want) + per - 1) // per)}
    for name, ids in batches.items():
        with open(C.SCR / "batches" / f"{name}.txt", "w") as f:
            for iid in ids:
                f.write(str(C.SCR / f"items_r{keys[iid]['round']}" / f"{iid}.md") + "\n")
    json.dump(batches, open(H / "batches_b.json", "w"), indent=1, sort_keys=True)
    print(f"{len(want)} deciding items in {len(batches)} B batches")


if __name__ == "__main__":
    main()
