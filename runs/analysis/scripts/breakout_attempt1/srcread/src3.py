import sys, pickle, re
sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import numpy as np
from collections import Counter
D = "/private/tmp/claude-501/-Users-dhaneshneelamana-projects-wsp-replication/1de9272e-bb08-4c08-9f63-28011de783b7/scratchpad/analysis/breakout_attempt1/"

ep = pickle.load(open(D + "episodes_claude_200.pkl", "rb"))
sc = np.array([r["score"] for r in ep]); ln = np.array([r["steps"] for r in ep])
print("instr pkl: n", len(ep), "mean score", sc.mean(), "mean len", ln.mean(), "seeds", ep[0]["seed"], ep[-1]["seed"])
np.save(D + "srcread/instr_scores.npy", np.stack([[r["seed"] for r in ep], sc, ln]))

for fn in ["stats_claude_softmax_0.1_200.pkl", "stats_claude_argmax_0.0_200.pkl", "stats_claude_argmax_0.1_200.pkl",
           "stats_claude_softmax_0.0_200.pkl", "stats_variant_samedir_softmax_0.1_200.pkl", "stats_variant_samedir_argmax_0.1_200.pkl"]:
    res = pickle.load(open(D + fn, "rb"))
    tot = Counter()
    for r in res: tot.update(r)
    s = np.array([r["score"] for r in res])
    print(f"=== {fn}: n={len(res)} mean {s.mean():.4f} misses {tot['done']} meanlen {tot['len']/len(res):.2f} steps {tot['steps']}")
    print(f"   catches {tot['catches']} same {tot['catch_same_dir']} reverse {tot['catch_reverse']} bricks/catch {tot['score']/max(1,tot['catches']):.4f} drought {tot['drought_steps']/tot['steps']:.4f}")
    print(f"   gH_err {tot['gH_err']} gV_err {tot['gV_err']}  score>21: {(s>21).sum()} score==21: {(s==21).sum()} score<21: {(s<21).sum()}")
    if fn == "stats_claude_softmax_0.1_200.pkl":
        gh = Counter(); gv = Counter()
        for k, v in tot.items():
            m = re.match(r"gH_err dx=(-?\d+) dy=(-?\d+) r=(\d+) c=(\d+)", k)
            if m: gh[("dx", int(m[1]), "dy", int(m[2]), "r", int(m[3]))] += v
            m = re.match(r"gV_err dx=(-?\d+) dy=(-?\d+) r=(\d+) dir=(\d+)", k)
            if m: gv[("dx", int(m[1]), "dy", int(m[2]), "r", int(m[3]), "dir", int(m[4]))] += v
        print("   gH errors by (dx,dy,row):", sorted(gh.items(), key=lambda kv: -kv[1]))
        print("   gH errors with r==8 and dy==0:", sum(v for k, v in gh.items() if k[5] == 8 and k[3] == 0), "of", sum(gh.values()))
        print("   gV errors by (dx,dy,row,dir):", sorted(gv.items(), key=lambda kv: -kv[1]))
        up = lambda d: d in (0, 1)
        print("   gV errors row0 dy0 upward dir:", sum(v for k, v in gv.items() if k[5] == 0 and k[3] == 0 and up(k[7])))
        print("   gV errors dy0 upward dir any row:", sum(v for k, v in gv.items() if k[3] == 0 and up(k[7])), "rows:", Counter({k[5]: 0 for k in gv}) and {r: sum(v for k, v in gv.items() if k[5] == r) for r in sorted({k[5] for k in gv})})
        fs = np.array([r["first_drought_score"] for r in res])
        m = fs == 21
        print("   first drought at score 21:", m.sum(), "of those final >21:", (s[m] > 21).sum())
