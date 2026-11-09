#!/usr/bin/env python3
"""Source choice for rung 4 (exemplars) and the LoRAs (training trajectories, held-out slice) of run olmo-ifladder, by
the pre-registered rules (preregistration/olmo-ifladder.md), iterating with the hand gate. VPS-side, standard library.

  python3 olmo_ifladder/sources.py needs <items.csv>   the stored strict successes whose label decides a choice and is not
                                                       known yet (prior gates or this run's source gate) -> items for
                                                       olmo_ifladder/handcheck.py prep
  python3 olmo_ifladder/sources.py choose [train|exemplars]   writes olmo_ifladder/exemplars.csv, problems_r4.jsonl
                                                       and / or train_manifest.csv / .jsonl, pids_lchk.txt, pids_leval.txt,
                                                       problems_plain.jsonl (fails if a needed label is unknown)

Labels: olmo_ifomega/handcheck.csv and olmo_transplant/handcheck_src.csv (earlier gates on the same stored samples),
then this run's source gate olmo_ifladder/handcheck_src.csv (final_label). Draw order: phase F -> E -> C, job, chunk, i.
Exemplars: for each target, sources in cand_exemplar.csv rank order; within a source its strict successes (finished)
in draw order; the first genuine is taken, a gamed one passes to the next success, then to the next source;
two sources per target. Training: ids in cand_train.csv order; within an id, candidate prompts in seeded order; the first
prompt (not used before) with a genuine s2300 and a genuine dpo trajectory (first genuine strict success of each,
prompt + response <= 16,384 tokens) fills the next slot; 16 slots. Held-out: for the first 8 ids (same order) with a
candidate left, that candidate; its first finished s2300 and dpo strict successes (no label needed: NLL diagnostic) and
its prompt for the LoRA check draws.
"""
import base64
import csv
import gzip
import hashlib
import json
import sys
from pathlib import Path

O = Path("olmo_ifladder")
OM = Path("artifacts/olmo_ifomega")
sys.path.insert(0, str(O))
from interventions import suffix  # noqa: E402

PROBS = {r["pid"]: r for r in map(json.loads, open("olmo_ifomega/problems.jsonl"))}
JOB_ORDER = ["F", "E1", "E2", "E3", "C1", "C2", "C3"]
N_SLOTS, N_HELDOUT, MAX_PER_SOURCE = 16, 8, 10**6  # no cap: the pre-registered rule walks every success of every ranked source
CAP = 16384
PROMPT_MARGIN = 700  # template + prompt tokens, upper bound used on the VPS (asserted exactly on the pod)


def ids_of(pid):
    x = PROBS[pid]["instruction_id_list"]
    return list(eval(x) if isinstance(x, str) else x)  # noqa: S307


def known_labels():
    lab = {}
    for r in csv.DictReader(open("olmo_ifomega/handcheck.csv")):
        if r["final_label"]:
            lab[(r["job"], r["pid"], str(r["chunk"]), str(r["i"]))] = (r["final_label"], "olmo_ifomega/handcheck.csv:" + r["item"])
    for r in csv.DictReader(open("olmo_transplant/handcheck_src.csv")):
        if r["final_label"]:
            j, p, c, i = r["key"].split("|")
            lab[(j, p, c, i)] = (r["final_label"], "olmo_transplant/handcheck_src.csv:" + r["item"])
    f = O / "handcheck_src.csv"
    if f.exists():
        for r in csv.DictReader(open(f)):
            if r["final_label"]:
                lab[(r["job"], r["pid"], str(r["chunk"]), str(r["i"]))] = (r["final_label"], "olmo_ifladder/handcheck_src.csv:" + r["item"])
    return lab


def strict_rows(model):
    out = {}
    for f in sorted(OM.glob("graded/*.jsonl")):
        if f.stem.split("_")[1:2] != [model]:
            continue
        for ln in open(f):
            r = json.loads(ln)
            if r.get("task") in ("ifbench", "ifeval") and r["strict"] and r["finish"] == "stop":
                out.setdefault(r["pid"], []).append(r)
    for v in out.values():
        v.sort(key=lambda r: (JOB_ORDER.index(r["job"].split("_")[0]) if r["job"].split("_")[0] in JOB_ORDER else 9,
                              r["job"], r["chunk"], r["i"]))
    return out


def key(r):
    return (r["job"], r["pid"], str(r["chunk"]), str(r["i"]))


class Need(Exception):
    pass


