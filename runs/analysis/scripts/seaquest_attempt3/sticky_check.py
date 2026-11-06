import sys, pickle
from collections import Counter
D = sys.argv[1]
AN = "nlurdf"
for name in ["claude", "astra"]:
    res = pickle.load(open(f"{D}/{name}_200.pkl", "rb"))
    coll = [r for r in res if r["cause"] in ("fish", "enemy_sub", "enemy_bullet")]
    pat = Counter()
    for r in coll:
        h = r["last_hist"]
        last = h[-1]
        # (policy action sampled, executed action) for last 2 steps
        pat[(AN[h[-2][1]] + "->" + AN[h[-2][2]], AN[last[1]] + "->" + AN[last[2]])] += 1
    print("===", name, "collision deaths", len(coll))
    print("  sticky override in final step:", sum(r["last_hist"][-1][4] for r in coll))
    print("  top (prev step sampled->executed, final step sampled->executed):")
    for k, v in pat.most_common(12): print("    ", k, v)
    # total sticky overrides in all steps (for base rate)
    tot_st = sum(r["sticky"] for r in res); tot_steps = sum(r["steps"] for r in res)
    print("  base rate: sticky overrides per step", tot_st / tot_steps)
