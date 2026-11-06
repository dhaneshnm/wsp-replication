import pickle, collections
import numpy as np

D = "/private/tmp/claude-501/-Users-dhaneshneelamana-projects-wsp-replication/1de9272e-bb08-4c08-9f63-28011de783b7/scratchpad/analysis/asterix_attempt1"
ACT = ["n", "l", "u", "r", "d", "f"]
# exact ramp_index (pre-step) for each step t, from asterix.py's timer logic
RAMP, rt, ri, sp, mv = [], 100, 0, 10, 5
for t in range(10000):
    RAMP.append(min(ri, 9))
    if sp > 1 or mv > 1:
        if rt >= 0: rt -= 1
        else:
            if mv > 1 and ri % 2: mv -= 1
            if sp > 1: sp -= 1
            ri += 1; rt = 100
print("first step of each ramp index:", [RAMP.index(k) for k in range(10)])
for tag in ["claude", "astra"]:
    res = pickle.load(open(f"{D}/episodes_{tag}.pkl", "rb"))
    N = len(res)
    sc = np.array([r["score"] for r in res]); st = np.array([r["steps"] for r in res])
    print(f"\n===== {tag}: N={N} mean score {sc.mean():.2f}  mean len {st.mean():.1f}  median len {np.median(st):.0f}  gold/step {sc.sum()/st.sum():.4f}")
    print("columns ever occupied:", sorted(set(c for r in res for c in r["cols"])))
    print("capped episodes:", sum(r["death"] is None for r in res))
    deaths = [r["death"] for r in res if r["death"]]
    cnt = collections.Counter(d["cause"] for d in deaths)
    print("death causes:", dict(cnt))
    # detail by cause
    for cause in ["trapped", "sticky", "sampled_fatal"]:
        ds = [d for d in deaths if d["cause"] == cause]
        if not ds:
            continue
        print(f"  [{cause}] n={len(ds)}  ramp at death: {dict(collections.Counter(min(d['ramp'],9) for d in ds))}")
        if cause == "trapped":
            print("    left/right would have survived this step:", sum(bool(d["safe_horiz"]) for d in ds))
            print("    earliest k (steps before death) from which vertical-only survival was possible:",
                  dict(collections.Counter(d["look_v"] for d in ds)))
            print("    same with left/right allowed:", dict(collections.Counter(d["look_all"] for d in ds)))
            print("    move_timer at death step (0 = entities move this step):", dict(collections.Counter(d["move_timer"] for d in ds)))
        if cause == "sticky":
            print("    executed (repeated) action:", dict(collections.Counter(ACT[d["executed"]] for d in ds)),
                  " sampled action:", dict(collections.Counter(ACT[d["sampled"]] for d in ds)))
        if cause == "sampled_fatal":
            ps = [d["p"][d["sampled"]] for d in ds]
            print("    sampled action:", dict(collections.Counter(ACT[d["sampled"]] for d in ds)),
                  " p(sampled):", np.round(sorted(ps), 3).tolist())
            print("    sticky flag among these:", sum(d["sticky"] for d in ds))
            print("    prob mass net put on fatal vertical actions:",
                  np.round(sorted(sum(d["p"][b] for b in [0, 2, 4] if d["fatal"][b]) for d in ds), 3).tolist())
    # all deaths: probability mass on fatal actions at the death step when a safe one existed
    ds = [d for d in deaths if d["cause"] != "trapped"]
    # deaths by difficulty
    print("ramp index at death (all):", dict(sorted(collections.Counter(min(d['ramp'], 9) for d in deaths).items())))
    print("death step percentiles 10/25/50/75/90:", np.percentile([d["steps"] for d in deaths], [10, 25, 50, 75, 90]).round(0).tolist())
    # gold by phase (ramp index)
    g = collections.Counter()
    for r in res:
        for (t, ramp, rew) in r["gold"]:
            g[min(ramp, 9)] += rew
    # steps by phase
    s = collections.Counter()
    for r in res:
        # approximate phase of step t from schedule: ramp_index k reached after ~101*(k) steps; use exact counting via gold? use schedule
        for t in range(r["steps"]):
            s[RAMP[t]] += 1
    print("gold per 100 steps by ramp phase (ramp index; >=8 means move_speed 1):",
          {k: round(100 * g[k] / s[k], 2) for k in sorted(s) if s[k]})
    print("share of total gold from ramp>=8:", round(sum(v for k, v in g.items() if k >= 8) / sum(g.values()), 3))
    print("vertical moves per 100 steps:", round(100 * sum(r["moves"] for r in res) / st.sum(), 2))
    rs = np.sum([r["row_steps"] for r in res], axis=0)
    print("fraction of steps per row 1..8:", (rs[1:9] / rs.sum()).round(3).tolist())
