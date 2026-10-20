#!/usr/bin/env python3
"""A numpy interpreter of RASP-L (Zhou et al. 2023, arXiv 2310.16028) with an instrumented computation graph
(run kalmar-complexity).

Semantics follow the paper's RASP-L core (Listing "RASP-L core functions", file rasp/raspL_core.py in the arXiv
source, copied in the README):
  tokens, indices, full, tok_map, seq_map, select(k, q, pred) [causal: key index <= query index],
  sel_width, aggr(A, v, default, reduction in {mean, max, min}) [mean is truncated to int, as `astype(int)`],
  kqv(k, q, v, pred, default, reduction) = aggr(select(k, q, pred), v, ...).
The library macros (shift_right, cumsum, where, mask, maximum, argmax, num_prev, has_seen, firsts, lasts,
index_select, first_true, induct, induct_prev) expand into these primitives exactly as in the paper's
rasp/rasp_lib.py, except where noted (`mask` is one binary seq_map instead of the paper's three; the induction
sentinel null_val is -128 instead of the paper's -999, which is not an int8).

A program is ordinary straight-line Python that calls these functions on `Node`s: every call creates one node
of a static computation graph (built once, evaluated on batches).  Python loops over a fixed range are macros:
they unroll into separate nodes, so the op count is that of the unrolled RASP-L program.

Measures (`metrics`): ops by kind (static: a node is counted once however many positions it runs at; inputs and
constants are free), attention depth (longest chain of aggregate / sel_width nodes on a dependency path; a
select adds nothing by itself, its aggregate is the layer), MLP run (longest chain of tok_map / seq_map nodes
with no attention in between), sequential depth (attention + map nodes on the longest path), and every flagged
(non-RASP-L) node with its reason.

Non-RASP-L constructs are allowed but always flagged on the node:
  - select with several key / query fields (a conjunction of predicates on a tuple) -> 'multi-field select'
  - values outside int8 that are not index-typed (e.g. 16-bit truth tables) -> declare vt='comp' -> flagged
  - arithmetic between index-typed values or between counts (sel_width outputs) -> flag='...'
The interpreter checks at run time that every node declared int8 ('bint', the default for maps) stays in
[-128, 127]; a violation raises.
"""
import io, itertools, tokenize
import numpy as np

NONE = -1                      # default pointer / "no value"
_ids = itertools.count()


class Node:
    __slots__ = ('id', 'kind', 'args', 'fn', 'vfn', 'pred', 'red', 'default', 'label', 'flags', 'vt', 'tags')

    def __init__(self, kind, args=(), fn=None, vfn=None, pred=None, red=None, default=0, label=None, flags=(),
                 vt='bint'):
        self.id = next(_ids)
        self.kind, self.args, self.fn, self.vfn = kind, tuple(args), fn, vfn
        self.pred, self.red, self.default, self.label = pred, red, default, label
        self.flags, self.vt, self.tags = [f for f in flags if f], vt, set()
        if vt == 'comp' and kind in ('tok_map', 'seq_map', 'aggregate'):
            self.flags.append('composite value (not int8)')

    __hash__ = object.__hash__

    def __repr__(self):
        return f'<{self.kind}#{self.id}{":" + self.label if self.label else ""}>'

    # elementwise operators = tok_map / seq_map nodes (one op each, as in the paper's numpy-style programs).
    # Types: comparisons and logic give int8; +/- a constant keeps an index / count type (successor /
    # predecessor, allowed); +/- between two sequences of index or count type is flagged as index arithmetic.
    def _bin(self, other, f, vf, name, arith):
        vts = [self.vt] + ([other.vt] if isinstance(other, Node) else [])
        vt, flag = 'bint', None
        if arith:
            if 'comp' in vts:
                vt = 'comp'
            elif any(v in ('index', 'width') for v in vts):
                vt = next(v for v in vts if v in ('index', 'width'))
                if isinstance(other, Node):
                    flag = 'index/count arithmetic'
        if isinstance(other, Node):
            return seq_map(self, other, f, vfn=vf, label=name, vt=vt, flag=flag)
        c = other
        return tok_map(self, lambda x: f(x, c), vfn=(lambda x: vf(x, c)), label=f'{name}{c}', vt=vt, flag=flag)

    def __add__(self, o): return self._bin(o, lambda a, b: a + b, np.add, '+', True)
    def __sub__(self, o): return self._bin(o, lambda a, b: a - b, np.subtract, '-', True)
    def __eq__(self, o): return self._bin(o, lambda a, b: int(a == b), lambda a, b: (a == b).astype(np.int64), '==', False)
    def __ne__(self, o): return self._bin(o, lambda a, b: int(a != b), lambda a, b: (a != b).astype(np.int64), '!=', False)
    def __lt__(self, o): return self._bin(o, lambda a, b: int(a < b), lambda a, b: (a < b).astype(np.int64), '<', False)
    def __le__(self, o): return self._bin(o, lambda a, b: int(a <= b), lambda a, b: (a <= b).astype(np.int64), '<=', False)
    def __gt__(self, o): return self._bin(o, lambda a, b: int(a > b), lambda a, b: (a > b).astype(np.int64), '>', False)
    def __ge__(self, o): return self._bin(o, lambda a, b: int(a >= b), lambda a, b: (a >= b).astype(np.int64), '>=', False)
    def __and__(self, o): return self._bin(o, lambda a, b: int(bool(a) and bool(b)),
                                           lambda a, b: ((a != 0) & (b != 0)).astype(np.int64), '&', False)
    def __or__(self, o): return self._bin(o, lambda a, b: int(bool(a) or bool(b)),
                                          lambda a, b: ((a != 0) | (b != 0)).astype(np.int64), '|', False)
    def __invert__(self): return tok_map(self, lambda a: int(not a), vfn=lambda a: (a == 0).astype(np.int64),
                                         label='not')


