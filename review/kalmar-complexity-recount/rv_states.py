#!/usr/bin/env python3
"""Reviewer per-state table for tf1200 (run kalmar-complexity): own state walk over the builder's proof structure.

  python3 rv_states.py            # -> out/states_tf1200.json.gz

For every tf1200 record (data/kalmar/tf1200_kal_sl.jsonl, in order) the builder (kalmar.build 'sl') is re-run; its proof
text and tags must equal the record's.  The actions are walked in state-environment order (a line's opening action,
then its boxes' contents, each box closed by an `exact`, then `end`), keeping my own scope stack (sets of formulas:
premises, lemma lines, split hypotheses, box binders, lines so far in each frame) and the valuation of the split
boxes entered.  Per state:
  tag, group (close:* grouped), depth (open boxes),
  leaf      the innermost frame is the leaf frame (all atoms split; top level if no atoms)
  opener    leaf and the target's literal is not in scope (target = not p for the first false premise p, else the goal)
  explored  nodes visited by the post-order search for the first needed node whose literal is not in scope (leaf states)
  focus_h   height of that node (opener states); of the innermost binder inside a box opened at the leaf; else 0
  target_h  height of the target at leaf states
  decl_eq   (opener states with a `have`) the formula the action declares == the focus's literal
  act_len / decl_len   tokens of the action / of its declared formula (own segmentation of the canonical text)
"""
import gzip, json, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.expanduser('~/review/kalmar-complexity')
sys.path.insert(0, WS); sys.path.insert(0, os.path.join(WS, 'kalmar')); sys.path.insert(0, HERE)
import kalmar as K


def val(f, v):
    return K.val(f, v)


def neg(f):
    return ('not', f)


def needed(f, v):
    k = f[0]
    if k in ('atom', 'bot'):
        return []
    if k == 'not':
        return [f[1]]
    x, y = f[1], f[2]
    t, p, q = val(f, v), val(x, v), val(y, v)
    if k == 'and':
        return [x, y] if t else ([x] if not p else [y])
    if k == 'or':
        return ([x] if p else [y]) if t else [x, y]
    return [y] if q else ([x] if not p else [x, y])


def height(f):
    return 0 if f[0] in ('atom', 'bot') else 1 + max(height(g) for g in f[1:])


def actions_tokens(prompt, proof):
    from state_env import canonicalise
    toks = canonicalise(prompt, proof)
    acts, i = [], 0
    while i < len(toks):
        t = toks[i]
        if t == 'have':
            j = i
            while toks[j] not in (';', 'by'):
                j += 1
            acts.append(toks[i:j + 1]); i = j + 1
        elif t == 'exact':
            acts.append(toks[i:i + 2]); i += 2
        else:
            i += 1
    return acts


def walk_record(prompt, proof_ref, tags_ref):
    prem, goal = K.parse_prompt(prompt)
    b = K.Builder(prem, goal, 'sl')
    top = b.run()
    body, tags, st = K.render(top)
    assert body == proof_ref, 'builder proof differs from the record'
    assert tags == tags_ref, 'builder tags differ'
    atoms = K.atoms_of(prem + [goal])
    natoms = len(atoms)
    out = []
    scopes = [set()]                 # innermost last
    frames = [{'kind': 'top', 'binder': None}]
    v = {}

    def in_scope(f):
        return any(f in s for s in scopes)

    def leaf_now():
        # leaf frame: all atoms valued and the innermost frame is the split box that set the last one (or top, no atoms)
        if len(v) < natoms:
            return False
        fr = frames[-1]
        return fr['kind'] == 'split' and fr.get('level') == natoms or (natoms == 0 and fr['kind'] == 'top')

    def in_leaf_box():
        return len(v) == natoms and any(fr['kind'] == 'leafbox' for fr in frames)

    def state(tag, line):
        rec = {'tag': tag, 'depth': len(frames) - 1, 'leaf': 0, 'opener': 0, 'explored': 0, 'focus_h': 0,
               'target_h': 0, 'decl_eq': None}
        if leaf_now():
            rec['leaf'] = 1
            fp = next((p for p in prem if not val(p, v)), None)
            tgt = fp if fp is not None else goal
            rec['target_h'] = height(tgt)
            cnt = [0]

            def search(f):
                cnt[0] += 1
                lit = f if val(f, v) else neg(f)
                if in_scope(lit):
                    return None
                for c in needed(f, v):
                    r = search(c)
                    if r is not None:
                        return r
                return f
            fo = search(tgt)
            rec['explored'] = cnt[0]
            if fo is not None:
                rec['opener'] = 1
                rec['focus_h'] = height(fo)
                if line is not None:
                    rec['decl_eq'] = line.f == (fo if val(fo, v) else neg(fo))
        elif in_leaf_box():
            rec['focus_h'] = height(frames[-1]['binder'])
        out.append(rec)

    def walk(stmts):
        for ln in stmts:
            state(ln.tag, ln)
            if ln.boxes:
                for bx in ln.boxes:
                    hyp = bx.hyp.f
                    if bx.tag == 'split':
                        atom = hyp[1] if hyp[0] == 'atom' else hyp[1][1]
                        v[atom] = hyp[0] == 'atom'
                        frames.append({'kind': 'split', 'binder': hyp, 'level': len(v)})
                    else:
                        kind = 'leafbox' if len(v) == natoms and (natoms > 0 or True) and bx.tag.startswith('leaf') else 'box'
                        frames.append({'kind': kind, 'binder': hyp})
                    scopes.append({hyp})
                    walk(bx.stmts)
                    state(bx.close_tag, None)
                    scopes.pop()
                    fr = frames.pop()
                    if fr['kind'] == 'split':
                        del v[atom]
            scopes[-1].add(ln.f)
    walk(top)
    state('end', None)
    return out


def main():
    t0 = time.time()
    rows = []
    for ri, line in enumerate(open(os.path.join(WS, 'data/kalmar/tf1200_kal_sl.jsonl'))):
        r = json.loads(line)
        kt = r['kal_tags']
        kt = json.loads(kt.replace("'", '"')) if isinstance(kt, str) else kt
        recs = walk_record(r['prompt'], r['proof'], kt)
        acts = actions_tokens(r['prompt'], r['proof'])
        assert len(acts) == len(recs), (ri, len(acts), len(recs))
        for x, a in zip(recs, acts):
            x['act_len'] = len(a)
            x['decl_len'] = (a.index(':=') - a.index(':') - 1) if a[0] == 'have' else 0
            x['rec'] = ri
            x['n_atoms'] = int(r['n_atoms'])
            x['decl'] = ' '.join(a[a.index(':') + 1:a.index(':=')]) if a[0] == 'have' else ''
        rows.extend(recs)
        if ri % 200 == 0:
            print(ri, len(rows), f'{time.time() - t0:.0f}s', flush=True)
    with gzip.open(os.path.join(HERE, 'out', 'states_tf1200.json.gz'), 'wt') as fh:
        json.dump(rows, fh)
    print('states', len(rows), 'openers', sum(r['opener'] for r in rows),
          'decl_eq true', sum(1 for r in rows if r['decl_eq']), 'false', sum(1 for r in rows if r['decl_eq'] is False),
          f'{time.time() - t0:.0f}s')


if __name__ == '__main__':
    main()
