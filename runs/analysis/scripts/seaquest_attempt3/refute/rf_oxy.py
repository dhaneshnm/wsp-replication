import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication"); sys.path.insert(0, "/private/tmp/claude-501/-Users-dhaneshneelamana-projects-wsp-replication/1de9272e-bb08-4c08-9f63-28011de783b7/scratchpad/analysis/seaquest_attempt3/refute")
import wsp, rf_runner as R, pickle, numpy as np
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
def analyse(seed):
    net = wsp.load_npz(R.CLAUDE)
    o = R.run(net, seed, detail=True)
    W = o["win"]
    res = dict(seed=seed, cause=o["cause"], d=o["d_end"], steps=o["steps"], score=o["score"],
               o_last=W[-1]["o"], d_last_pre=W[-1]["d"], y_last_pre=W[-1]["y"], y_end=o.get("y_end"))
    # final contiguous SURF window
    t = len(W) - 1
    cat = Counter(); argmax_up = 0; n_win = 0
    if W[t]["h1"][26] > 0:
        while t > 0 and W[t - 1]["h1"][26] > 0: t -= 1
        for s in W[t:]:
            row, h1, h2 = s["y"], s["h1"], s["h2"]
            up_on = h2[row - 1] > 0 if row >= 1 else False
            dn_on = h2[8 + row] > 0 if row <= 7 else False
            if row == 0: c = "at row 0"
            elif up_on and not dn_on: c = "up chosen"
            elif up_on and dn_on: c = "up/down tie"
            elif dn_on: c = "pushed down"
            elif row >= 2 and h1[17 + row - 2] > 0: c = "up vetoed by U(row above)"
            elif row == 1 and h1[25] < 0: c = "row1 blocked (HD off)"
            else: c = "other"
            cat[c] += 1; n_win += 1; argmax_up += int(np.argmax(s["z"]) == 2)
        res.update(win_onset_row=W[t]["y"], win_len=len(W) - t)
    res.update(cat=dict(cat), n_win=n_win, argmax_up=argmax_up)
    # all SURF-on veto steps (analyst's veto_content definition) with ground-truth directions
    nveto = 0; all_away = 0; kinds = Counter(); subcol = Counter()
    for s in W:
        h1, h2, row = s["h1"], s["h2"], s["y"]
        if h1[26] <= 0 or row < 2 or h2[row - 1] > 0 or h1[17 + row - 2] <= 0: continue
        nveto += 1; above = row - 1; away = True; subcol[s["x"]] += 1
        for c in range(6, 10):
            if s["g_danger"][above, c] > 0:
                objs = [ob for ob in s["objs"] if ob[0] == c and ob[1] == above]
                for ob in objs:
                    kind = "bullet" if ob[3] == "bullet" else "enemy"
                    kinds[(kind, c, "R" if ob[2] else "L")] += 1
                    if not ((c <= 7 and not ob[2]) or (c == 9 and ob[2])): away = False
                if not objs: kinds[("?", c, "?")] += 1; away = False
        all_away += away
    res.update(nveto=nveto, all_away=all_away, kinds=dict(kinds), subcol=dict(subcol))
    return res
if __name__ == "__main__":
    mine = pickle.load(open("rf_claude.pkl", "rb"))
    an = pickle.load(open("/private/tmp/claude-501/-Users-dhaneshneelamana-projects-wsp-replication/1de9272e-bb08-4c08-9f63-28011de783b7/scratchpad/analysis/seaquest_attempt3/claude_200.pkl", "rb"))
    seeds = sorted({r["seed"] for r in mine if r["cause"] == "oxygen"} | {r["seed"] for r in an if r["cause"] == "oxygen"})
    print("union of oxygen seeds (mine | analyst):", len(seeds))
    with ProcessPoolExecutor(4) as ex:
        res = list(ex.map(analyse, seeds))
    pickle.dump(res, open("rf_oxy.pkl", "wb"))
    for r in res: print("  seed", r["seed"], "my cause", r["cause"], "o_last(pre)", r["o_last"], "d pre", r["d_last_pre"], "d post", r["d"], "row pre", r["y_last_pre"], "row post", r["y_end"])
    res = [r for r in res if r["o_last"] <= 0]
    print("episodes whose final step began with oxygen <= 0:", len(res), "; pre-step divers>=1:", sum(r["d_last_pre"] >= 1 for r in res), "; post-step divers>=1:", sum(r["d"] >= 1 for r in res))
    for r in res: r["d"] = r["d_last_pre"]
    print("oxygen-death seeds:", len(res), " d>=1:", sum(r["d"] >= 1 for r in res))
    tot = Counter(); nw = 0; am = 0
    for r in res:
        tot.update(r["cat"]); nw += r["n_win"]; am += r["argmax_up"]
    print("final SURF window, all oxygen deaths with SURF on at death:", sum(r["n_win"] > 0 for r in res), "episodes; steps", nw, dict(tot))
    print("  'up vetoed' share:", tot["up vetoed by U(row above)"], "/", nw, "=", tot["up vetoed by U(row above)"] / max(1, nw), "; argmax==up on", am, "steps")
    d1 = [r for r in res if r["d"] >= 1]
    t1 = Counter(); n1 = 0
    for r in d1: t1.update(r["cat"]); n1 += r["n_win"]
    print("  restricted to d>=1 episodes:", len(d1), "steps", n1, dict(t1))
    per = [r["cat"].get("up vetoed by U(row above)", 0) / r["n_win"] for r in d1 if r["n_win"]]
    print("  per-episode vetoed share among d>=1: min %.2f median %.2f max %.2f; episodes with share>=0.87: %d" % (min(per), np.median(per), max(per), sum(p >= 0.87 for p in per)))
    nv = sum(r["nveto"] for r in d1); aw = sum(r["all_away"] for r in d1); K = Counter(); SC = Counter()
    for r in d1: K.update(r["kinds"]); SC.update(r["subcol"])
    print("veto steps (all SURF-on, d>=1 oxygen deaths):", nv, " all danger cells moving away from col 8:", aw)
    print("  sub column during veto steps:", dict(SC))
    for k, v in K.most_common(10): print("   ", k, v)
