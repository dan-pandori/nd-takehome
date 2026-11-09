"""Blinded hand-check items for my repeat of run olmo-ifladder's hand gate.

usage: rvl_hand_items.py ROUND            (ROUND = A1, A2, ... first reads; B1.. second reads; C1.. third reads)

Selection (my own walk, rvl_hand.py `walk`): for every reach (prompt, cell) in R2 R3 R4 LM LC S2 S3 S4, the strict
successes (my re-grade) in draw order (chunk, index); a draw is read unless an identical whitespace-collapsed answer to
the same prompt text (cell groups {R2,S2} {R3,S3} {R4,S4} {LM,LC}) already has a label, or my mechanical rule-1 screen
labels it gamed (pre-registered list: one-sentence answers for sentence:increment / alliteration_increment /
words:last_first / format:emoji; one non-empty line for format:line_indent; no line starting with '*' for
format:sub-bullets). The walk reads until 2 genuine and at least the first min(n, 4) draws, or none left.
Source items (round A1 only): the 32 training trajectories' answers (16 s2300, 16 dpo; train_manifest.csv).
Second / third reads are listed by rvl_hand.py (hand/need_<ROUND>.json).

Item text: the final user turn exactly as the model received it (ladder rungs: the original prompt + the appended
text; LoRA / source items: the original prompt), the constraints with the checker's verdict, the answer (text after
the last '</think>'). Item ids are random (seeded by the round name); items are shuffled across cells and models.
Writes ~/review/oifl_rv/items/<id>.md, hand/key_<ROUND>.json (id -> sample key), hand/batches_<ROUND>.json.
"""
import gzip
import hashlib
import json
import random
import sys

from rvl_core import ART, CODE, KIT, SCR, answer_of, iter_gz, iter_job, load_csv, upstream_record, wsnorm

HAND = KIT / "hand"
HAND.mkdir(exist_ok=True)
ITEMS = SCR / "items"
ITEMS.mkdir(exist_ok=True)
JOB_OF = {"R2": "R2_dpo", "R3": "R3_dpo", "R4": "R4_dpo", "S2": "R2_s2300", "S3": "R3_s2300", "S4": "R4_s2300",
          "LM": "Leval_main", "LC": "Leval_ctrl"}
PROB_OF = {"R2": "problems_r2.jsonl", "R3": "problems_r3.jsonl", "R4": "problems_r4.jsonl", "S2": "problems_r2.jsonl",
           "S3": "problems_r3.jsonl", "S4": "problems_r4.jsonl", "LM": "problems_plain.jsonl",
           "LC": "problems_plain.jsonl"}


def user_turn(cell, pid, _c={}):
    f = PROB_OF[cell]
    if f not in _c:
        _c[f] = {json.loads(l)["pid"]: json.loads(l) for l in open(CODE / f)}
    r = _c[f][pid]
    return r.get("prompt_sample") or upstream_record(pid)[1]["prompt"]


def texts_for(keys):
    """keys: list of (cell, pid, chunk, i) -> {key: answer} streamed from the sample files."""
    out = {}
    by_job = {}
    for k in keys:
        by_job.setdefault(JOB_OF[k[0]], set()).add(k)
    for job, ks in by_job.items():
        cell = [c for c, j in JOB_OF.items() if j == job][0]
        for r in iter_job(job):
            k = (cell, r["pid"], int(r["chunk"]), int(r["i"]))
            if k in ks:
                out[k] = answer_of(r["text"])
    return out


def src_texts():
    """The 32 training trajectories' answers: {('SRC', pid, writer): (prompt, answer)}."""
    man = [r for r in load_csv(CODE / "train_manifest.csv") if r["role"] == "train"]
    out = {}
    need = {}
    for r in man:
        need.setdefault(r["job"], set()).add((r["pid"], int(r["chunk"]), int(r["i"]), r["writer"]))
    for job, ks in need.items():
        want = {(a, b, c): w for a, b, c, w in ks}
        for x in iter_gz(SCR / "src" / f"{job}.jsonl.gz"):
            k = (x["pid"], int(x["chunk"]), int(x["i"]))
            if k in want:
                out[("SRC", x["pid"], want[k], job, k[1], k[2])] = (upstream_record(x["pid"])[1]["prompt"],
                                                                     answer_of(x["text"]))
    return out


def item_md(iid, prompt, task, rec, answer, per):
    lines = [f"# Item {iid}", "", "## Prompt (sent to the model verbatim)", "", prompt, "",
             "## Constraints checked (official checker)", ""]
    for j, (cid, kw) in enumerate(zip(rec["instruction_id_list"], rec["kwargs"])):
        kw = {a: b for a, b in dict(kw).items() if b is not None}
        ok = per[j] if per is not None else True
        lines.append(f"- `{cid}` {json.dumps(kw, ensure_ascii=False)}: checker says {'followed' if ok else 'NOT followed'}")
    lines += ["", f"## Answer (the text after the model's private reasoning, which is not shown; "
                  f"{len(answer.split())} words)", "", answer, ""]
    return "\n".join(lines)


def write_round(rnd, keys, with_src=False, batch=22, src_keys=None):
    """keys: list of (cell, pid, chunk, i) to read in this round."""
    rng = random.Random(f"oifl-{rnd}")
    texts = texts_for(keys)
    regr = {}
    for k in keys:
        job = JOB_OF[k[0]]
        if job not in regr:
            regr[job] = {(r["pid"], r["chunk"], r["i"]): r for r in
                         (json.loads(l) for l in gzip.open(KIT / "out" / "regrade" / f"{job}.jsonl.gz", "rt"))}
    entries = []
    for k in keys:
        cell, pid, ch, i = k
        task, rec = upstream_record(pid)
        g = regr[JOB_OF[cell]][(pid, ch, i)]
        assert g["strict"], k
        entries.append((list(k), user_turn(cell, pid), task, rec, texts[k], g["per"]))
    if with_src or src_keys:
        want = None if with_src else {tuple(x) for x in src_keys}
        for k, (prompt, ans) in src_texts().items():
            if want is not None and tuple(k) not in want:
                continue
            task, rec = upstream_record(k[1])
            entries.append((list(k), prompt, task, rec, ans, None))
    key = {}
    used = set()
    for e in entries:
        while True:
            iid = "y" + hashlib.sha256(f"{rnd}|{rng.random()}".encode()).hexdigest()[:6]
            if iid not in used and not (ITEMS / f"{iid}.md").exists():
                break
        used.add(iid)
        key[iid] = e[0]
        (ITEMS / f"{iid}.md").write_text(item_md(iid, e[1], e[2], e[3], e[4], e[5]))
    ids = list(key)
    rng.shuffle(ids)
    batches = [ids[j:j + batch] for j in range(0, len(ids), batch)]
    json.dump(key, open(HAND / f"key_{rnd}.json", "w"), indent=0)
    json.dump(batches, open(HAND / f"batches_{rnd}.json", "w"), indent=0)
    print(f"round {rnd}: {len(ids)} items in {len(batches)} batches")
    return key, batches


if __name__ == "__main__":
    rnd = sys.argv[1]
    need = json.load(open(HAND / f"need_{rnd}.json"))
    write_round(rnd, [tuple(k) for k in need["keys"]], with_src=need.get("with_src", False),
                batch=need.get("batch", 22), src_keys=need.get("src_keys"))