# ------------------------------------------------------------------ predicates
class Pred:
    """kind: 'eq' (all fields equal), 'lt'/'le'/'gt'/'ge' (single field, key OP query), 'true',
    'kflag' (fn of the key only), 'fn' (vectorised fn(*keys, *queries) -> bool array)."""
    __slots__ = ('kind', 'fn', 'name')

    def __init__(self, kind, fn=None, name=None):
        self.kind, self.fn, self.name = kind, fn, name or kind


equals, lt, leq, gt, geq = Pred('eq'), Pred('lt'), Pred('le'), Pred('gt'), Pred('ge')
TRUE = Pred('true')


def kflag(fn, name='kflag'):
    """predicate depending on the key only (like the paper's `lambda k, q: k`); fn vectorised over key arrays."""
    return Pred('kflag', fn, name)


def pfn(fn, name='fn'):
    return Pred('fn', fn, name)


# ------------------------------------------------------------------ primitives
_TOK = {}


def tokens():
    if 'tokens' not in _TOK:
        _TOK['tokens'] = Node('tokens', label='tokens', vt='tok')
    return _TOK['tokens']


def indices(x=None):
    if 'indices' not in _TOK:
        _TOK['indices'] = Node('indices', label='indices', vt='index')
    return _TOK['indices']


def reset():
    """forget the cached input nodes (start a fresh program)."""
    _TOK.clear()


def full(x, c):
    return Node('const', fn=int(c), label=f'const{c}')


def tok_map(x, fn, vfn=None, label=None, vt='bint', flag=None):
    return Node('tok_map', (x,), fn=fn, vfn=vfn, label=label, vt=vt, flags=[flag] if flag else [])


def seq_map(x, y, fn, vfn=None, label=None, vt='bint', flag=None):
    return Node('seq_map', (x, y), fn=fn, vfn=vfn, label=label, vt=vt, flags=[flag] if flag else [])


def select(k, q, pred, label=None):
    ks = tuple(k) if isinstance(k, (tuple, list)) else (k,)
    qs = tuple(q) if isinstance(q, (tuple, list)) else (q,)
    flags = []
    if len(ks) > 1 or len(qs) > 1:
        flags.append('multi-field select (conjunction over a tuple key)')
    n = Node('select', ks + qs, pred=pred, label=label, flags=flags)
    n.fn = len(ks)                                   # number of key fields
    return n


def aggr(A, v, default=0, reduction='mean', label=None, vt=None):
    return Node('aggregate', (A, v), red=reduction, default=default, label=label,
                vt=vt if vt is not None else v.vt)


def sel_width(A, label=None):
    return Node('sel_width', (A,), label=label, vt='width')


def kqv(k, q, v, pred, default=0, reduction='mean', label=None):
    return aggr(select(k, q, pred), v, default=default, reduction=reduction, label=label)


