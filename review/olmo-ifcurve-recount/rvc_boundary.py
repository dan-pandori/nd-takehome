"""Template boundary and response-token checks (every row of every job the run uses), plus thinking length under the
'before the LAST </think>' definition for rows with more than one '</think>'.

For every row: the response's first decoded characters (does the thinking start right after the generation prompt's
'<think>', i.e. no second '<think>' opener?), special tokens inside the response ids (only a final EOS 100257 is
expected), and the last-close thinking length. Prints five full junctions (my rebuilt prompt ids + the stored response
ids, decoded with special tokens shown) from five different jobs / checkpoints. Writes out/boundary.txt and
out/think_last.json ({json(key): ids before the last '</think>'}).
"""
import collections
import json

from tokenizers import Tokenizer

from rvc_core import ALL_JOBS, OUT, TOKJ, Pieces, Tee, iter_job, unb64, upstream_record

T = Tee("boundary.txt")
P = Pieces()
tk = Tokenizer.from_file(str(TOKJ))
SYSTEM = "You are a helpful AI assistant."
MK = b"</think>"


def my_ids(prompt):
    s = f"<|im_start|>system\n{SYSTEM}<|im_end|>\n<|im_start|>user\n{prompt}<|im_end|>\n<|im_start|>assistant\n<think>"
    return tk.encode(s, add_special_tokens=False).ids


stats = collections.Counter()
starts = collections.Counter()
specials = collections.Counter()
xt = collections.Counter()
last = {}
shown = 0
want_show = {"F_dpo_ifb", "M_s0050", "T4_s0750", "B_s2300", "X3_s1600"}
for job in ALL_JOBS:
    for r in iter_job(job, with_ids=True):
        ids = unb64(r["ids"])
        stats["rows"] += 1
        sp = [i for i in ids if i in P.special]
        xt[(r["finish"], bool(ids) and ids[-1] == 100257, tuple(sorted(set(sp) - {100257})))] += 1
        if sp:
            if sp == [100257] and ids[-1] == 100257:
                specials["final EOS only"] += 1
            else:
                specials["other specials " + ",".join(map(str, sorted(set(sp))))] += 1
        else:
            specials["none (cut or no EOS)" if r["finish"] == "length" else "none, finish " + r["finish"]] += 1
        head = r["text"][:7]
        starts["starts with <think>" if r["text"].lstrip().startswith("<think>") else "no <think> opener"] += 1
        b = P.bytes_of(ids)
        if b.count(MK) >= 2:
            z = b.rfind(MK)
            pos, n = 0, 0
            for i in ids:
                pb = b"" if i in P.special else P.piece[i]
                if pos + len(pb) <= z:
                    n += 1
                pos += len(pb)
            last[json.dumps([job, r["pid"], int(r["chunk"]), int(r["i"])])] = n
        if job in want_show and shown < 5:
            want_show.discard(job)
            shown += 1
            pr = my_ids(upstream_record(r["pid"])[1]["prompt"])
            full = pr + ids
            j = len(pr)
            T(f"--- junction {job} {r['pid']} chunk {r['chunk']} i {r['i']} (prompt {len(pr)} ids, row prompt_tokens "
              f"{r.get('prompt_tokens')}):")
            T("    ..." + repr(tk.decode(full[j - 8:j], skip_special_tokens=False)) + "  ||  " +
              repr(tk.decode(full[j:j + 12], skip_special_tokens=False)) + " ...")
            T("    last response ids decoded: " + repr(tk.decode(ids[-6:], skip_special_tokens=False)))
T("rows:", stats["rows"])
T("response opener:", dict(starts))
T("special tokens inside response ids:", dict(specials))
T("rows with >= 2 '</think>':", len(last))
T("cross-tab (finish, ends with EOS 100257, other special ids inside):")
for k, v in sorted(xt.items(), key=lambda x: -x[1]):
    T("   ", k, v)
json.dump(last, open(OUT / "think_last.json", "w"))
