"""Reviewer rebuild of every model input from stored ids: hand-rendered template + tokenizers (no HF chat template),
source trace ids from the inherited sample files, the registered change per condition. Compares sha256 with every
sample row's input_sha256 and checks generated ids decode to the stored text."""
import gzip, json, base64, hashlib, csv, os, collections, sys
import numpy as np
from tokenizers import Tokenizer
B = os.path.expanduser("~/review/olmo-answeronly")
A = f"{B}/artifacts/olmo_answeronly"
toks = {m: Tokenizer.from_file(os.path.expanduser(f"~/review/otr_rv/tok/{m}/tokenizer.json"))
        for m in ("allenai_Olmo-3-32B-Think-DPO", "allenai_Olmo-3.1-32B-Think")}
tok = toks["allenai_Olmo-3-32B-Think-DPO"]
def u(s): return np.frombuffer(base64.b64decode(s), dtype=np.int32).tolist()
def sha(ids): return hashlib.sha256(np.asarray(ids, dtype=np.int32).tobytes()).hexdigest()
up = {}
for l in open(os.path.expanduser("~/review/otr_rv/upstream/ifbench/IFBench_test.jsonl")):
    x = json.loads(l); up[x["prompt"]] = x
probs = {json.loads(l)["pid"]: json.loads(l) for l in open(f"{B}/olmo_ifomega/problems.jsonl") if '"ifbench_' in l}
src = {}
for f in ("F_s2300_ifb", "C1_s2300_ifb", "C2_s2300_ifb", "Leval_main"):
    for l in gzip.open(f"{A}/inputs/{f}.jsonl.gz", "rt"):
        r = json.loads(l); src[(r["job"], r["pid"], str(r["chunk"]), str(r["i"]))] = r
traces = {}
for row in csv.DictReader(open(f"{B}/olmo_transplant/traces.csv")):
    if row["kind"] == "rl": traces[row["trace"]] = (f'{row["job"]}|{row["pid"]}|{row["chunk"]}|{row["i"]}', int(row["think_k"]), row)
for row in csv.DictReader(open(f"{B}/olmo_answeronly/lora_traces.csv")):
    traces[row["trace"]] = (row["src"], int(row["think_k"]), row)
A1 = "After thinking, reply with only your final answer, exactly as drafted, with no introduction or explanation."
A2 = "Answer in at most 60 words."
SUF = {"A1": "\n\n" + A1, "A2": "\n\n" + A2}
A3 = tok.encode("I will now output exactly the final draft above and nothing else.\n", add_special_tokens=False).ids
EOS = {tok.token_to_id(t) for t in ("<|endoftext|>", "<|im_end|>") if tok.token_to_id(t) is not None}
def prompt(pid, suffix):
    p = probs[pid]["prompt"]; assert p in up
    s = ("<|im_start|>system\nYou are a helpful AI assistant.<|im_end|>\n<|im_start|>user\n" + p + suffix +
         "<|im_end|>\n<|im_start|>assistant\n<think>")
    return tok.encode(s, add_special_tokens=False).ids
stats = collections.Counter(); bad = []; trace_chk = {}
thinkend_tail = collections.Counter()
for j in ("R_dpo", "R_s2300", "C_dpo", "C_s2300", "L1_lora", "L2_dpo", "L3_lora"):
    for l in gzip.open(f"{A}/samples/{j}.jsonl.gz", "rt"):
        r = json.loads(l); c = r["cond"]
        s, k, trow = traces[r["trace"]]
        sj, spid, sch, si = s.split("|"); sr = src[(sj, spid, sch, si)]
        ids = u(sr["ids"])
        if r["trace"] not in trace_chk:
            # checks on the trace: think_k ends right after the first </think> (+ "\n\n" or "\n")
            dec = tok.decode(ids[:k], skip_special_tokens=False)
            thinkend_tail[repr(dec[-12:])] += 1
            trace_chk[r["trace"]] = (dec.count("</think>"), dec.rstrip().endswith("</think>"))
        pre = list(ids[:k])
        suffix = ""
        if c in SUF: suffix = SUF[c]
        elif c == "A3": pre = ids[:k - 3] + A3 + ids[k - 3:k]
        elif c == "A4":
            ans = ids[k:]; n = len([x for x in ans if x not in EOS]) if not any(x in EOS for x in ans) else ans.index(next(x for x in ans if x in EOS))
            kp = min(5, n - 1); pre = ids[:k] + ans[:kp]
            stats[f"A4 kp={kp}"] += 1
            assert int(r["answer_prefill_k"]) == kp, (r["rid"], kp, r["answer_prefill_k"])
        assert r["user_suffix"] == suffix
        p = prompt(r["pid"], suffix)
        ok = sha(p + pre) == r["input_sha256"]
        stats[(j, c, ok)] += 1
        if not ok: bad.append(r["rid"])
        assert int(r["prefix_len"]) == len(pre) and int(r["prompt_len"]) == len(p), r["rid"]
        g = u(r["ids"])
        if c == "A4":
            pf = r["prefill_ids"] if isinstance(r["prefill_ids"], list) else json.loads(r["prefill_ids"]); assert pf == pre[len(pre) - len(pf):]
            stats[("A4 text==dec(prefill+gen)", tok.decode(pf + g) == r["text"] or tok.decode(pf+[x for x in g if x not in EOS]) == r["text"])] += 1
        else:
            stats[("text==dec(gen)", tok.decode([x for x in g if x not in EOS]) == r["text"])] += 1
for k, v in sorted(stats.items(), key=str): print(k, v)
print("bad", len(bad), bad[:5])
print("trace </think> count in prefix", collections.Counter(v for v in trace_chk.values()))
print("prefix tails", thinkend_tail.most_common(6))
print("A3 ids", A3)
same = sum(toks["allenai_Olmo-3-32B-Think-DPO"].encode(x).ids == toks["allenai_Olmo-3.1-32B-Think"].encode(x).ids for x in [probs[p]["prompt"] for p in list(probs)[:50]])
print("tokenizers agree on 50 prompts:", same)

if len(sys.argv) > 1:
    seen = set()
    for j in ("R_dpo", "R_s2300", "L2_dpo"):
        for l in gzip.open(f"{A}/samples/{j}.jsonl.gz", "rt"):
            r = json.loads(l)
            if (j, r["cond"]) in seen or r["pid"] != ("ifbench_284" if r["cond"] == "A4" else r["pid"]): continue
            seen.add((j, r["cond"]))
            s, k, _ = traces[r["trace"]]; ids = u(src[tuple(s.split("|"))]["ids"])
            p = prompt(r["pid"], r["user_suffix"])
            print("=====", j, r["rid"], "| prompt tail:", repr(tok.decode(p[-30:], skip_special_tokens=False)))
            pre = ids[:k]
            if r["cond"] == "A3": pre = ids[:k-3] + A3 + ids[k-3:k]
            if r["cond"] == "A4": pre = ids[:k] + (r["prefill_ids"] if isinstance(r["prefill_ids"], list) else json.loads(r["prefill_ids"]))
            print("  prefix head:", repr(tok.decode(pre[:12], skip_special_tokens=False)))
            print("  prefix tail:", repr(tok.decode(pre[-25:], skip_special_tokens=False)))
            print("  answer head:", repr(r["text"][:120]))