# ------------------------------------------------------------------ the paper's library (rasp_lib.py)
_SHIFT = {}


def shift_index(n):
    """indices + n (successor / predecessor of an index: allowed in RASP-L); cached per n."""
    if n not in _SHIFT:
        _SHIFT[n] = tok_map(indices(), lambda i: i + n, vfn=lambda i: i + n, label=f'idx+{n}', vt='index')
    return _SHIFT[n]


_SHIFT_SEL = {}


def shift_sel(n):
    if n not in _SHIFT_SEL:
        _SHIFT_SEL[n] = select(shift_index(n), indices(), equals, label=f'shift{n}')
    return _SHIFT_SEL[n]


def shift_right(x, n, default=0, label=None):
    """the paper's shift_right: kqv(indices + n, indices, x, equals); the select is shared per n."""
    return aggr(shift_sel(n), x, default=default, reduction='max', label=label or f'shift{n}')


def cumsum(bool_array):
    return sel_width(select(bool_array, bool_array, kflag(lambda k: k != 0, 'k')))


def where(cond, x, y, label=None):
    """np.where(cond, x, y) exactly as the paper's library: three binary seq_maps, 0 as the neutral value."""
    vt = x.vt if isinstance(x, Node) else 'bint'
    xm = seq_map(x, cond, lambda a, m: a if m else 0, vfn=lambda a, m: np.where(m != 0, a, 0), label='where x', vt=vt)
    ym = seq_map(y, cond, lambda a, m: a if not m else 0, vfn=lambda a, m: np.where(m != 0, 0, a), label='where y',
                 vt=vt)
    return seq_map(xm, ym, lambda a, b: a if b == 0 else b, vfn=lambda a, b: np.where(b == 0, a, b),
                   label=label or 'where', vt=vt)


def mask(x, bool_mask, mask_val=0, label=None):
    """x where bool_mask else mask_val: one binary seq_map (the paper composes three)."""
    return seq_map(x, bool_mask, lambda a, m: a if m else mask_val,
                   vfn=lambda a, m: np.where(m != 0, a, mask_val), label=label or 'mask', vt=x.vt)


def maximum(x):
    return kqv(x, x, x, TRUE, reduction='max')


def minimum(x):
    return kqv(x, x, x, TRUE, reduction='min')


def argmax(x):
    mm = maximum(x)
    return kqv(mm, x, indices(), equals, reduction='max')


def num_prev(x, queries):
    return sel_width(select(x, queries, equals))


def has_seen(x, queries):
    return kqv(x, queries, full(x, 1), equals, default=0, reduction='max')


def firsts(x, queries, default=-1):
    return kqv(x, queries, indices(), equals, default=default, reduction='min')


def lasts(x, queries, default=-1):
    return kqv(x, queries, indices(), equals, default=default, reduction='max')


def index_select(x, idx, default=0, label=None):
    return kqv(indices(), idx, x, equals, default=default, reduction='max', label=label)


def first_true(x, default=-1):
    seen_true = kqv(x, full(x, 1), full(x, 1), equals, default=0, reduction='max')
    first_occ = seq_map(seen_true, shift_right(seen_true, 1), lambda c, p: int(bool(c) and not p))
    return kqv(first_occ, full(x, 1), indices(), equals, default=default, reduction='max')


def induct_kqv(k, q, v, offset, default=0, null_val=-128):
    indices_to_copy = firsts(shift_right(k, offset, default=null_val), q, default=null_val)
    return index_select(v, indices_to_copy, default=default)


def induct(k, q, offset, default=0, null_val=-128):
    return induct_kqv(k, q, k, offset=offset, default=default, null_val=null_val)


def induct_prev(k, q, offset, default=0, null_val=-128):
    indices_to_copy = firsts(k, q, default=null_val) + offset
    return index_select(k, indices_to_copy, default=default)


# ------------------------------------------------------------------ graph utilities
def ancestors(outs):
    seen, stack = {}, list(outs)
    while stack:
        n = stack.pop()
        if n.id in seen:
            continue
        seen[n.id] = n
        stack.extend(n.args)
    return [seen[i] for i in sorted(seen)]


ATTN = ('aggregate', 'sel_width')
MAPS = ('tok_map', 'seq_map')
FREE = ('tokens', 'indices', 'const')


