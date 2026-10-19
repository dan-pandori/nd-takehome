"""RL numbers quoted by the blog, from the reviewer's rl_<arm>.json (create-or-elicit found files; 9.56 M ALiBiGPT lean_staten
policies from scratch on K12 / K12- / dose1, 16 rounds T1 expert iteration; round 1 = samples of the pretrained model)."""
import json
O = '/home/dan/review/proof-strategies/review_ps/out/'
arms = ['full_s3','full_s4','full_s5','dose1_s0','dose1_s1','dose1_s2','ko_s0','ko_s1','ko_s2','ko_s3','ko_s4','ko_s5']
for a in arms:
    d = json.load(open(O + f'rl_{a}.json'))
    new, fw, w, ng = d['new_by_round'], d['free_working_by_round'], d['working_by_round'], d['neg_goal_working_by_round']
    fr2 = sum(fw[str(r)] for r in range(2, 17)); wr2 = sum(w[str(r)] for r in range(2, 17)); ngr2 = sum(ng[str(r)] for r in range(2, 17))
    sc = d['sigma_cov_first_working_round']
    sc1 = sum(1 for v in sc.values() if v == 1)
    tot = sum(new.values())
    print(f"{a}: new_r1={new['1']} free_r1={fw['1']} ({100*fw['1']/new['1']:.3f} %) working_r1={w['1']} ({100*w['1']/new['1']:.3f} %) ng_r1={ng['1']} | "
          f"free_r2-16={fr2} working_r2-16={wr2} ng_r2-16={ngr2} | r16: new={new['16']} free={fw['16']} ({100*fw['16']/new['16']:.2f} %) working={w['16']} ({100*w['16']/new['16']:.2f} %) | "
          f"sc_r1={sc1} sc_by16={len(sc)} | total distinct={tot} free_all={sum(fw.values())}")
