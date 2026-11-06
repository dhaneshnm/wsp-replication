"""Claim 2: per-seed comparison of the analyst's traced pickles (trace.run) with wsp.play_episode, seeds 0..199,
plus a direct trace.run vs wsp.play_episode check on seeds 600..611 (outside the analyst's 0..7)."""
import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
AN = "/private/tmp/claude-501/-Users-dhaneshneelamana-projects-wsp-replication/1de9272e-bb08-4c08-9f63-28011de783b7/scratchpad/analysis/seaquest_attempt3/"
IN = AN + "indep/"
sys.path.insert(0, IN)
import pickle, numpy as np, wsp, myrun
for name in ["claude", "astra"]:
    off = {s: (sc, st) for s, sc, st in pickle.load(open(IN + f"{name}_official.pkl", "rb"))}
    mine = {r["seed"]: (r["score"], r["steps"]) for r in pickle.load(open(IN + f"{name}_0.1.pkl", "rb"))}
    ana = {r["seed"]: (r["score"], r["steps"]) for r in pickle.load(open(AN + f"{name}_200.pkl", "rb"))}
    mism_ana = [s for s in off if off[s] != ana.get(s)]
    mism_mine = [s for s in off if off[s] != mine.get(s)]
    print(name, "seeds", len(off), "analyst-pickle mismatches vs play_episode:", len(mism_ana), mism_ana[:5],
          "| my-runner mismatches:", len(mism_mine), "| seed1 official", off[1], "analyst", ana[1])
if len(sys.argv) > 1:
    sys.path.insert(0, AN)
    import trace as T
    net = wsp.load_npz(myrun.CLAUDE)
    for s in range(600, 612):
        a = tuple(wsp.play_episode(net, "seaquest", s)[:2]); b = T.run(net, s)
        print(s, a, (b["score"], b["steps"]), "equal" if a == (b["score"], b["steps"]) else "DIFF")
