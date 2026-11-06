import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import wsp
BASE = "/Users/dhaneshneelamana/projects/wsp-replication/runs/cap128k/claude-opus-5-5/seaquest/attempt%d/net.npz"
if __name__ == "__main__":
    for k in (1, 2):
        net = wsp.load_npz(BASE % k)
        m = {n: v.copy() for n, v in net.items()}
        m["b3"][1] = -100.0; m["b3"][3] = -100.0   # left/right never sampled (copy in memory only)
        r = wsp.evaluate(m, "seaquest", episodes=200, workers=4)
        print(f"attempt{k} left/right masked (b3[1]=b3[3]=-100), seeds 0-199: mean {r['mean']:.2f} se {r['se']:.2f} mean_len {r['mean_length']:.1f}")
