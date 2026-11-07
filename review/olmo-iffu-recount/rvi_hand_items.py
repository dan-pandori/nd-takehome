"""Blinded hand-check items for the reviewer's hand gate of run olmo-iffu (built from the raw texts; no executor file).

Arms (draw order = (chunk, index) within the arm; T4 and its continuation T4b are one arm):
  T2_dpo, T2_s2300, T2c_dpo, T2c_s2300, T3_dpo, T4 (= T4_s0750 + T4b_s0750): IF strict successes (my re-grade);
  T1_dpo: every response credited under `omega` or `rl` (my re-grade).
T3_prior: olmo-ifomega's one dpo strict success on a test-3 prompt (ifbench_252; text fetched from the bucket into
  ~/review/oiffu_rv/prior_252.json), deciding for test 3's "0 genuine in 1,024".
Round 1: per (arm, prompt) the first 3 strict successes in draw order (all of T1's credited responses). Later rounds:
  `python3 rvi_hand_items.py <round>` takes hand/need_r<round>.json (written by rvi_hand.py: (arm, pid, ranks)).
Items get random ids (seeded per round), are shuffled across arms and models, and are written to
~/review/oiffu_rv/items_r<round>/ (not committed; regenerable); the key and batches go to hand/key_r<round>.json and
hand/batches_r<round>.json. Readers see the prompt as sampled, the constraints (the checker's own descriptions) and
the answer (IF), or the problem, the official answer and the full response (OMEGA); never the model, arm or rank.
"""
import collections
import gzip
import json
import random
import sys

import rvi_core as C

HINT_NOTE = ("Note: the last paragraph of this prompt (\"Answer in at most 60 words.\") is a length limit that the "
             "experimenter appended to the original request. Shortness that it asks for is not gutting the request, "
             "and the limit itself is not one of the checked constraints.")
IF_ARMS = {"T2_dpo": ["T2_dpo"], "T2_s2300": ["T2_s2300"], "T2c_dpo": ["T2c_dpo"], "T2c_s2300": ["T2c_s2300"],
           "T3_dpo": ["T3_dpo"], "T4": ["T4_s0750", "T4b_s0750"]}
PROB_FILE = {"T2_dpo": "olmo_iffu/problems_hint.jsonl", "T2_s2300": "olmo_iffu/problems_hint.jsonl",
             "T2c_dpo": "olmo_iffu/problems_hint2c.jsonl", "T2c_s2300": "olmo_iffu/problems_hint2c.jsonl",
             "T3_dpo": "olmo_ifomega/problems.jsonl", "T4": "olmo_ifomega/problems.jsonl",
             "T1_dpo": "olmo_iffu/problems_geo.jsonl", "T3_prior": "olmo_ifomega/problems.jsonl"}
ROUND1_K = 3
BATCH_IF = 22


def regrade(job):
    with gzip.open(C.OUT / "regrade" / f"{job}.jsonl.gz", "rt") as f:
        return [json.loads(ln) for ln in f]


def successes():
    """{(arm, pid): [regrade rows of strict successes in draw order]} and T1's credited rows."""
    out = {}
    for arm, jobs in IF_ARMS.items():
        by = collections.defaultdict(list)
        for job in jobs:
            for r in regrade(job):
                if r["strict"]:
                    by[r["pid"]].append(r)
        for pid, rs in by.items():
            out[(arm, pid)] = sorted(rs, key=lambda r: (r["chunk"], r["i"]))
    by = collections.defaultdict(list)
    for r in regrade("T1_dpo"):
        if r["omega"] or r["rl"]:
            by[r["pid"]].append(r)
    for pid, rs in by.items():
        out[("T1_dpo", pid)] = sorted(rs, key=lambda r: (r["chunk"], r["i"]))
    return out


def texts(wanted):
    """{(job, pid, chunk, i): text} for the wanted keys, streaming the sample files."""
    jobs = {k[0] for k in wanted}
    got = {}
    for job in jobs:
        for r in C.iter_rows(job, with_ids=False):
            k = (job, r["pid"], r["chunk"], r["i"])
            if k in wanted:
                got[k] = r["text"]
    return got


def constraint_lines(task, rec):
    import rvi_graders as G  # noqa: F401  (registers the upstream packages)
    reg = sys.modules["ifbench.instructions_registry" if task == "ifbench" else
                      "instruction_following_eval.instructions_registry"]
    lines = []
    for iid, kw in zip(rec["instruction_id_list"], rec["kwargs"]):
        kw = {a: b for a, b in kw.items() if b is not None}
        ins = reg.INSTRUCTION_DICT[iid](iid)
        desc = ins.build_description(**kw)
        args = ins.get_instruction_args()
        if args and "prompt" in args:
            desc = ins.build_description(prompt=rec["prompt"])
        lines.append(f"- `{iid}` {json.dumps(kw) if kw else ''}: {desc}")
    return lines


