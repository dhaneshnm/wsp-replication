# In-play analysis of a replay.py pickle: gate errors, catch types, misses, on-target no-op probs, loops.
# usage: analyze.py PICKLE NET_PATH
import sys
sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import pickle
from collections import Counter
import numpy as np
import wsp

res = pickle.load(open(sys.argv[1], "rb"))
net = wsp.load_npz(sys.argv[2])
VX = np.array([-1, 1, 1, -1]); VY = np.array([-1, -1, 1, 1])
tot = Counter(); gV_cat = Counter(); gH_cat = Counter()
harm_diff_argmax = 0; harm_maxdp = 0.0
p0_on = []; pL_on = []; pR_on = []
for r in res:
    n = len(r["by"])
    vx = VX[r["d"]]; vy = VY[r["d"]]
    gH = np.sign(r["h4"]); gV = np.sign(r["h5"])
    dy = r["by"] - r["ly"]; dx = r["bx"] - r["lx"]
    prev_catch = np.concatenate([[0], r["catch"][:-1]])
    tot["steps"] += n
    eH = gH != vx; eV = gV != vy
    tot["gH_err"] += int(eH.sum()); tot["gV_err"] += int(eV.sum())
    for i in np.nonzero(eV)[0]:
        gV_cat[(int(r["by"][i]), int(dy[i]), "true_up" if vy[i] < 0 else "true_down")] += 1
    for i in np.nonzero(eH)[0]:
        gH_cat[("row8_after_catch" if (r["by"][i] == 8 and prev_catch[i] > 0) else f"other r={r['by'][i]} dx={dx[i]} dy={dy[i]}")] += 1
    # harmlessness of gH errors at row-8 post-catch frames: flip h4 to the true sign, recompute output
    for i in np.nonzero(eH & (r["by"] == 8) & (prev_catch > 0))[0]:
        x = np.zeros(600, np.float32)
        x[(r["by"][i] * 10 + r["bx"][i]) * 6 + 3] = 1; x[(90 + r["pos"][i]) * 6] = 1; x[(r["ly"][i] * 10 + r["lx"][i]) * 6 + 4] = 1
        h1 = np.tanh(x @ net["W1"] + net["b1"])
        def out(h):
            z = np.tanh(h @ net["W2"] + net["b2"]) @ net["W3"] + net["b3"]
            p = np.exp(z - z.max()); return p / p.sum()
        p_a = out(h1); h1b = h1.copy(); h1b[4] = -h1b[4]; p_b = out(h1b)
        harm_diff_argmax += int(np.argmax(p_a) != np.argmax(p_b)); harm_maxdp = max(harm_maxdp, float(np.abs(p_a - p_b).max()))
    # catches
    c = r["catch"]
    idx = np.nonzero(c)[0]
    tot["catches"] += len(idx)
    tot["catch_branch_under_ball"] += int((c == 1).sum()); tot["catch_branch_landing_col"] += int((c == 2).sum())
    for i in idx:
        if i + 1 < n:
            if VX[r["d"][i + 1]] == VX[r["d"][i]]: tot["catch_same_vx"] += 1
            else: tot["catch_reversed_vx"] += 1
    on = r["amax"] == 0
    p0_on.append(r["p0"][on]); pL_on.append(r["pL"][on]); pR_on.append(r["pR"][on])
    tot["deviate_sampled"] += int((r["asamp"] != r["amax"]).sum())
    tot["deviate_sticky"] += int((r["aexec"] != r["asamp"]).sum())
print("steps", tot["steps"], " gH errors", tot["gH_err"], " gV errors", tot["gV_err"])
print("gV error categories (row, dy, true dir):", gV_cat.most_common(10))
print("gH error categories:", gH_cat.most_common(6))
print("row-8 post-catch gH-error frames: argmax changes if gH corrected:", harm_diff_argmax, " max |dp|:", harm_maxdp)
print("catches", tot["catches"], " branch ball_x==pos (paddle under row-8 ball):", tot["catch_branch_under_ball"],
      " branch new_x==pos (landing col):", tot["catch_branch_landing_col"])
print("catches by horizontal dir change: same", tot["catch_same_vx"], " reversed", tot["catch_reversed_vx"])
p0 = np.concatenate(p0_on); pL = np.concatenate(pL_on); pR = np.concatenate(pR_on)
print(f"argmax==noop steps {len(p0)} ({len(p0)/tot['steps']:.3f}); p(noop) min {p0.min():.5f} median {np.median(p0):.5f} max {p0.max():.6f} mean {p0.mean():.5f}; mean pL {pL.mean():.5f} mean pR {pR.mean():.5f}")
print("p(noop) on-target value counts (rounded 4dp):", Counter(np.round(p0, 4).tolist()).most_common(5))
print("executed!=argmax via sampling:", tot["deviate_sampled"], " executed!=sampled via sticky:", tot["deviate_sticky"])
sc = np.array([r["score"] for r in res])
print(f"score mean {sc.mean():.4f} misses {sum(r['done'] for r in res)} max {sc.max()} mean_len {np.mean([r['steps'] for r in res]):.2f}")
# misses
mc = Counter()
for r in res:
    if r["done"]:
        m = r["miss"]
        if not m["cf_rally_start_catches"]:
            mc["pure argmax from rally start also misses (policy error)"] += 1
        else:
            mc[f"noise: decisive deviation = {m['decisive']['kind']}"] += 1
print("miss attribution:", dict(mc))
# reward droughts / loops
first_drought_score = []; escaped = 0; stuck21 = 0
for r in res:
    rt = np.nonzero(r["r"])[0]
    cum = np.cumsum(r["r"])
    # first >=300-step stretch without reward
    times = np.concatenate([[-1], rt, [len(r["r"])]])
    gaps = np.diff(times)
    k = np.nonzero(gaps > 300)[0]
    if len(k) and times[k[0]] + 301 <= len(r["r"]):
        s0 = int(cum[times[k[0]]]) if times[k[0]] >= 0 else 0
        first_drought_score.append(s0)
        if s0 == 21:
            stuck21 += 1
            if r["score"] > 21: escaped += 1
    else:
        first_drought_score.append(-1)
print("score at start of first >300-step reward drought (-1 = none):", Counter(first_drought_score).most_common(8))
print(f"episodes whose first >300-step drought started at score 21: {stuck21}; of those final score > 21: {escaped}")