def walk(lab, s23, dpo, lookahead=False):
    """Apply the rules; returns (exemplars, train, heldout, needs). needs = rows whose label is required and unknown.
    lookahead: list the first undecided candidate of every id at once (reads in parallel; the choice stays sequential)."""
    needs = []
    ex = list(csv.DictReader(open(O / "cand_exemplar.csv")))
    exemplars = {}
    for t in dict.fromkeys(r["target"] for r in ex):
        srcs = list(dict.fromkeys(r["source"] for r in ex if r["target"] == t))
        got, blocked = [], False
        for s in srcs:
            if len(got) == 2:
                break
            for r in s23.get(s, [])[:MAX_PER_SOURCE]:
                l = lab.get(key(r))
                if l is None:  # an unread label blocks this target until it is read
                    needs.append(("exemplar", "s2300", r))
                    blocked = True
                    break
                if l[0] == "genuine":
                    got.append((s, r, l[1]))
                    break
            if blocked:
                break
        exemplars[t] = got

    tr = list(csv.DictReader(open(O / "cand_train.csv")))
    id_order = [i for _, i in sorted({(int(r["id_rank"]), r["id"]) for r in tr})]
    used, train, blocked = set(), [], False
    for iid in id_order:
        if len(train) == N_SLOTS or blocked:
            break
        cands = [c for _, c in sorted({(int(r["cand_rank"]), r["source"]) for r in tr if r["id"] == iid})]
        for c in cands:
            if c in used:
                continue
            pick = {}
            for who, pool in (("s2300", s23), ("dpo", dpo)):
                for r in pool.get(c, []):
                    if r["n_tok"] + PROMPT_MARGIN > CAP:
                        continue
                    l = lab.get(key(r))
                    if l is None:
                        needs.append(("train", who, r))
                        pick[who] = None
                        break
                    if l[0] == "genuine":
                        pick[who] = (r, l[1])
                        break
            if None in pick.values():
                if not lookahead:
                    blocked = True  # order matters: decide this candidate before any later one
                break
            if len(pick) == 2:
                train.append((iid, c, pick["s2300"], pick["dpo"]))
                used.add(c)
                break
    heldout = []
    if len(train) == N_SLOTS:
        for iid in id_order:
            if len(heldout) == N_HELDOUT:
                break
            cands = [c for _, c in sorted({(int(r["cand_rank"]), r["source"]) for r in tr if r["id"] == iid})]
            rest = [c for c in cands if c not in used]
            if not rest:
                continue
            c = rest[0]
            a = [r for r in s23.get(c, []) if r["n_tok"] + PROMPT_MARGIN <= CAP]
            d = [r for r in dpo.get(c, []) if r["n_tok"] + PROMPT_MARGIN <= CAP]
            if a and d:
                heldout.append((iid, c, a[0], d[0]))
                used.add(c)
    return exemplars, train, heldout, needs


def sample_path(job):
    return OM / "samples" / f"{job}.jsonl.gz"


def cmd_needs(out_csv):
    lab = known_labels()
    s23, dpo = strict_rows("s2300"), strict_rows("dpo")
    _, train, _, needs = walk(lab, s23, dpo, lookahead=True)
    seen, rows = set(), []
    for role, who, r in needs:
        k = key(r)
        if k in seen:
            continue
        seen.add(k)
        rows.append({"samples": str(sample_path(r["job"])), "graded": str(OM / "graded" / f"{r['job']}.jsonl"),
                     "problems": "olmo_ifomega/problems.jsonl", "job": r["job"], "pid": r["pid"], "chunk": r["chunk"],
                     "i": r["i"], "model": who, "role": f"source-{role}", "note": "0"})
    with open(out_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["samples", "graded", "problems", "job", "pid", "chunk", "i", "model", "role", "note"])
        w.writeheader()
        w.writerows(rows)
    missing = sorted({r["samples"] for r in rows if not Path(r["samples"]).exists()})
    print(f"needs: {len(rows)} items ({sum(r['role'] == 'source-exemplar' for r in rows)} exemplar, "
          f"{sum(r['role'] == 'source-train' for r in rows)} train); train slots so far {len(train)}; missing files {missing}")


def text_of(r):
    with gzip.open(sample_path(r["job"]), "rt") as f:
        for ln in f:
            x = json.loads(ln)
            if (x["pid"], x["chunk"], x["i"]) == (r["pid"], r["chunk"], r["i"]):
                return x
    raise KeyError(key(r))


def answer_of(text):
    return text.rsplit("</think>", 1)[1].strip() if "</think>" in text else None


def cmd_choose(part="all"):
    lab = known_labels()
    s23, dpo = strict_rows("s2300"), strict_rows("dpo")
    exemplars, train, heldout, needs = walk(lab, s23, dpo)
    if part in ("all", "train"):
        assert not [n for n in needs if n[0] == "train"], "training labels still needed (run `needs`)"
        assert len(train) == N_SLOTS and len(heldout) == N_HELDOUT, (len(train), len(heldout))
        write_train(train, heldout)
    if part in ("all", "exemplars"):
        assert not needs, f"{len(needs)} labels still needed (run `needs`)"
        assert all(len(v) == 2 for v in exemplars.values()), [t for t, v in exemplars.items() if len(v) != 2]
        write_exemplars(exemplars)