def if_item(iid, prob, rec, task, text):
    ans = C.answer_of(text)
    sent = prob.get("prompt_sample", prob["prompt"])
    parts = [f"# Item {iid}", "", "## Prompt (exactly as the model received it)", "", "```text", sent, "```", ""]
    if "prompt_sample" in prob:
        parts += [HINT_NOTE, ""]
    parts += ["## Verifiable constraints (the official automatic checker judged every one followed)", ""]
    parts += constraint_lines(task, rec)
    parts += ["", "## Answer (the text after the model's private reasoning, which is not shown)", "", "```text",
              ans, "```", ""]
    return "\n".join(parts)


def omega_item(iid, prob, text):
    parts = [f"# Item {iid}", "", "## Problem (as the model received it)", "", "```text", prob["prompt"], "```", "",
             f"## Official answer: {prob['answer']}", "",
             "## Full response (the opening <think> is part of the prompt, so the text starts mid-thought)", "",
             "```text", text, "```", ""]
    return "\n".join(parts)


def main():
    rnd = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    succ = successes()
    if rnd == 1:
        need = []
        for (arm, pid), rs in sorted(succ.items()):
            if arm == "T1_dpo":
                need += [(arm, pid, k) for k in range(len(rs))]
            else:
                need += [(arm, pid, k) for k in range(min(ROUND1_K, len(rs)))]
    else:
        need = [tuple(x) for x in json.load(open(C.KIT / "hand" / f"need_r{rnd}.json"))]
    probs = {arm: {r["pid"]: r for r in C.load_jsonl(C.RAW / fn)} for arm, fn in PROB_FILE.items()}
    ifb, ife = C.upstream_ifbench(), C.upstream_ifeval()
    keys, prior_txt = {}, {}
    for arm, pid, k in need:
        if arm == "T3_prior":  # olmo-ifomega's prior strict success on a test-3 prompt (rvi_before.py; fetched text)
            r = json.load(open(C.SCR / f"prior_{pid.split('_')[1]}.json"))
            keys[(arm, pid, k)] = (r["job"], pid, r["chunk"], r["i"])
            prior_txt[keys[(arm, pid, k)]] = r["text"]
            continue
        r = succ[(arm, pid)][k]
        keys[(arm, pid, k)] = (r["job"], pid, r["chunk"], r["i"])
    txt = texts({v for v in keys.values() if v not in prior_txt})
    txt.update(prior_txt)
    rng = random.Random(f"oiffu-review-r{rnd}")
    order = list(keys)
    rng.shuffle(order)
    used = set()
    d = C.SCR / f"items_r{rnd}"
    d.mkdir(exist_ok=True)
    key_out, if_ids, om_ids = {}, [], []
    for kk in order:
        while True:
            iid = "r%d%05x" % (rnd, rng.randrange(16 ** 5))
            if iid not in used:
                used.add(iid)
                break
        arm, pid, rank = kk
        job, _, chunk, i = keys[kk]
        prob = probs[arm][pid]
        if arm == "T1_dpo":
            body = omega_item(iid, prob, txt[keys[kk]])
            om_ids.append(iid)
        else:
            task, num = pid.split("_")
            rec = (ifb if task == "ifbench" else ife)[num]
            body = if_item(iid, prob, rec, task, txt[keys[kk]])
            if_ids.append(iid)
        (d / f"{iid}.md").write_text(body)
        key_out[iid] = {"arm": arm, "job": job, "pid": pid, "rank": rank, "chunk": chunk, "i": i}
    batches = {f"r{rnd}_if_{b:02d}": if_ids[b * BATCH_IF:(b + 1) * BATCH_IF]
               for b in range((len(if_ids) + BATCH_IF - 1) // BATCH_IF)}
    for j, iid in enumerate(om_ids):
        batches[f"r{rnd}_om_{j:02d}"] = [iid]
    (C.KIT / "hand").mkdir(exist_ok=True)
    json.dump(key_out, open(C.KIT / "hand" / f"key_r{rnd}.json", "w"), indent=1, sort_keys=True)
    json.dump(batches, open(C.KIT / "hand" / f"batches_r{rnd}.json", "w"), indent=1, sort_keys=True)
    sizes = {b: sum((d / f"{x}.md").stat().st_size for x in ids) for b, ids in batches.items()}
    print(f"round {rnd}: {len(if_ids)} IF items, {len(om_ids)} OMEGA items, {len(batches)} batches; bytes {sizes}")


if __name__ == "__main__":
    main()
