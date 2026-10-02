"""evidence-atlas figures. Reads atlas/data/*.csv (and atlas/data/rescore_wholeproof.csv if present); writes atlas/figures/*.png.

Every point is one model seed; ticks are seed means. Families are colored by interface/format (state = proof-state
`lean_staten`, whole proof = `lean_seq`, token = ND token format); open markers = frozen Stage-1, filled = after RL.
Checker is in the row label: no mark = Lean alone, † = Lean ∧ nd_verify, ‡ = nd_verify alone."""
import csv, collections, math, os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(HERE, '..', 'data')
F = os.path.join(HERE, '..', 'figures')
os.makedirs(F, exist_ok=True)

# reference categorical palette (dataviz skill, light mode), fixed order
C = ['#2a78d6', '#eb6834', '#1baf7a', '#eda100', '#e87ba4', '#008300', '#4a3aa7', '#e34948']
INK, INK2, GRID = '#0b0b0b', '#52514e', '#e4e3df'
FMT_COLOR = {'lean_staten': C[0], 'lean_seq': C[1], 'token': C[2]}
FMT_NAME = {'lean_staten': 'proof state (lean_staten)', 'lean_seq': 'whole proof (lean_seq)', 'token': 'whole proof (ND token)'}
CHECK_MARK = {'lean_only': '', 'lean_and_ndverify': ' †', 'nd_verify': ' ‡'}

plt.rcParams.update({'font.size': 9, 'axes.edgecolor': INK2, 'axes.labelcolor': INK, 'xtick.color': INK2,
                     'ytick.color': INK, 'axes.spines.top': False, 'axes.spines.right': False,
                     'savefig.dpi': 160, 'savefig.bbox': 'tight', 'font.family': 'DejaVu Sans'})


def load(name):
    p = os.path.join(D, name)
    return list(csv.DictReader(open(p))) if os.path.exists(p) else []


def num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


# ---- the families shown on the shared-pool figures: (family, stage, label, format, frozen?) ----
ROWS = [
    # fork, proof state
    ('ours-3.2M-SN-v2-cap6', 'frozen', 'ours 3.2M state, cap 6 — frozen', 'lean_staten', True),
    ('ours-3.2M-SN-v2-cap6', 'T1', 'ours 3.2M state, cap 6 — T1 ladder', 'lean_staten', False),
    ('ours-3.2M-SN-cap12', 'frozen', 'ours 3.2M state, cap 12 — frozen', 'lean_staten', True),
    ('ours-3.2M-SN-cap12', 'T1', 'ours 3.2M state, cap 12 — T1 ladder', 'lean_staten', False),
    ('best-9.56M-cap6', 'frozen', 'best 9.56M state, cap 6 — frozen', 'lean_staten', True),
    ('best-9.56M-cap6', 'T1', 'best 9.56M state, cap 6 — T1 ladder', 'lean_staten', False),
    ('best-9.56M-cap12', 'frozen', 'best 9.56M state, cap 12 — frozen', 'lean_staten', True),
    ('best-9.56M-cap12', 'T1', 'best 9.56M state, cap 12 — T1 ladder', 'lean_staten', False),
    # fork, whole proof (this run's re-score)
    ('ours-3.2M-C0-wp-cap6', 'frozen', 'ours 3.2M whole proof, cap 6 — frozen*', 'lean_seq', True),
    ('ours-3.2M-C0-wp-cap6', 'T1', 'ours 3.2M whole proof, cap 6 — T1 ladder*', 'lean_seq', False),
    ('ours-3.2M-K12-wp-cap12', 'frozen', 'ours 3.2M whole proof, cap 12 — frozen*', 'lean_seq', True),
    ('ours-3.2M-K12-wp-cap12', 'T1', 'ours 3.2M whole proof, cap 12 — T1 ladder*', 'lean_seq', False),
    # Robbie's factorial (all after RL; cap-6 data; 2,400 s budget)
    ('robbie-factorial:lean-naive-ei', 'rl-harness-EI', 'Robbie naive pretrain, Lean, plain EI', 'lean_seq', False),
    ('robbie-factorial:lean-naive-leon', 'rl-leon-c005', 'Robbie naive pretrain, Lean, Leon RL + guided', 'lean_seq', False),
    ('robbie-factorial:lean-best-ei', 'rl-harness-EI', 'Robbie best 9.56M, Lean, plain EI', 'lean_seq', False),
    ('robbie-factorial:lean-best-leon', 'rl-leon-c005', 'Robbie best 9.56M, Lean, Leon RL + guided', 'lean_seq', False),
    ('robbie-state-recipes:198-SN', 'rl-harness-EI', 'Robbie recipe 198 9.56M, state SN, plain EI', 'lean_staten', False),
    ('robbie-state-recipes:198-C0', 'rl-harness-EI', 'Robbie recipe 198 9.56M, whole proof C0, plain EI', 'lean_seq', False),
    ('robbie-factorial:abs-naive-ei', 'rl-harness-EI', 'Robbie naive pretrain, token, plain EI', 'token', False),
    ('robbie-factorial:abs-naive-leon', 'rl-leon-c005', 'Robbie naive pretrain, token, Leon RL + guided', 'token', False),
    ('robbie-factorial:abs-best-ei', 'rl-harness-EI', 'Robbie best 9.56M, token, plain EI', 'token', False),
    ('robbie-factorial:abs-best-leon', 'rl-leon-c005', 'Robbie best 9.56M, token, Leon RL + guided', 'token', False),
]


