"""Provenance checks for run olmo-iffu (brief, "For the reviewer": subsets vs seeds, hint wording, token budget).

1. The 43 IFBench hand-reach prompts parsed from review_olmo-ifomega.md (the list the brief names); test 2's and test
   3's subsets re-drawn with random.Random(seed).sample under both list orders (numeric IFBench index, the review's
   own order); test 2c's 32 = the 43 minus test 2's 10 minus ifbench_281; test 4's 43.
2. Problems files vs my upstream fetches: prompt, instruction ids, kwargs (None-valued keys dropped); hint rows:
   prompt_sample == prompt + "\n\n" + "Answer in at most 60 words."
3. Prompt tokens: the olmo_thinker template (my fetch of open-instruct @ 7e780f2fea; its sha256 vs the metas'),
   rendered for one user turn and tokenised with each model's tokenizer.json, vs every row's prompt_tokens.
4. Budgets: config max_position_embeddings (my download of each config.json) and rows' max_tokens; T1 must have
   max_tokens == 65,536 - prompt tokens; everything else 32,768. Finish 'length' iff n_tok == max_tokens.
5. Engine seeds, TP, GPUs, revisions per job (metas + rows) vs the pre-registration.
-> out/provenance.txt, out/provenance.json
"""
import ast
import collections
import gzip
import hashlib
import json
import random
import re

from tokenizers import Tokenizer

import rvi_core as C

LINES, RES = [], {}


def say(s=""):
    LINES.append(s)
    print(s)


def reach43():
    txt = (C.KIT.parent.parent / "review_olmo-ifomega.md").read_text()
    m = re.search(r"IFBench hand-reach prompts \(strict mapping, 43\): (.*)", txt)
    ids = re.findall(r"`(ifbench_\d+)`", m.group(1))
    assert len(ids) == 43 == len(set(ids))
    return ids


def template():
    src = (C.SCR / "upstream" / "oi" / "dataset_transformation.py").read_text()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and any(getattr(t, "id", None) == "CHAT_TEMPLATES" for t in node.targets):
            d = node.value
            for k, v in zip(d.keys, d.values):
                if isinstance(k, ast.Constant) and k.value == "olmo_thinker":
                    return ast.literal_eval(v)
    raise RuntimeError("olmo_thinker not found")


def render_one_user(content):
    # olmo_thinker for [{"role": "user", "content": c}], add_generation_prompt=True (no system message given)
    return ("<|im_start|>system\nYou are a helpful AI assistant.<|im_end|>\n"
            "<|im_start|>user\n" + content + "<|im_end|>\n" + "<|im_start|>assistant\n<think>")