def metrics(outs, extra_flags=None):
    """static measures of the program computing `outs` (a list of nodes)."""
    nodes = ancestors(outs)
    A, R, S = {}, {}, {}                  # attention depth, MLP run, sequential depth
    for n in nodes:
        ins = n.args
        a = max((A[x.id] for x in ins), default=0)
        s = max((S[x.id] for x in ins), default=0)
        if n.kind in ATTN:
            A[n.id], R[n.id], S[n.id] = a + 1, 0, s + 1
        elif n.kind in MAPS:
            A[n.id], R[n.id], S[n.id] = a, 1 + max((R[x.id] for x in ins), default=0), s + 1
        else:                               # inputs, constants, selects
            A[n.id], R[n.id], S[n.id] = a, max((R[x.id] for x in ins), default=0) if n.kind == 'select' else 0, s
    kinds = {}
    for n in nodes:
        if n.kind not in FREE:
            kinds[n.kind] = kinds.get(n.kind, 0) + 1
    flagged = [n for n in nodes if n.flags]
    fl = {}
    for n in flagged:
        for f in n.flags:
            fl[f] = fl.get(f, 0) + 1
    return {'ops': sum(kinds.values()), 'by_kind': kinds,
            'attn_depth': max((A[o.id] for o in outs), default=0),
            'mlp_run': max((R[n.id] for n in nodes), default=0),
            'seq_depth': max((S[o.id] for o in outs), default=0),
            'heads': kinds.get('aggregate', 0) + kinds.get('sel_width', 0),
            'flagged_ops': len(flagged), 'flags': fl}


def depth_of(n, outs_nodes=None):
    """attention depth of one node."""
    return metrics([n])['attn_depth']


def source_size(text, drop_kw=('label', 'flag', 'vfn', 'vt')):
    """(tokens, non-comment non-blank lines) of Python source text.  Not counted: comments, docstrings, layout
    tokens, and the keyword arguments in `drop_kw` (node labels, non-RASP-L flags, numpy fast paths that
    duplicate a map's scalar function, type annotations)."""
    toks = list(tokenize.generate_tokens(io.StringIO(text).readline))
    LAYOUT = (tokenize.COMMENT, tokenize.NL, tokenize.NEWLINE, tokenize.INDENT, tokenize.DEDENT,
              tokenize.ENDMARKER, tokenize.ENCODING)
    keep = [t.type not in LAYOUT for t in toks]
    prev = tokenize.INDENT
    for i, t in enumerate(toks):                       # docstrings / bare string statements
        if t.type == tokenize.STRING and prev in (tokenize.INDENT, tokenize.NEWLINE, tokenize.NL, tokenize.DEDENT):
            keep[i] = False
        if t.type not in (tokenize.COMMENT,):
            prev = t.type
    sig = [i for i, t in enumerate(toks) if t.type not in LAYOUT]
    pos = {i: k for k, i in enumerate(sig)}
    for k, i in enumerate(sig):
        t = toks[i]
        if not (t.type == tokenize.NAME and t.string in drop_kw and k + 1 < len(sig) and toks[sig[k + 1]].string == '='
                and k > 0 and toks[sig[k - 1]].string in (',', '(')):
            continue
        depth, m, params = 0, k + 2, 0
        while m < len(sig):
            s = toks[sig[m]]
            if s.type == tokenize.NAME and s.string == 'lambda' and depth == 0:
                params += 1                            # a lambda's parameter commas do not end the argument
            elif s.type == tokenize.OP:
                if s.string in '([{':
                    depth += 1
                elif s.string in ')]}':
                    if depth == 0:
                        break
                    depth -= 1
                elif s.string == ':' and depth == 0 and params:
                    params -= 1
                elif s.string == ',' and depth == 0 and not params:
                    break
            m += 1
        for q in range(k, m):
            keep[sig[q]] = False
        if toks[sig[k - 1]].string == ',':
            keep[sig[k - 1]] = False
        elif m < len(sig) and toks[sig[m]].string == ',':
            keep[sig[m]] = False
    n = sum(keep)
    lines = {toks[i].start[0] for i in range(len(toks)) if keep[i]}
    return n, len(lines)


