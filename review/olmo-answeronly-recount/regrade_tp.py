"""Reviewer re-grade: upstream IFBench (allenai/IFBench copy at ~/review/otr_rv/upstream/ifbench) strict + loose,
on every stored sample row. Answer = text after last </think> of ("</think>" + row text), stripped.
Also strict on the unstripped answer (diagnostic). Constraints from upstream IFBench_test.jsonl matched by prompt."""
import gzip, json, sys, glob, os, copy
UP = os.path.expanduser("~/review/otr_rv/upstream/ifbench")
sys.path.insert(0, UP)
import langdetect
langdetect.DetectorFactory.seed = 0
import nltk; nltk.data.path.insert(0, os.path.expanduser("~/nltk_data"))
import evaluation_lib as ev

A = os.path.expanduser("~/review/olmo-answeronly/artifacts/olmo_answeronly/samples")
up = [json.loads(l) for l in open(f"{UP}/IFBench_test.jsonl")]
byprompt = {u["prompt"]: u for u in up}
probs = {}
for l in open(os.path.expanduser("~/review/olmo-answeronly/olmo_ifomega/problems.jsonl")):
    p = json.loads(l)
    if p["pid"].startswith("ifbench_"):
        probs[p["pid"]] = p

def grade(u, resp):
    inp = ev.InputExample(key=u["key"], instruction_id_list=list(u["instruction_id_list"]), prompt=u["prompt"],
                          kwargs=copy.deepcopy(u["kwargs"]))
    s = ev.test_instruction_following_strict(inp, {u["prompt"]: resp})
    inp2 = ev.InputExample(key=u["key"], instruction_id_list=list(u["instruction_id_list"]), prompt=u["prompt"],
                           kwargs=[{k: v for k, v in kw.items() if v is not None} for kw in u["kwargs"]])
    lo = ev.test_instruction_following_loose(inp2, {u["prompt"]: resp})
    return bool(s.follow_all_instructions), [bool(x) for x in s.follow_instruction_list], bool(lo.follow_all_instructions)

out = open(sys.argv[2], "w")
f = sys.argv[1]
miss = 0
for l in gzip.open(f, "rt"):
    r = json.loads(l)
    p = probs[r["pid"]]
    u = byprompt.get(p["prompt"])
    if u is None:
        miss += 1; continue
    full = "</think>" + r["text"]
    ans_raw = full.rsplit("</think>", 1)[1]
    st, per, lo = grade(u, ans_raw.strip())
    st_raw = grade(u, ans_raw)[0]
    out.write(json.dumps({"rid": r["rid"], "i": int(r["i"]), "pid": r["pid"], "cond": r["cond"], "writer": r["writer"],
                          "job": r["job"], "trace": r["trace"], "strict": st, "per": per, "loose": lo,
                          "strict_unstripped": st_raw, "reopened": "</think>" in r["text"],
                          "finish": r["finish"], "n_tok": int(r["n_tok"]), "budget": int(r.get("budget",0))}) + "\n")
print(f, "missing-prompt rows", miss)