def main():
    # ---- 1. subsets
    r43 = reach43()
    num = sorted(r43, key=lambda s: int(s.split("_")[1]))
    exp2 = "ifbench_290 ifbench_4 ifbench_64 ifbench_79 ifbench_170 ifbench_0 ifbench_188 ifbench_207 ifbench_179 ifbench_268".split()
    exp3 = "ifbench_252 ifbench_269 ifbench_253 ifbench_3 ifbench_78 ifbench_248 ifbench_211 ifbench_166 ifbench_136 ifbench_133".split()
    say("1. Subsets (the 43 parsed from review_olmo-ifomega.md)")
    for name, order in (("numeric IFBench index", num), ("the review's listed order", r43)):
        elig = [p for p in order if p != "ifbench_281"]
        t2 = random.Random(20261106).sample(elig, 10)
        rest = [p for p in order if p not in t2]
        t3 = random.Random(20261107).sample(rest, 10)
        say(f"   order = {name}: test 2 = {' '.join(t2)}  (pre-registered list {'MATCHES' if t2 == exp2 else 'differs'})")
        say(f"   {'':>{len('order = ' + name)}}  test 3 = {' '.join(t3)}  ({'MATCHES' if t3 == exp3 else 'differs'})")
    t2c = [p for p in num if p not in exp2 and p != "ifbench_281"]
    say(f"   test 2 / test 3 disjoint: {not set(exp2) & set(exp3)}; test 3 subset of the 33 rest: "
        f"{set(exp3) <= set(r43) - set(exp2)}; test 2c = 43 - test 2 - 281: {len(t2c)} prompts; "
        f"contains all of test 3: {set(exp3) <= set(t2c)}")
    RES["t2"], RES["t3"], RES["t2c"], RES["r43"] = exp2, exp3, t2c, num
    # sets actually sampled, from the sample files
    sampled = collections.defaultdict(set)
    for job in C.JOBS:
        for r in C.iter_rows(job, with_ids=False):
            sampled[job].add(r["pid"])
    ife3, caps3 = ["ifeval_2350", "ifeval_2447", "ifeval_3478"], ["ifeval_1314", "ifeval_2247", "ifeval_2563"]
    geo3 = sorted(p for p in sampled["T1_dpo"])
    checks = {"T1_dpo": set(geo3) if len(geo3) == 3 else None,
              "T2_dpo": set(exp2 + ife3 + caps3), "T2_s2300": set(exp2 + ife3 + caps3),
              "T2c_dpo": set(t2c), "T2c_s2300": set(t2c), "T3_dpo": set(exp3), "T4_s0750": set(num)}
    for job, want in checks.items():
        say(f"   {job}: sampled {len(sampled[job])} prompts; equals the design set: {sampled[job] == want}")
    say(f"   T4b_s0750: {sorted(sampled['T4b_s0750'])}")
    say(f"   T1 prompts: {[p[-3:] for p in geo3]}")

    # ---- 2. problems files vs upstream
    ifb, ife = C.upstream_ifbench(), C.upstream_ifeval()
    say("\n2. Problems files vs upstream datasets (prompt, instruction ids, kwargs without None values)")
    hint = "Answer in at most 60 words."
    for fn in ("olmo_iffu/problems_hint.jsonl", "olmo_iffu/problems_hint2c.jsonl", "olmo_ifomega/problems.jsonl"):
        rows = C.load_jsonl(C.RAW / fn)
        bad, n, nh, badh = [], 0, 0, []
        for r in rows:
            if r["task"] not in ("ifbench", "ifeval"):
                continue
            up = (ifb if r["task"] == "ifbench" else ife)[r["pid"].split("_")[1]]
            kw_r = [{a: b for a, b in k.items() if b is not None} for k in r["kwargs"]]
            kw_u = [{a: b for a, b in k.items() if b is not None} for k in up["kwargs"]]
            n += 1
            if (r["prompt"], list(r["instruction_id_list"]), kw_r) != (up["prompt"], list(up["instruction_id_list"]), kw_u):
                bad.append(r["pid"])
            if "prompt_sample" in r:
                nh += 1
                if r["prompt_sample"] != r["prompt"] + "\n\n" + hint or r.get("hint") != hint:
                    badh.append(r["pid"])
        say(f"   {fn}: {n} IF rows, {len(bad)} differ from upstream {bad[:5]}; hinted rows {nh}, "
            f"wrong hint {badh}")
    geo = C.load_jsonl(C.RAW / "olmo_iffu" / "problems_geo.jsonl")
    og = {r["pid"]: r for r in C.load_jsonl(C.RAW / "olmo_ifomega" / "problems.jsonl") if r["pid"] in [g["pid"] for g in geo]}
    for g in geo:
        o = og[g["pid"]]
        same = all(g[k] == o[k] for k in o if k != "answer")
        say(f"   problems_geo {g['pid'][-3:]}: equals olmo_ifomega's row except the answer: {same}; "
            f"answer {o['answer']} -> {g['answer']}; prompt = prompt_original minus the boxed instruction: "
            f"{g['prompt'] + chr(10) * 2 + 'Present the answer in LaTex format: ' + chr(92) + 'boxed{Your answer}' == g['prompt_original']}")

    # ---- 3. template and prompt tokens
    T = template()
    tsha = hashlib.sha256(T.encode()).hexdigest()
    metas = {}
    for job in C.JOBS:
        metas[job] = [json.loads(ln) for ln in open(C.ART / "meta" / f"{job}.json")]
    msha = {m["template_sha256"] for ms in metas.values() for m in ms}
    say(f"\n3. olmo_thinker sha256 (my fetch) {tsha[:16]}; metas {sorted(x[:16] for x in msha)}; equal: {msha == {tsha}}")
    toks = {"dpo": Tokenizer.from_file(str(C.SCR / "tok" / "allenai_Olmo-3-32B-Think-DPO" / "tokenizer.json")),
            "s": Tokenizer.from_file(str(C.SCR / "tok" / "allenai_Olmo-3.1-32B-Think" / "tokenizer.json"))}
    src = {}
    for fn in ("olmo_iffu/problems_hint.jsonl", "olmo_iffu/problems_hint2c.jsonl", "olmo_ifomega/problems.jsonl",
               "olmo_iffu/problems_geo.jsonl"):
        src[fn] = {r["pid"]: r for r in C.load_jsonl(C.RAW / fn)}
    job_file = {"T1_dpo": "olmo_iffu/problems_geo.jsonl", "T2_dpo": "olmo_iffu/problems_hint.jsonl",
                "T2_s2300": "olmo_iffu/problems_hint.jsonl", "T2c_dpo": "olmo_iffu/problems_hint2c.jsonl",
                "T2c_s2300": "olmo_iffu/problems_hint2c.jsonl", "T3_dpo": "olmo_ifomega/problems.jsonl",
                "T4_s0750": "olmo_ifomega/problems.jsonl", "T4b_s0750": "olmo_ifomega/problems.jsonl"}
    for job, fn in job_file.items():
        say(f"   {job}: meta problems file {metas[job][-1]['problems']} (expected {fn})")
    ptok_ok, ptok_bad, nohint_tokens = 0, [], {}
    seen = set()
    for job in C.JOBS:
        for r in C.iter_rows(job, with_ids=False):
            key = (job, r["pid"])
            if key in seen:
                continue
            seen.add(key)
            p = src[job_file[job]][r["pid"]]
            content = p.get("prompt_sample", p["prompt"])
            tk = toks["dpo" if r["model"] == "dpo" else "s"]
            enc = tk.encode(render_one_user(content), add_special_tokens=False)
            n = len(enc.ids)
            if n == r["prompt_tokens"]:
                ptok_ok += 1
            else:
                ptok_bad.append((job, r["pid"], n, r["prompt_tokens"]))
            if "prompt_sample" in p:
                nohint_tokens[key] = (n, len(tk.encode(render_one_user(p["prompt"]), add_special_tokens=False).ids))
    say(f"   prompt_tokens == my count of the templated user turn sent: {ptok_ok} (job, prompt) pairs; "
        f"differ: {ptok_bad[:6]}")
    dif = collections.Counter(a - b for a, b in nohint_tokens.values())
    say(f"   hinted pairs: token difference (with hint - without) {dict(dif)} -> the rows' prompt_tokens "
        f"include the hint")
    special = [t for t in ("<|im_start|>", "<|im_end|>", "<think>", "</think>", "<|endoftext|>")]
    say("   special tokens (dpo tokenizer): " + ", ".join(f"{t}={toks['dpo'].token_to_id(t)}" for t in special))

    # ---- 4. budgets
    say("\n4. Budgets")
    for name in ("allenai_Olmo-3-32B-Think-DPO", "allenai_Olmo-3.1-32B-Think"):
        cfg = json.load(open(C.SCR / "tok" / name / "config.json"))
        lt = cfg.get("layer_types") or []
        say(f"   {name}: max_position_embeddings {cfg.get('max_position_embeddings')}, rope_scaling "
            f"{cfg.get('rope_scaling')}, layers {cfg.get('num_hidden_layers')}, kv heads {cfg.get('num_key_value_heads')}, "
            f"sliding_window {cfg.get('sliding_window')}, layer types {dict(collections.Counter(lt))}")
    for job in C.JOBS:
        mt, fin, viol, n = collections.Counter(), collections.Counter(), [], 0
        maxn = 0
        for r in C.iter_rows(job, with_ids=False):
            n += 1
            mt[r["max_tokens"]] += 1
            fin[r["finish"]] += 1
            maxn = max(maxn, r["n_tok"])
            want = 65536 - r["prompt_tokens"] if job == "T1_dpo" else 32768
            if r["max_tokens"] != want:
                viol.append(("max_tokens", r["pid"], r["max_tokens"], want))
            if (r["finish"] == "length") != (r["n_tok"] == r["max_tokens"]):
                viol.append(("finish", r["pid"], r["finish"], r["n_tok"], r["max_tokens"]))
            if r["n_tok"] > r["max_tokens"]:
                viol.append(("over", r["pid"], r["n_tok"]))
        meta = metas[job][-1]
        say(f"   {job}: {n} rows; max_tokens {dict(mt)}; finish {dict(fin)}; longest {maxn}; violations {viol[:4]}; "
            f"meta fill_context {meta['fill_context']}, max_tokens_by_pid {sorted(set(meta['max_tokens_by_pid'].values()))}")

    # ---- 5. seeds, TP, GPUs, revisions
    say("\n5. Jobs (meta, last line) and rows")
    want_seed = {"T1_dpo": 7001, "T2_dpo": 7101, "T2_s2300": 7102, "T3_dpo": 7201, "T4_s0750": 7301,
                 "T4b_s0750": 7302, "T2c_dpo": 7103, "T2c_s2300": 7104}
    for job in C.JOBS:
        ms = metas[job]
        revs = collections.Counter((r["model"], r["rev"]) for r in C.iter_rows(job, with_ids=False))
        say(f"   {job}: {len(ms)} meta line(s); seeds {[m['seed'] for m in ms]} (pre-registered {want_seed[job]}); "
            f"tp {[m['tp'] for m in ms]}; gpus {ms[-1]['gpus']}; T {ms[-1]['temperature']} top_p {ms[-1]['top_p']}; "
            f"chunk {ms[-1]['chunk']} chunk0 {ms[-1]['chunk0']} stop_after {ms[-1]['stop_after']} inflight "
            f"{ms[-1]['inflight']}; vllm {ms[-1]['vllm']}; rows (model, rev) {dict(revs)}")
    C.dump(RES, "provenance.json")
    (C.OUT / "provenance.txt").write_text("\n".join(LINES) + "\n")


if __name__ == "__main__":
    main()