def region(path, tag):
    """the program text between '# <tag> BEGIN' and '# <tag> END' in a file, without the lines tagged
    '# instrumentation'."""
    import re, textwrap
    out, on = [], False
    for line in open(path, encoding='utf-8'):
        if line.strip() == f'# {tag} BEGIN':
            on = True
            continue
        if line.strip() == f'# {tag} END':
            on = False
            continue
        if on and '# instrumentation' not in line:
            out.append(line)
    return textwrap.dedent(''.join(out))


# ------------------------------------------------------------------ evaluation
class Evaluator:
    """Evaluate the graph computing `outs` on a batch of equal-length token sequences.

    Liveness: every output is needed at the last position only, unless `all_positions`; a node is computed at
    every position if some aggregate reads it as a key or a value (or a map needing every position reads it),
    otherwise only at the last position (a pure optimisation: values at the last position are identical)."""

    def __init__(self, outs, all_positions=False, check_int8=True, inputs=()):
        self.outs = list(outs)
        self.nodes = ancestors(self.outs)
        self.check = check_int8
        self.inputs = {n.id for n in inputs}          # nodes whose values are supplied by the caller (`extra`)
        need = {}
        for o in self.outs:
            need[o.id] = 'all' if all_positions else 'last'
        for n in reversed(self.nodes):
            nd = need.get(n.id)
            if nd is None or n.id in self.inputs:
                continue
            if n.kind in MAPS:
                for x in n.args:
                    if need.get(x.id) != 'all':
                        need[x.id] = nd if need.get(x.id) is None else ('all' if nd == 'all' else need[x.id])
            elif n.kind in ATTN:
                sel = n.args[0]
                nk = sel.fn
                for x in sel.args[:nk]:
                    need[x.id] = 'all'
                for x in sel.args[nk:]:
                    if need.get(x.id) != 'all':
                        need[x.id] = nd if need.get(x.id) is None else ('all' if nd == 'all' else need[x.id])
                if n.kind == 'aggregate':
                    need[n.args[1].id] = 'all'
                if need.get(sel.id) != 'all':
                    need[sel.id] = nd
        self.need = need

    def run(self, toks, extra=None):
        """toks: int array (B, N).  extra: {node: array (B, N)} for externally supplied inputs.
        Returns {node: values}: (B,) for last-only nodes, (B, N) otherwise."""
        B, N = toks.shape
        env = {}
        idx = np.broadcast_to(np.arange(N, dtype=np.int64), (B, N))
        for n in self.nodes:
            nd = self.need.get(n.id)
            if nd is None or n.kind == 'select':
                continue
            if n.id in self.inputs:
                v = extra[n]
            elif n.kind == 'tokens':
                v = toks.astype(np.int64)
            elif n.kind == 'indices':
                v = idx
            elif n.kind == 'const':
                v = np.full((B, N), n.fn, dtype=np.int64)
            elif n.kind in MAPS:
                xs = [self._get(env, x, nd) for x in n.args]
                v = _apply_map(n, xs)
            elif n.kind in ATTN:
                v = self._attn(env, n, nd, B, N)
            else:
                raise ValueError(n.kind)
            if nd == 'last' and v.ndim == 2:
                v = v[:, -1]
            if self.check and n.vt in ('bint', 'tok') and n.kind not in ('tokens',) and v.size:
                lo, hi = int(v.min()), int(v.max())
                if lo < -128 or hi > 127:
                    raise OverflowError(f'{n} declared int8 but takes values in [{lo}, {hi}]')
            env[n.id] = v
        return env

    @staticmethod
    def _get(env, x, nd):
        v = env[x.id]
        if nd == 'last' and v.ndim == 2:
            return v[:, -1]
        return v

    def _attn(self, env, n, nd, B, N):
        sel = n.args[0]
        nk = sel.fn
        K = [env[x.id] for x in sel.args[:nk]]
        Q = [env[x.id] for x in sel.args[nk:]]
        if nd == 'last':
            Q = [q[:, -1] if q.ndim == 2 else q for q in Q]
        if n.kind == 'sel_width':
            V, red, default = None, 'count', 0
        else:
            V, red, default = env[n.args[1].id], n.red, n.default
        return attend(sel.pred, K, Q, V, red, default, last=(nd == 'last'))


_CACHE = {}