def write_exemplars(exemplars):
    exrows, r4 = [], []
    for t, got in exemplars.items():
        msgs = []
        for rank, (s, r, src) in enumerate(got, 1):
            x = text_of(r)
            ans = answer_of(x["text"])
            exrows.append({"target": t, "slot": rank, "source": s, "job": r["job"], "chunk": r["chunk"], "i": r["i"],
                           "label_src": src, "answer_words": len(ans.split()),
                           "answer_sha256": hashlib.sha256(ans.encode()).hexdigest()})
            msgs += [{"role": "user", "content": PROBS[s]["prompt"]}, {"role": "assistant", "content": ans}]
        p = PROBS[t]
        final = p["prompt"] + suffix(t, ids_of(t), 4)
        msgs.append({"role": "user", "content": final})
        rec = {k: p[k] for k in ("pid", "task", "key", "prompt", "instruction_id_list", "kwargs")}
        rec.update(prompt_sample=final, messages_sample=msgs, rung=4)
        r4.append(rec)
    with open(O / "exemplars.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(exrows[0]))
        w.writeheader()
        w.writerows(exrows)
    order = [json.loads(ln)["pid"] for ln in open(O / "problems_r3.jsonl")]
    r4.sort(key=lambda r: order.index(r["pid"]))
    with open(O / "problems_r4.jsonl", "w") as f:
        for r in r4:
            f.write(json.dumps(r) + "\n")
    print(f"exemplars: {len(exrows)} rows for {len(exemplars)} targets")


def write_train(train, heldout):
    man, mrows = [], []
    for slot, (iid, c, (ra, la), (rd, ld)) in enumerate(train):
        for who, r, src in (("s2300", ra, la), ("dpo", rd, ld)):
            x = text_of(r)
            sha = hashlib.sha256(x["text"].encode()).hexdigest()
            man.append({"role": "train", "writer": who, "slot": slot, "pid": c, "prompt": PROBS[c]["prompt"],
                        "ids": x["ids"], "key": "|".join(key(r)), "sha256": sha})
            mrows.append({"role": "train", "slot": slot, "id": iid, "pid": c, "ids": " ".join(ids_of(c)), "writer": who,
                          "job": r["job"], "chunk": r["chunk"], "i": r["i"], "n_tok": r["n_tok"],
                          "text_sha256": sha, "label_src": src})
    for k, (iid, c, ra, rd) in enumerate(heldout):
        for who, r in (("s2300", ra), ("dpo", rd)):
            x = text_of(r)
            sha = hashlib.sha256(x["text"].encode()).hexdigest()
            man.append({"role": "heldout", "writer": who, "slot": k, "pid": c, "prompt": PROBS[c]["prompt"],
                        "ids": x["ids"], "key": "|".join(key(r)), "sha256": sha})
            mrows.append({"role": "heldout", "slot": k, "id": iid, "pid": c, "ids": " ".join(ids_of(c)), "writer": who,
                          "job": r["job"], "chunk": r["chunk"], "i": r["i"], "n_tok": r["n_tok"],
                          "text_sha256": sha, "label_src": "strict only (NLL diagnostic)"})
    with open(O / "train_manifest.jsonl", "w") as f:
        for m in man:
            f.write(json.dumps(m) + "\n")
    with open(O / "train_manifest.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(mrows[0]))
        w.writeheader()
        w.writerows(mrows)
    # problems for the LoRA check (held-out + calibration) and evaluation (reach + calibration) jobs: plain prompts
    reach_cal = [r["pid"] for r in csv.DictReader(open(O / "prompts.csv"))]
    with open(O / "problems_plain.jsonl", "w") as f:
        for pid in reach_cal + [c for _, c, _, _ in heldout]:
            p = PROBS[pid]
            f.write(json.dumps({k: p[k] for k in ("pid", "task", "key", "prompt", "instruction_id_list", "kwargs")}) + "\n")
    # LoRA check (held-out + calibration, 16 each) and evaluation (reach 64 + calibration 48) pid lists, longest
    # expected first (dpo's stored unhinted mean tokens; the sampler runs them with --order given)
    mt = {r["pid"]: float(r["mean_tok"]) for r in csv.DictReader(open("olmo_ifomega/results.csv"))
          if r["model"] == "dpo" and r["mean_tok"]}
    pr = list(csv.DictReader(open(O / "prompts.csv")))
    cal = [r["pid"] for r in pr if r["set"] == "calib"]
    rch = [r["pid"] for r in pr if r["set"] == "reach"]
    ho = [c for _, c, _, _ in heldout]
    by = lambda xs: sorted(xs, key=lambda x: -mt.get(x, 0))  # noqa: E731
    (O / "pids_lchk.txt").write_text("\n".join(f"{x}:16" for x in by(ho + cal)) + "\n")
    (O / "pids_leval.txt").write_text("\n".join(f"{x}:{64 if x in rch else 48}" for x in by(rch + cal)) + "\n")
    print(f"train slots {len(train)}: {[c for _, c, _, _ in train]}; held-out {[c for _, c, _, _ in heldout]}")


if __name__ == "__main__":
    {"needs": lambda: cmd_needs(sys.argv[2]), "choose": lambda: cmd_choose(sys.argv[2] if len(sys.argv) > 2 else "all")}[sys.argv[1]]()
