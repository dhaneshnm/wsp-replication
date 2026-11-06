import pickle, collections
import numpy as np
D = "/private/tmp/claude-501/-Users-dhaneshneelamana-projects-wsp-replication/1de9272e-bb08-4c08-9f63-28011de783b7/scratchpad/analysis/asterix_attempt1"
for tag in ["claude", "astra"]:
    res = pickle.load(open(f"{D}/episodes_{tag}.pkl", "rb"))
    deaths = [r["death"] for r in res if r["death"]]
    print(tag, "N", len(res), "mean", np.mean([r["score"] for r in res]), "deaths", len(deaths))
    print("  cols", sorted(set(c for r in res for c in r["cols"])))
    c = collections.Counter(d["cause"] for d in deaths); print("  causes", dict(c), {k: v/len(deaths) for k, v in c.items()})
    tr = [d for d in deaths if d["cause"] == "trapped"]
    print("  trapped by player row:", dict(sorted(collections.Counter(d["player"][0] for d in tr).items())))
    print("  trapped safe_horiz nonempty:", sum(bool(d["safe_horiz"]) for d in tr), "of", len(tr))
    print("  trapped safe_horiz sets:", collections.Counter(tuple(d["safe_horiz"]) for d in tr))
    print("  all deaths by row:", dict(sorted(collections.Counter(d["player"][0] for d in deaths).items())))
    st = [d for d in deaths if d["cause"] == "sticky"]
    print("  sticky: all have sticky flag", all(d["sticky"] for d in st), "executed fatal", all(d["fatal"][d["executed"]] for d in st),
          "sampled nonfatal", all(not d["fatal"][d["sampled"] if d["sampled"] != 5 else 0] for d in st))
for tag in ["claude_s01", "claude_s0", "astra_s01", "astra_s0"]:
    res = pickle.load(open(f"{D}/ep2_{tag}.pkl", "rb"))
    sc = np.array([r["score"] for r in res]); L = np.array([r["steps"] for r in res])
    gs = sum(r["spawned"]["gold"] for r in res)
    pm = sum(r["prev_move_fatal"] for r in res); ps = sum(r["prev_move_steps"] for r in res)
    print(tag, "N", len(res), "mean %.3f len %.1f gold spawned %d collected %d rate %.4f prevmove fatal %d/%d=%.4f all-steps prev_fatal %.4f" % (
        sc.mean(), L.mean(), gs, sc.sum(), sc.sum()/gs, pm, ps, pm/ps, sum(r["prev_fatal"] for r in res)/L.sum()))
