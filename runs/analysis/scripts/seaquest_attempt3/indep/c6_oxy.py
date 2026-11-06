"""Claims 6 and 12: for Claude's oxygen deaths with divers aboard, replay with per-step hidden units and ground-truth
objects; measure the final SURF window and what blocks the climb. Direction comes from the env objects, not the trail."""
import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
IN = "/private/tmp/claude-501/-Users-dhaneshneelamana-projects-wsp-replication/1de9272e-bb08-4c08-9f63-28011de783b7/scratchpad/analysis/seaquest_attempt3/indep/"
sys.path.insert(0, IN)
import pickle, numpy as np
from collections import Counter
import myrun


def up_unit_cf(net, h1, row):
    """Up unit for `row` with that row-above danger unit forced off."""
    h = h1.copy(); h[16 + row - 1] = -1.0
    return np.tanh(h @ net["W2"] + net["b2"])[row - 1]


def summarize(net, r):
    log = r.pop("log")
    surf = [s["h1"][26] > 0 for s in log]
    # final contiguous SURF window
    t = len(log) - 1
    win = []
    if surf[t]:
        while t > 0 and surf[t - 1]:
            t -= 1
        win = list(range(t, len(log)))
    cls = Counter()
    for i in win:
        s = log[i]; row = s["row"]
        if row == 0: cls["row0"] += 1
        elif s["h2"][row - 1] > 0: cls["up_unit_on"] += 1
        elif row >= 2 and s["h1"][16 + row - 1] > 0:
            cls["vetoed_by_U_above"] += 1
            cls["vetoed_and_cf_up_on"] += up_unit_cf(net, s["h1"], row) > 0
        elif row == 1: cls["row1_other"] += 1
        else: cls["other"] += 1
    # all SURF-on veto steps in the episode, with ground-truth blockers
    veto = 0; harmless_all = 0; harmless_cf_up = 0; blockers = Counter(); cf_up = 0
    for s, on in zip(log, surf):
        row = s["row"]
        if not on or row < 2 or s["h2"][row - 1] > 0 or s["h1"][16 + row - 1] <= 0:
            continue
        veto += 1
        cells = [o for o in s["above"] if 6 <= o[1] <= 9]
        harmless = all((o[1] <= 7 and not o[2]) or (o[1] == 9 and o[2]) for o in cells)
        cfu = up_unit_cf(net, s["h1"], row) > 0
        cf_up += cfu
        harmless_all += harmless; harmless_cf_up += harmless and cfu
        for o in cells:
            blockers[(o[0], o[1], "R" if o[2] else "L")] += 1
    return dict(seed=r["seed"], d=r["d_at_death"], cause=r["cause"], steps=r["steps"], win=len(win),
                win_cls=dict(cls), veto=veto, harmless_all=harmless_all, harmless_cf_up=harmless_cf_up,
                cf_up=cf_up, blockers=dict(blockers),
                win_rows=Counter(log[i]["row"] for i in win))


if __name__ == "__main__":
    base = pickle.load(open(IN + "claude_0.1.pkl", "rb"))
    seeds = [r["seed"] for r in base if r["cause"] == "oxygen" and r["d_at_death"] >= 1]
    print("oxygen deaths with d>=1:", len(seeds), seeds)
    res = myrun.run_many(myrun.CLAUDE, seeds, detail_fn=summarize)
    assert all(r["cause"] == "oxygen" for r in res)
    pickle.dump(res, open(IN + "oxy_detail.pkl", "wb"))
    tot = Counter(); W = 0
    for r in res:
        tot.update(r["win_cls"]); W += r["win"]
    print("final SURF window: episodes with SURF on at death", sum(r["win"] > 0 for r in res), "total window steps", W)
    print("  classes:", dict(tot), f" vetoed share {tot['vetoed_by_U_above']/W:.1%}")
    print("  window rows:", dict(sum((r["win_rows"] for r in res), Counter())))
    V = sum(r["veto"] for r in res); H = sum(r["harmless_all"] for r in res)
    print(f"all SURF-on veto steps: {V}; every blocker in cols 6-9 moving away (ground truth): {H} ({H/V:.1%});"
          f" up unit would turn on if U(above) were off: {sum(r['cf_up'] for r in res)}; harmless & cf up: {sum(r['harmless_cf_up'] for r in res)}")
    B = sum((Counter(r["blockers"]) for r in res), Counter())
    print("blocker cells (kind, col, dir):", B.most_common(12))
    print("per-episode (seed, d, window, classes):")
    for r in res: print("  ", r["seed"], r["d"], r["win"], r["win_cls"])
