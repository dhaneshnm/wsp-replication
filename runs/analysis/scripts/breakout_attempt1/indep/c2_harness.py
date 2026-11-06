# Claim 2: harness evaluate (200 eps, 4 workers) + per-episode harness play_episode for comparison with replay.py
import sys
sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import pickle
import numpy as np
import wsp
from concurrent.futures import ProcessPoolExecutor

N = "/Users/dhaneshneelamana/projects/wsp-replication/runs/claude-opus-5-5/breakout/attempt1/net.npz"


def one(args):
    net, s = args
    sc, st, _ = wsp.play_episode(net, "breakout", s)
    return s, sc, st


if __name__ == "__main__":
    net = wsp.load_npz(N)
    r = wsp.evaluate(net, "breakout", episodes=200, workers=4)
    print("wsp.evaluate 200 eps:", r)
    with ProcessPoolExecutor(4) as ex:
        per = list(ex.map(one, [(net, s) for s in range(200)], chunksize=10))
    pickle.dump(per, open("harness_per_episode.pkl", "wb"))
    sc = np.array([p[1] for p in per]); st = np.array([p[2] for p in per])
    print("wsp.play_episode per-episode: mean", sc.mean(), "mean_len", st.mean())
    rep = pickle.load(open("claude_softmax_0.1.pkl", "rb"))
    d_sc = sum(int(p[1] != q["score"]) for p, q in zip(per, rep))
    d_st = sum(int(p[2] != q["steps"]) for p, q in zip(per, rep))
    print("episodes where replay.py differs from harness: score", d_sc, "steps", d_st)
