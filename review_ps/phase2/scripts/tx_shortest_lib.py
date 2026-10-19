
def lines_of(proof):
    out = []
    for part in proof.split(";"):
        t = part.split()
        if not t or t[0] == "QED":
            continue
        k = int(t[0][1:]); i = 1; d = 0
        while t[i] == "|":
            i += 1; d += 1
        c = t.index(":", i)
        out.append({"k": k, "d": d, "f": " ".join(t[i:c]), "rule": t[c + 1], "refs": [int(x[1:]) for x in t[c + 2:]]})
    return out


def readable_why(prompt, proof):
    if ' F ' in prompt.replace('(', ' ').replace(')', ' '):
        return 'F in theorem'
    toks = prompt.split()
    for k in range(len(toks) - 2):
        if toks[k] in 'PQRS' and toks[k + 1] in ('&', 'v', '>') and toks[k + 2] == toks[k]:
            return 'X op X in theorem'
    for ln in lines_of(proof):
        if ln['rule'] == 'AS' and ln['f'] == 'F':
            return 'AS F'
        if ln['rule'] == 'R':
            return 'R line'
        if len(ln['refs']) >= 2 and len(set(ln['refs'][:2])) < 2 and ln['rule'] in ('ANDI', 'NEGE'):
            return 'ANDI/NEGE same line twice'
        if ln['rule'] in ('IMPI', 'NEGI') and ln['refs'][0] == ln['refs'][1]:
            return 'one-line box'
        if ln['rule'] == 'ORE' and (ln['refs'][1] == ln['refs'][2] and ln['refs'][3] == ln['refs'][4]):
            return 'ORE two one-line boxes'
    return ''
