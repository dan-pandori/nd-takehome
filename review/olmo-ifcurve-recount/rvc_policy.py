"""Apply my acceptance policy for adjudicator proposals consistently to every confirmation (after the second
adversarial check found it applied in one direction only): a LOW-confidence confirmation is dropped (the reader
labels stand) whenever the group's reads have a majority against it -- two agreeing reads, or a 2-1 majority of
three. High-confidence confirmations and rule-5 / rule-6 entries are kept. Records the dropped groups in
hand/adj_rejected.json under 'policy_consistency_dropped'."""
import collections
import json

import rvc_hand as H


def main():
    rd = H.reads()
    cf = H.HAND / "confirm.json"
    conf = json.load(open(cf))
    rej = json.load(open(H.HAND / "adj_rejected.json"))
    dropped = []
    for key, c in list(conf.items()):
        if "(low)" not in c["reason"]:
            continue
        g = tuple(json.loads(key))
        labs = [r[1] for r in rd.get(g, [])]
        maj = None
        if len(labs) == 2 and labs[0] == labs[1]:
            maj = labs[0]
        elif len(labs) >= 3:
            maj = collections.Counter(labs[:3]).most_common(1)[0][0]
        if maj is not None and maj != c["label"]:
            dropped.append([g[0], g[1][:12], labs, c["label"], c.get("round")])
            conf.pop(key)
    rej["policy_consistency_dropped"] = dropped
    json.dump(conf, open(cf, "w"), indent=1)
    json.dump(rej, open(H.HAND / "adj_rejected.json", "w"), indent=1)
    print("dropped", len(dropped), dropped)


if __name__ == "__main__":
    main()
