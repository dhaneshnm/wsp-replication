# Gold capture rate (identity-tracked spawns), score per step, episode-length stats for both nets (seeds 0..199).
import sys, os, pickle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vlib import *
for name in ("claude", "astra"):
    res = pickle.load(open(f"my_inst_{name}.pkl", "rb"))
    gs = sum(R["gold_spawned"] for R in res); gi = sum(R["gold_in_flight"] for R in res)
    got = sum(R["score"] for R in res); L = np.array([R["steps"] for R in res]); S = np.array([R["score"] for R in res])
    # per-episode capture rate too
    per = np.array([R["score"] / R["gold_spawned"] for R in res if R["gold_spawned"]])
    print(f"{name}: gold spawned {gs}, collected {got:.0f}, capture {got/gs:.3f}; excl. {gi} still on board at end {got/(gs-gi):.3f}; "
          f"mean per-episode capture {per.mean():.3f}; score/step {S.sum()/L.sum():.4f}; length mean {L.mean():.1f} median {np.median(L):.1f}; "
          f"enemies spawned {sum(R['enemy_spawned'] for R in res)}")