def solved_by(rows, pool, k):
    """(family, stage) -> {'vals': [per-seed solved], 'checker': ...}; one row per seed (first seen wins)."""
    out = collections.defaultdict(lambda: {'vals': {}, 'checker': None})
    rows = sorted(rows, key=lambda r: 're-read' in (r.get('judge') or ''))    # a checkpoint's first read wins over re-reads
    for r in rows:
        if r['pool'] != pool or r['metric'] not in ('solved', 'dev_metric') or r['k'] != str(k):
            continue
        key = (r['family'], r['stage'])
        seed = r['seed'] + '|' + (r.get('judge') or '')
        v = num(r['value'])
        if v is None:
            continue
        o = out[key]
        if r['seed'] not in [s.split('|')[0] for s in o['vals']]:
            o['vals'][seed] = v
            o['checker'] = r['checker']
    return out


def strip(ax, data, n_pool, title, xlabel):
    ys, labels = [], []
    y = 0
    for fam, st, lab, fmt, frozen in ROWS:
        d = data.get((fam, st))
        if not d or not d['vals']:
            continue
        vals = list(d['vals'].values())
        col = FMT_COLOR[fmt]
        ax.scatter(vals, [y] * len(vals), s=34, facecolors='white' if frozen else col, edgecolors=col, linewidths=1.6,
                   zorder=3)
        m = sum(vals) / len(vals)
        ax.plot([m, m], [y - 0.32, y + 0.32], color=INK, lw=1.4, zorder=4)
        ax.text(n_pool * 1.01, y, f'{m:.1f}', va='center', fontsize=7.5, color=INK2)
        labels.append(lab + CHECK_MARK.get(d['checker'], ' ?'))
        ys.append(y)
        y += 1
    ax.set_yticks(ys)
    ax.set_yticklabels(labels, fontsize=7.8)
    ax.invert_yaxis()
    ax.set_xlim(0, n_pool * 1.08)
    ax.grid(axis='x', color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    ax.set_title(title, loc='left', fontsize=10, color=INK)
    ax.set_xlabel(xlabel)
    return len(ys)


def legend_handles():
    from matplotlib.lines import Line2D
    h = [Line2D([], [], marker='o', ls='', mfc=FMT_COLOR[f], mec=FMT_COLOR[f], mew=1.6, label=FMT_NAME[f])
         for f in ('lean_staten', 'lean_seq', 'token')]
    h += [Line2D([], [], marker='o', ls='', mfc='white', mec=INK2, mew=1.6, label='frozen Stage-1'),
          Line2D([], [], marker='o', ls='', mfc=INK2, mec=INK2, mew=1.6, label='after RL'),
          Line2D([], [], color=INK, lw=1.4, label='seed mean')]
    return h


tb = load('textbook72_harmonized.csv') + load('rescore_wholeproof.csv')
dh = load('dev_holdout_harmonized.csv') + load('rescore_wholeproof.csv')

# ---- figure 1: textbook72 solved at k = 256 ----
fig, ax = plt.subplots(figsize=(8.2, 7.2))
n = strip(ax, solved_by(tb, 'textbook72', 256), 72, 'textbook72: problems solved at pass@256 (T 0.8), every family scored',
          'problems solved (of 72); dots = model seeds')
ax.legend(handles=legend_handles(), loc='upper left', bbox_to_anchor=(0.6, 0.47), fontsize=7.5, frameon=False)
fig.text(0.0, -0.02, 'Checker: no mark = Lean alone; † = Lean ∧ nd_verify (Robbie\'s lean cells); ‡ = nd_verify alone (token cells). '
         '* = re-scored in this run.\nFork state reads: max_steps 96, max_action 512; whole-proof reads: max_new 512; '
         'Robbie: max_new 512. Robbie\'s cells are cap-6 data, 2,400 s budget.', fontsize=7, color=INK2)
fig.savefig(os.path.join(F, 'textbook72_by_family.png'))
plt.close(fig)

# ---- figure 2: dev1108 (k 64) and holdout250 (k 256) ----
fig, axs = plt.subplots(1, 2, figsize=(12.5, 6.6), sharey=False)
strip(axs[0], solved_by(dh, 'dev1108', 64), 1108, "Robbie's dev metric: dev1108 solved at k 64 (T 0.8)", 'theorems solved (of 1,108)')
strip(axs[1], solved_by(dh, 'holdout250', 256), 250, 'holdout250 solved at k 256 (T 0.8)', 'theorems solved (of 250)')
axs[1].legend(handles=legend_handles(), loc='upper left', bbox_to_anchor=(1.08, 1.0), fontsize=7.5, frameon=False)
fig.text(0.0, -0.02, 'Same pools as Robbie (dev1108 = sha1-even half of transfer.jsonl; holdout250 = his passk.py set). '
         'Robbie\'s dev values are copied from his tables (no per-theorem files in git); his recipe-198 state rows are Lean alone (the cleanest overlap).\n'
         'Checker marks as in the textbook72 figure. * = re-scored in this run.', fontsize=7, color=INK2)
fig.tight_layout()
fig.savefig(os.path.join(F, 'dev_holdout_by_family.png'))
plt.close(fig)

FAM_COLOR = {'state 3.2M cap 6': C[2], 'state 3.2M cap 12': C[0], 'state best 9.56M cap 6': C[4],
             'state best 9.56M cap 12': C[6], 'whole proof 3.2M cap 6': C[1], 'whole proof 3.2M cap 12': C[7],
             'whole proof 3.2M cap 14': C[3], 'Robbie best, Lean, Leon RL': C[5], 'Robbie naive, Lean, EI': '#9a9893'}


def fam_color(lab):
    return FAM_COLOR[lab.rstrip(' *†')]


# ---- figure 3: textbook72 pass@k curves (expected solved, unbiased estimator), seed means ----
CURVES = [('ours-3.2M-SN-v2-cap6', 'state 3.2M cap 6'), ('ours-3.2M-SN-cap12', 'state 3.2M cap 12'),
          ('best-9.56M-cap6', 'state best 9.56M cap 6'), ('best-9.56M-cap12', 'state best 9.56M cap 12'),
          ('ours-3.2M-C0-wp-cap6', 'whole proof 3.2M cap 6*'), ('ours-3.2M-K12-wp-cap12', 'whole proof 3.2M cap 12*'),
          ('robbie-factorial:lean-best-leon', 'Robbie best, Lean, Leon RL †'), ('robbie-factorial:lean-naive-ei', 'Robbie naive, Lean, EI †')]
pk = collections.defaultdict(lambda: collections.defaultdict(list))
for r in tb:
    if r['pool'] == 'textbook72' and r['metric'] == 'pass_at_k_expected_solved' and 're-read' not in (r.get('judge') or ''):
        stage = 'frozen' if r['stage'] == 'frozen' else ('rl' if r['stage'] in ('T1', 'rl-harness-EI', 'rl-leon-c005') else None)
        if stage and num(r['value']) is not None:
            pk[(r['family'], stage)][int(r['k'])].append(float(r['value']))
fig, axs = plt.subplots(1, 2, figsize=(11, 4.4), sharey=True)
for ax, stage, title in ((axs[0], 'frozen', 'frozen Stage-1'), (axs[1], 'rl', 'after RL')):
    for i, (fam, lab) in enumerate(CURVES):
        d = pk.get((fam, stage))
        if not d:
            continue
        ks = sorted(d)
        ys = [sum(d[k]) / len(d[k]) for k in ks]
        ls = ':' if 'robbie' in fam else ('--' if 'whole' in lab else '-')
        ax.plot(ks, ys, ls, color=fam_color(lab), lw=2, marker='o', ms=4, label=lab)
    ax.set_xscale('log', base=4)
    ax.set_xticks([1, 4, 16, 64, 256]); ax.set_xticklabels(['1', '4', '16', '64', '256'])
    ax.set_xlim(0.8, 300)
    ax.legend(fontsize=7, frameon=False, loc='upper left')
    ax.set_ylim(0, 60)
    ax.grid(color=GRID, lw=0.8); ax.set_axisbelow(True)
    ax.set_title(f'textbook72 pass@k — {title}', loc='left', fontsize=10)
    ax.set_xlabel('k (samples per problem, T 0.8)')
axs[0].set_ylabel('expected problems solved (of 72)')
fig.text(0.0, -0.04, 'Unbiased estimator Σ 1 − C(n−c,k)/C(n,k) from per-problem accepted counts (n = 256), mean over model seeds. '
         'Solid = fork proof state, dashed = fork whole proof (Lean alone), dotted = Robbie whole proof (Lean ∧ nd_verify).\nRobbie\'s factorial has no frozen read-outs on textbook72. * = re-scored in this run.',
         fontsize=7, color=INK2)
fig.tight_layout()
fig.savefig(os.path.join(F, 'textbook72_passk.png'))
plt.close(fig)

# ---- figure 4: length frontier, rr600 per-stratum solve rate ----
lf = load('length_frontier.csv')
LFAM = [('ours-3.2M-lean_seq-cap6', 'whole proof 3.2M cap 6'), ('ours-3.2M-lean_seq-cap12', 'whole proof 3.2M cap 12'),
        ('ours-3.2M-lean_staten-cap6', 'state 3.2M cap 6'), ('ours-3.2M-lean_staten-cap12', 'state 3.2M cap 12'),
        ('best-9.56M-lean_staten-cap6', 'state best 9.56M cap 6'), ('best-9.56M-lean_staten-cap12', 'state best 9.56M cap 12'),
        ('ours-3.2M-lean_seq-cap14', 'whole proof 3.2M cap 14')]
agg = collections.defaultdict(lambda: collections.defaultdict(lambda: collections.defaultdict(list)))
groups = collections.defaultdict(set)
seen = set()
for r in lf:
    if r['pool'] == 'rr600' and r['metric'] == 'solved' and r['L'] not in ('', None):
        groups[(r['family'], r['stage'])].add(r['apples_group'])
for r in lf:
    if r['pool'] == 'rr600' and r['metric'] == 'solved' and r['L'] not in ('', None):
        key = (r['family'], r['stage'])
        g = sorted(groups[key])[-1]          # prefer group B (max_steps 96) when a family was read twice
        if r['apples_group'] == g and (r['stage'], r['family'], r['L'], r['seed']) not in seen:   # one read per seed
            seen.add((r['stage'], r['family'], r['L'], r['seed']))
            agg[r['stage']][r['family']][int(r['L'])].append(float(r['value']) / float(r['n_pool']))
fig, axs = plt.subplots(1, 2, figsize=(11, 4.4), sharey=True)
for ax, stage, title in ((axs[0], 'frozen', 'frozen Stage-1'), (axs[1], 'T1', 'after the T1 ladder')):
    for i, (fam, lab) in enumerate(LFAM):
        d = agg[stage].get(fam)
        if not d:
            continue
        Ls = sorted(d)
        ys = [sum(d[L]) / len(d[L]) for L in Ls]
        nseed = max(len(v) for v in d.values())
        ax.plot(Ls, ys, '--' if 'whole' in lab else '-', color=fam_color(lab), lw=2, marker='o', ms=4, label=f'{lab} (n={nseed})')
    ax.legend(fontsize=7, frameon=False, loc='upper right' if stage == 'frozen' else 'center right')
    ax.set_xlim(10.7, 16.3)
    ax.set_ylim(0, 1.02)
    ax.set_xticks(range(11, 17))
    ax.grid(color=GRID, lw=0.8); ax.set_axisbelow(True)
    ax.set_title(f'length frontier, rr600 — {title}', loc='left', fontsize=10)
    ax.set_xlabel('L_true stratum (ND-derived minimal length; an upper bound under Lean)')
axs[0].set_ylabel('fraction of the 100 theorems solved (pass@256, T 0.8)')
fig.text(0.0, -0.05, 'Lean alone. rr600 = 100 theorems per stratum 11–16 (long-pool). Fork 3.2M state reads at max_steps 48 except where '
         're-read at 96 (best-state settings, preferred);\nwhole-proof reads max_new 1,536. Whole proof cap 12 / cap 14 frozen: one seed. '
         'No best-recipe whole-proof model exists. Dashed = whole proof, solid = proof state.', fontsize=7, color=INK2)
fig.tight_layout()
fig.savefig(os.path.join(F, 'length_frontier_rr600.png'))
plt.close(fig)

# ---- figure 5: the experiment map over time ----
em = load('experiment_map.csv')
AREAS = ['create_vs_elicit', 'data_caps', 'format', 'pretrain_recipe', 'rl_algorithm', 'interface', 'search_exploration',
         'measurement', 'llm_pretrained', 'infrastructure', 'other']
CK = {'lean_only': (C[0], 'Lean alone'), 'lean_and_ndverify': (C[1], 'Lean ∧ nd_verify'),
      'nd_verify': (C[2], 'nd_verify / older ND verifiers'), 'old_nd_verifier': (C[2], None)}
import datetime as dt
fig, ax = plt.subplots(figsize=(11, 4.8))
jit = collections.Counter()
for r in em:
    try:
        d = dt.date.fromisoformat(r['date'][:10])
    except ValueError:
        continue
    if d < dt.date(2026, 9, 1):
        d = dt.date(2026, 9, 1)            # June sprints pinned at the left edge
    y = AREAS.index(r['area_primary'])
    jit[(d, y)] += 1
    yy = y + 0.13 * ((jit[(d, y)] - 1) % 5 - 2)
    col = CK.get(r['checker_class'], ('#9a9893', None))[0]
    reviewed = r['review_status'].startswith('reviewed')
    mk = 's' if r['owner'] not in ('dan-agents', 'dan-codex') else 'o'
    ax.scatter([d], [yy], s=38, marker=mk, facecolors=col if reviewed else 'white', edgecolors=col, linewidths=1.5, zorder=3)
ax.axvline(dt.date(2026, 9, 27), color=INK2, lw=1, ls=':')
ax.text(dt.date(2026, 9, 27), -0.9, ' Lean alone decides (09-27)', fontsize=7, color=INK2)
ax.set_yticks(range(len(AREAS))); ax.set_yticklabels([a.replace('_', ' ') for a in AREAS])
ax.invert_yaxis(); ax.set_ylim(len(AREAS) - 0.4, -1.2)
ax.grid(axis='x', color=GRID, lw=0.8); ax.set_axisbelow(True)
import matplotlib.dates as mdates
ax.xaxis.set_major_locator(mdates.DayLocator(bymonthday=[1, 5, 9, 13, 17, 21, 25, 29]))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
from matplotlib.lines import Line2D
h = [Line2D([], [], marker='o', ls='', mfc=c, mec=c, label=l) for c, l in [CK['lean_only'], CK['lean_and_ndverify'], CK['nd_verify']]]
h += [Line2D([], [], marker='o', ls='', mfc='#9a9893', mec='#9a9893', label='no checker / mixed'),
      Line2D([], [], marker='o', ls='', mfc='white', mec=INK2, label='unreviewed (open)'),
      Line2D([], [], marker='s', ls='', mfc=INK2, mec=INK2, label='other members (square)')]
ax.legend(handles=h, fontsize=7, frameon=False, loc='upper left', bbox_to_anchor=(1.0, 1.0))
ax.set_title(f'The experiment map: {len(em)} experiments by question and date (June sprints pinned at 09-01)', loc='left', fontsize=10)
fig.tight_layout()
fig.savefig(os.path.join(F, 'experiment_map_timeline.png'))
plt.close(fig)
print('figures written to', os.path.normpath(F))
