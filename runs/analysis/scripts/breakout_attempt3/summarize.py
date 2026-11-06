import json, sys, numpy as np, collections
for which in ["claude", "astra"]:
    res = json.load(open(f"rallies_{which}.json"))
    sc = np.array([e["score"] for e in res]); ln = np.array([e["steps"] for e in res])
    capped = ln >= 10000
    R = [r for e in res for r in e["rallies"]]
    M = [r for r in R if r["missed"]]
    print(f"===== {which}: {len(res)} eps, mean {sc.mean():.1f}, median {np.median(sc):.0f}, mean len {ln.mean():.0f}, capped {capped.sum()} (mean score capped {sc[capped].mean() if capped.any() else float('nan'):.1f}, uncapped {sc[~capped].mean():.1f})")
    print(f"  points/step {sc.sum()/ln.sum():.4f}; rallies {len(R)}; misses {len(M)}; P(miss per rally) {len(M)/len(R):.4f}; steps per rally {ln.sum()/len(R):.1f}; points per rally {sc.sum()/len(R):.3f}")
    print(f"  score quantiles 10/25/50/75/90: {np.percentile(sc,[10,25,50,75,90]).round(0).tolist()}; episodes with score<30: {(sc<30).sum()}")
    print(f"  direction-sign errors (H or V vs true ball_dir): {sum(e['dirwrong_frames'] for e in res)} of {sum(e['frames'] for e in res)} frames; sticky-changed actions {sum(e['sticky_changed'] for e in res)}")
    # slack at rally start and at start of final descent
    s0 = collections.Counter(); s0m = collections.Counter()
    for r in R:
        b = min(r["slack0"], 12); s0[b] += 1; s0m[b] += r["missed"]
    print("  rally-start slack (actions - distance to catch cells): " + ", ".join(f"{k}:{s0m[k]}/{s0[k]}" for k in sorted(s0)))
    ds = collections.Counter(); dsm = collections.Counter()
    for r in R:
        b = max(min(r["desc_slack"], 8), -3); ds[b] += 1; dsm[b] += r["missed"]
    print("  slack at first frame of final descent, misses/rallies: " + ", ".join(f"{k}:{dsm[k]}/{ds[k]}" for k in sorted(ds)))
    # waste decomposition in missed rallies
    W = collections.Counter()
    for r in M:
        for k, v in r["waste"].items(): W[k] += v
    Wall = collections.Counter()
    for r in R:
        for k, v in r["waste"].items(): Wall[k] += v
    print("  waste steps in MISSED rallies by cause:", dict(W), "| in all rallies:", dict(Wall))
    if M and M[0].get("greedy_catch") is not None:
        g = sum(1 for r in M if r["greedy_catch"])
        print(f"  greedy no-sticky replay of missed rallies catches the ball in {g}/{len(M)}")
    # cause classes for misses
    cls = collections.Counter()
    for r in M:
        w = r["waste"]
        if r["slack0"] < 0: c = "unreachable from rally start"
        elif w["sticky"] == 0 and w["sampling"] == 0: c = "policy only (no sticky/sampling waste)"
        elif w["policy"] == 0: c = "noise only (sticky/sampling)"
        else: c = "policy + noise"
        cls[c] += 1
    print("  miss classes:", dict(cls))
    print("  desc_row at final descent start among misses:", dict(collections.Counter(r["desc_row"] for r in M)))
    print("  bricks remaining at miss:", np.percentile([r["bricks"] for r in M], [10,50,90]).tolist() if M else None)
    print("  final distance at miss:", dict(collections.Counter(r["final_dist"] for r in M)))