def _apply_map(n, xs):
    """elementwise map: a numpy expression if given, else the scalar function tabulated on the values present
    (results cached per node across batches)."""
    if n.vfn is not None:
        out = n.vfn(*xs)
        return np.asarray(out, dtype=np.int64) if not isinstance(out, np.ndarray) or out.dtype != np.int64 else out
    fn = n.fn
    cache = _CACHE.setdefault(n.id, {})
    if len(xs) == 1:
        x = xs[0]
        if not x.size:
            return x.astype(np.int64)
        lo, hi = int(x.min()), int(x.max())
        if hi - lo <= 1 << 20:
            present = np.zeros(hi - lo + 1, bool)
            present[(x - lo).ravel()] = True
            codes = np.flatnonzero(present)
            tab = np.zeros(hi - lo + 1, np.int64)
            tab[codes] = [cache[c + lo] if (c + lo) in cache else cache.setdefault(c + lo, fn(int(c + lo)))
                          for c in codes]
            return tab[x - lo]
        u, inv = np.unique(x, return_inverse=True)
        tab = np.array([fn(int(a)) for a in u], dtype=np.int64)
        return tab[inv].reshape(x.shape)
    x, y = np.broadcast_arrays(*xs)
    if not x.size:
        return x.astype(np.int64)
    xlo, ylo = int(x.min()), int(y.min())
    rx, ry = int(x.max()) - xlo + 1, int(y.max()) - ylo + 1
    code = (x - xlo) * ry + (y - ylo)
    if rx * ry <= 1 << 22:
        present = np.zeros(rx * ry, bool)
        present[code.ravel()] = True
        codes = np.flatnonzero(present)
        tab = np.zeros(rx * ry, np.int64)
        vals = []
        for c in codes:
            key = (int(c // ry) + xlo, int(c % ry) + ylo)
            v = cache.get(key)
            if v is None:
                v = cache[key] = fn(*key)
            vals.append(v)
        tab[codes] = vals
        return tab[code]
    u, first, inv = np.unique(code.ravel(), return_index=True, return_inverse=True)
    xf, yf = x.ravel()[first], y.ravel()[first]
    tab = np.array([fn(int(a), int(b)) for a, b in zip(xf, yf)], dtype=np.int64)
    return tab[inv].reshape(x.shape)


# ---- attention kernels
_NEUTRAL = {'max': np.iinfo(np.int64).min // 4, 'min': np.iinfo(np.int64).max // 4}


def _reduce_dense(mask, V, red, default):
    """mask (..., Nk) bool, V broadcastable to mask -> reduced over the last axis."""
    cnt = mask.sum(-1)
    if red == 'count':
        return cnt.astype(np.int64)
    Vb = np.broadcast_to(V, mask.shape)
    if red == 'max':
        out = np.where(mask, Vb, _NEUTRAL['max']).max(-1)
    elif red == 'min':
        out = np.where(mask, Vb, _NEUTRAL['min']).min(-1)
    elif red == 'mean':
        s = np.where(mask, Vb, 0).sum(-1)
        with np.errstate(divide='ignore', invalid='ignore'):
            out = np.trunc(s / np.maximum(cnt, 1)).astype(np.int64)
    elif red == 'and':                                   # bitwise AND = min on every bit channel (composite)
        out = np.bitwise_and.reduce(np.where(mask, Vb, -1), axis=-1)
    else:
        raise ValueError(red)
    return np.where(cnt > 0, out, default).astype(np.int64)


def _pred_dense(pred, K, Q):
    """K: list of (B, 1, Nk) or (B, Nk) arrays; Q: list of (B, Nq, 1) or (B, 1).  -> bool mask."""
    k = pred.kind
    if k == 'eq':
        m = None
        for a, b in zip(K, Q):
            e = (a == b)
            m = e if m is None else (m & e)
        return m
    if k == 'lt':
        return K[0] < Q[0]
    if k == 'le':
        return K[0] <= Q[0]
    if k == 'gt':
        return K[0] > Q[0]
    if k == 'ge':
        return K[0] >= Q[0]
    if k == 'true':
        return np.ones(np.broadcast_shapes(K[0].shape, Q[0].shape), dtype=bool)
    if k == 'kflag':
        m = pred.fn(*K)
        return np.broadcast_to(m, np.broadcast_shapes(K[0].shape, Q[0].shape))
    if k == 'fn':
        return pred.fn(*K, *Q)
    raise ValueError(k)


def attend(pred, K, Q, V, red, default, last=False):
    """causal select + aggregate.  K: key arrays (B, N); Q: query arrays (B, N) or (B,) if last; V: (B, N)."""
    B, N = K[0].shape
    if last:
        Kd = [k for k in K]
        Qd = [q[:, None] for q in Q]
        m = _pred_dense(pred, Kd, Qd)                        # (B, N); every key is <= the last query
        return _reduce_dense(m, V if V is not None else 0, red, default)
    k = pred.kind
    if k == 'eq' and len(K) == 1:
        off = _iota_offset(K[0])
        if off is not None and V is not None:           # keys are indices + off: a gather (one key per query)
            src = Q[0] - off
            ar = np.arange(N)[None, :]
            ok = (src >= 0) & (src < N) & (src + off <= ar) & (src <= ar)
            o = np.take_along_axis(V, np.clip(src, 0, N - 1), 1)
            return np.where(ok, o, default).astype(np.int64)
    if k == 'eq':
        return _eq_scan(K, Q, V, red, default)
    if k in ('true', 'kflag'):
        m = np.ones((B, N), bool) if k == 'true' else np.broadcast_to(pred.fn(*K), (B, N))
        return _prefix(m, V, red, default)
    if k in ('lt', 'le') and K[0] is not None and _is_iota(K[0]):
        pf = _prefix(np.ones((B, N), bool), V, red, default, with_count=True)
        out, cnt = pf
        q = Q[0] - (1 if k == 'lt' else 0)
        q = np.minimum(q, np.arange(N)[None, :])
        ok = q >= 0
        qc = np.clip(q, 0, N - 1)
        o = np.take_along_axis(out, qc, 1)
        return np.where(ok, o, 0 if red == 'count' else default).astype(np.int64)
    # generic dense fallback, chunked over queries
    out = np.empty((B, N), dtype=np.int64)
    step = max(1, int(4e6 // max(1, B * N)))
    ar = np.arange(N)
    for s in range(0, N, step):
        e = min(N, s + step)
        Kd = [kk[:, None, :] for kk in K]
        Qd = [qq[:, s:e, None] for qq in Q]
        m = _pred_dense(pred, Kd, Qd) & (ar[None, None, :] <= ar[s:e][None, :, None])
        out[:, s:e] = _reduce_dense(m, (V[:, None, :] if V is not None else 0), red, default)
    return out


def _iota_offset(a):
    """n if a == indices + n on every row, else None."""
    if a.shape[1] == 0:
        return None
    n = int(a[0, 0])
    r = np.arange(a.shape[1]) + n
    if np.array_equal(a[0], r) and (a.shape[0] == 1 or np.array_equal(a[-1], r)) and \
            (a.shape[0] <= 2 or np.array_equal(a[a.shape[0] // 2], r)):
        return n
    return None


def _is_iota(a):
    return a.shape[1] > 0 and a[0, 0] == 0 and np.array_equal(a[0], np.arange(a.shape[1])) and \
        (a.shape[0] == 1 or np.array_equal(a[-1], a[0]))


def _prefix(mask, V, red, default, with_count=False):
    """inclusive prefix reduce over positions where mask holds."""
    cnt = np.cumsum(mask, 1)
    if red == 'count':
        out = cnt.astype(np.int64)
    elif red == 'max':
        out = np.maximum.accumulate(np.where(mask, V, _NEUTRAL['max']), 1)
    elif red == 'min':
        out = np.minimum.accumulate(np.where(mask, V, _NEUTRAL['min']), 1)
    elif red == 'mean':
        s = np.cumsum(np.where(mask, V, 0), 1)
        with np.errstate(divide='ignore', invalid='ignore'):
            out = np.trunc(s / np.maximum(cnt, 1)).astype(np.int64)
    elif red == 'and':
        out = np.bitwise_and.accumulate(np.where(mask, V, -1), 1)
    else:
        raise ValueError(red)
    if red != 'count':
        out = np.where(cnt > 0, out, default).astype(np.int64)
    return (out, cnt) if with_count else out


def _eq_scan(K, Q, V, red, default):
    """for every query position q: reduce V over keys k <= q whose key tuple equals the query tuple."""
    B, N = K[0].shape
    kc = np.zeros((B, N), np.int64)
    qc = np.zeros((B, N), np.int64)
    R = 1
    for a, b in zip(K, Q):
        lo = min(int(a.min()), int(b.min()))
        hi = max(int(a.max()), int(b.max()))
        r = hi - lo + 1
        kc = kc * r + (a - lo)
        qc = qc * r + (b - lo)
        R *= r
        if R > (1 << 40):                       # compress through a joint ranking
            u, inv = np.unique(np.concatenate([kc.ravel(), qc.ravel()]), return_inverse=True)
            kc = inv[:B * N].reshape(B, N).astype(np.int64)
            qc = inv[B * N:].reshape(B, N).astype(np.int64)
            R = len(u)
    rows = np.arange(B, dtype=np.int64)[:, None] * R
    kc = (kc + rows).ravel()
    qc = (qc + rows).ravel()
    pos = np.broadcast_to(np.arange(N, dtype=np.int64), (B, N)).ravel()
    W = N + 1
    skey = kc * W + pos
    order = np.argsort(skey, kind='stable')
    sk = skey[order]
    scode = kc[order]
    # group starts in sorted order
    newg = np.empty(len(scode), bool)
    newg[0] = True
    newg[1:] = scode[1:] != scode[:-1]
    gid = np.cumsum(newg) - 1
    if red == 'count':
        gstart = np.flatnonzero(newg)
        acc = np.arange(len(scode)) - gstart[gid] + 1
    else:
        sv = V.ravel()[order].astype(np.int64)
        if red == 'max':
            span = int(sv.max() - sv.min()) + 1 if len(sv) else 1
            acc = np.maximum.accumulate(sv + gid * span) - gid * span
        elif red == 'min':
            span = int(sv.max() - sv.min()) + 1 if len(sv) else 1
            acc = np.minimum.accumulate(sv - gid * span) + gid * span
        elif red == 'mean':
            gstart = np.flatnonzero(newg)
            cs = np.cumsum(sv)
            base = np.where(gstart[gid] > 0, cs[gstart[gid] - 1], 0)
            s = cs - base
            c = np.arange(len(scode)) - gstart[gid] + 1
            acc = np.trunc(s / c).astype(np.int64)
        else:
            raise ValueError(red)
    j = np.searchsorted(sk, qc * W + pos, side='right') - 1
    ok = (j >= 0)
    jj = np.clip(j, 0, len(sk) - 1)
    ok &= scode[jj] == qc
    out = np.where(ok, acc[jj], 0 if red == 'count' else default)
    return out.reshape(B, N).astype(np.int64)


def run_program(outs, seqs, batch=256, all_positions=False, extra_fn=None, bucket=1, pad=0, max_tokens=1 << 18,
                inputs=()):
    """Evaluate outs on a list of int sequences (varying lengths); returns {node: list of per-sequence values}
    (scalars for last-only nodes).

    bucket > 1: sequences are left-padded with token `pad` to a multiple of `bucket` so that batches are larger.
    This is only valid for programs that ignore leading pad tokens (checked for the Kalmár policy by running
    both ways, see test_rasp.py --check-padding); index-typed outputs are shifted back by the pad length."""
    ev = Evaluator(outs, all_positions=all_positions, inputs=inputs)
    res = {o: [None] * len(seqs) for o in outs}
    bylen = {}
    for i, s in enumerate(seqs):
        L = -(-len(s) // bucket) * bucket
        bylen.setdefault(L, []).append(i)
    for L, ids in sorted(bylen.items()):
        bs = max(1, min(batch, max_tokens // max(L, 1)))
        for s in range(0, len(ids), bs):
            chunk = ids[s:s + bs]
            arr = np.full((len(chunk), L), pad, dtype=np.int64)
            padn = np.array([L - len(seqs[i]) for i in chunk])
            for r, i in enumerate(chunk):
                arr[r, L - len(seqs[i]):] = seqs[i]
            extra = extra_fn(chunk, arr, padn) if extra_fn else None
            env = ev.run(arr, extra)
            for o in outs:
                v = env[o.id]
                for r, i in enumerate(chunk):
                    if v.ndim == 1:
                        x = v[r]
                        if o.vt == 'index' and padn[r] and x >= padn[r]:
                            x = x - padn[r]
                        res[o][i] = x
                    else:
                        x = v[r, padn[r]:].copy()
                        if o.vt == 'index' and padn[r]:
                            x = np.where(x >= padn[r], x - padn[r], x)
                        res[o][i] = x
    return res
