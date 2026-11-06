import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import pickle, collections, numpy as np
BY, BX, LY, LX, D, POS, A, HS, VS, EFF, POSA, DONE, R = range(13)
for which in ["claude", "astra"]:
    res = pickle.load(open(f"play_{which}_200.pkl", "rb"))
    sc = np.array([e["score"] for e in res]); ln = np.array([e["steps"] for e in res])
    Rl = [r for e in res for r in e["rallies"]]; M = [r for r in Rl if r["missed"]]
    print(f"===== {which}: frames {ln.sum()} score sum {sc.sum()} points/step {sc.sum()/ln.sum():.5f}; rallies {len(Rl)} misses {len(M)} miss/rally {len(M)/len(Rl):.5f}")
    print("  terminal episodes:", int((ln < 10000).sum()), "capped:", int((ln >= 10000).sum()))
    de = collections.Counter()
    for e in res: de.update(e["dirwrong"])
    print("  direction misreads:", sum(de.values()), "of", ln.sum(), dict(de.most_common()))
    walk = sum(1 for r in Rl if any(ev[0] == "walk" for ev in r["ev"]))
    print("  rallies with a walk nx8->x8 in final descent:", walk, "of", len(Rl))
    pol = sum(1 for r in Rl if any(ev[0] == "exit_policy" for ev in r["ev"]))
    print("  rallies with policy exit from catch set in final descent:", pol)
    tr = collections.Counter(r["turn_row"] for r in Rl)
    print("  turn rows:", dict(sorted(tr.items())))
    if which == "claude":
        ue = collections.Counter(r["up_target"] - r["x8"] for r in Rl if r.get("up_target") is not None)
        n_ue = sum(ue.values())
        print("  up-target - x8 at last rising frame (net believes rising):", n_ue, "rallies;", sorted(ue.items()))
        print("     |err|==2:", ue[2]+ue[-2], "|err|==1:", ue[1]+ue[-1], "0:", ue[0])
        for row in sorted(tr):
            c = collections.Counter(r["up_target"] - r["x8"] for r in Rl if r.get("up_target") is not None and r["turn_row"] == row)
            print(f"     turn row {row}: {sorted(c.items())}")
        nn = sum(1 for r in Rl if r["fd"] > 0 and r.get("up_target") is None)
        print("  rallies with fd>0 but net not believing rising at last rising frame:", nn, "; rallies with fd==0:", sum(1 for r in Rl if r["fd"] == 0))
    # slack after the turn: desc_len - |pos - x8| and desc_len - catch-set distance
    s_x8 = collections.Counter(); s_cs = collections.Counter()
    for r in Rl:
        a = r["desc_len"] - abs(r["desc_pos"] - r["x8"]); b = r["desc_len"] - min(abs(r["desc_pos"] - r["x8"]), abs(r["desc_pos"] - r["nx8"]))
        s_x8[a] += 1; s_cs[b] += 1
    print("  desc slack vs x8 <3:", sum(v for k, v in s_x8.items() if k < 3), sorted((k, v) for k, v in s_x8.items() if k < 3))
    print("  desc slack vs catch set <3:", sum(v for k, v in s_cs.items() if k < 3), sorted((k, v) for k, v in s_cs.items() if k < 3))
