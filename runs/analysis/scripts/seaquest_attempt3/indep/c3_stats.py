"""Claims 3, 6 (death causes), 8 (kills/steps): statistics from my own runner's 200-episode pickles."""
import pickle, numpy as np
from collections import Counter
AN = "/private/tmp/claude-501/-Users-dhaneshneelamana-projects-wsp-replication/1de9272e-bb08-4c08-9f63-28011de783b7/scratchpad/analysis/seaquest_attempt3/"
IN = AN + "indep/"
for name in ["claude", "astra"]:
    res = pickle.load(open(IN + f"{name}_0.1.pkl", "rb"))
    ana = {r["seed"]: r["cause"] for r in pickle.load(open(AN + f"{name}_200.pkl", "rb"))}
    st = np.array([r["steps"] for r in res]); k = np.array([r["kills"] for r in res])
    causes = Counter(r["cause"] for r in res)
    print(f"=== {name}: episodes {len(res)}  causes {dict(causes)}")
    amap = {"fish": "collision", "enemy_sub": "collision", "enemy_bullet": "collision"}
    dis = [r["seed"] for r in res if amap.get(ana[r["seed"]], ana[r["seed"]]) != r["cause"]]
    print("  cause disagreements with analyst's trace (collision classes merged):", len(dis), dis[:10])
    print(f"  mean steps {st.mean():.1f}  kills/ep {k.mean():.2f}  kills per 100 steps {100*k.sum()/st.sum():.3f}  bonus/ep {np.mean([r['bonus'] for r in res]):.2f}")
    ox = [r for r in res if r["cause"] == "oxygen"]
    print(f"  oxygen deaths {len(ox)} ({len(ox)/len(res):.1%}); divers at death among them: {dict(Counter(r['d_at_death'] for r in ox))}; with d>=1: {sum(r['d_at_death']>=1 for r in ox)}")
    # sticky-forced vertical moves
    ev = [e for r in res for e in r["sticky_vert"]]
    moved = [e for e in ev if e[2]]
    fatal = [e for e in moved if e[5]]
    print(f"  sticky-forced vertical (executed up/down != policy choice): {len(ev)}, changed row {len(moved)}, fatal {len(fatal)}")
    print(f"    fatal with dest-row danger in cols 6-9 at decision time: {sum(e[3] for e in fatal)}; with danger in cols x0-2..x0+1: {sum(e[4] for e in fatal)}")
    print(f"    all row changes with dest danger cols 6-9: {sum(e[3] for e in moved)}")
    deaths = [r for r in res if r["cause"] != "cap"]
    sf = [r for r in deaths if r["last_ex"] != r["last_a"] and r["last_ex"] in (2, 4) and r["last_row_post"] != r["last_row_pre"]]
    print(f"  deaths {len(deaths)}; final step = sticky-forced vertical row change: {len(sf)} ({len(sf)/len(deaths):.1%})")
    print(f"    of these, policy's own action would have survived that step (replay): {sum(bool(r['cf_policy_survives']) for r in sf)}")
    print(f"    their causes: {dict(Counter(r['cause'] for r in sf))}; sub col pre-step: {dict(Counter(r['last_col'] for r in sf))}")
    print(f"    (policy choice -> executed): {dict(Counter(('nlurdf'[r['last_a']] + '->' + 'nlurdf'[r['last_ex']]) for r in sf))}")
    ovr = [r for r in deaths if r["last_ex"] != r["last_a"]]
    print(f"  deaths whose final step had any sticky override: {len(ovr)}; collision deaths: {causes['collision']}; collision deaths with override on final step: {sum(r['cause']=='collision' for r in ovr)}")
    print(f"  all deaths where replaying the policy's own action survives the final step: {sum(bool(r['cf_policy_survives']) for r in deaths)}")
