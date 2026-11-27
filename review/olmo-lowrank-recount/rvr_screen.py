"""My mechanical rule-1 screen (rule 1 of olmo_ifomega/handcheck_rule_if.md, implemented literally; unit-tested) and the
answer texts of the hand-gate scope. -> out/answers_scope.json.gz {draw key: answer}, out/screen.json {group: reason}.
A group is (pid, sha256 of the whitespace-collapsed answer)."""
import gzip
import json
import re
import sys

from rvr_core import OUT, answer_of, iter_job, sha_text, upstream_record, wsnorm

PER_SENT = {"sentence:increment", "sentence:alliteration_increment", "words:last_first", "format:emoji"}


def one_sentence(a):
    """No '.', '!' or '?' followed by more text (closing quotes / brackets / further marks skipped): an emoji, a tag or
    a word after a full stop all mean more than one sentence."""
    t = a.strip()
    for m in re.finditer(r"[.!?]", t):
        rest = re.sub(r"^[.!?\"'”’)\]]*", "", t[m.end():])
        if rest.strip():
            return False
    return True


def flag(pid, ans):
    ids = set(upstream_record(pid)[1]["instruction_id_list"])
    if ids & PER_SENT and one_sentence(ans):
        return "one sentence (per-sentence constraint)"
    if "format:line_indent" in ids and len([l for l in ans.splitlines() if l.strip()]) <= 1:
        return "one non-empty line (line_indent)"
    if "format:sub-bullets" in ids and not any(l.lstrip().startswith("*") for l in ans.splitlines()):
        return "no line starting with * (sub-bullets)"
    return None


def tests():
    cases = [("Hello world. Bye now", False), ("Hello world.</i> Bye", False), ("Hello world.<br>Bye", False),
             ("Sun 😀. Moon 🌙.", False), ("Hello world 😀 bye 🌙", True), ("Hello world.", True),
             ("Hello world...", True), ('He said "hi." She left.', False), ('He said "hi."', True),
             ("One (two). Three", False), ("Wait! Really? Yes.", False), ("no punctuation at all", True),
             ("Ends with a quote.'", True), ("A. B", False), ("3.5 apples", False), ("Ends here. 😀", False),
             ("Line one\nLine two", True)]
    bad = [(s, w) for s, w in cases if one_sentence(s) != w]
    print("one_sentence unit tests:", len(cases) - len(bad), "/", len(cases), bad)
    return not bad


def main():
    assert tests()
    S = json.load(open(OUT / "scope.json"))["scope"]
    want = {(d["job"], d["pid"], d["chunk"], d["i"]) for d in S}
    ans = {}
    for job in sorted({d["job"] for d in S}):
        for r in iter_job(job):
            k = (job, r["pid"], int(r["chunk"]), int(r["i"]))
            if k in want:
                ans[k] = answer_of(r["text"])
    assert len(ans) == len(want)
    for d in S:
        assert sha_text(wsnorm(ans[(d["job"], d["pid"], d["chunk"], d["i"])])) == d["ans_sha"]
    with gzip.open(OUT / "answers_scope.json.gz", "wt") as f:
        json.dump({json.dumps(list(k)): v for k, v in ans.items()}, f)
    scr = {}
    for d in S:
        g = f"{d['pid']}|{d['ans_sha']}"
        why = flag(d["pid"], ans[(d["job"], d["pid"], d["chunk"], d["i"])])
        if why:
            scr[g] = why
    json.dump(scr, open(OUT / "screen.json", "w"), indent=1)
    from collections import Counter
    print("screened groups", len(scr), Counter(scr.values()))
    print("screened draws by job", Counter(d["job"] for d in S if f"{d['pid']}|{d['ans_sha']}" in scr))
    print("screened by pid", Counter(g.split("|")[0] for g in scr))


if __name__ == "__main__":
    main()
