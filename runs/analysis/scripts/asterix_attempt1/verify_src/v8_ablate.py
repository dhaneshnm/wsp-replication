"""Re-implement the A1+A2 edit (row r-2 danger into up-unit, r+2 into down-unit, w=0.3; row r+-2 gold, w=0.15) on a COPY,
evaluate on seeds 0..199 (reproduction) and 200..399 (held-out), with base and Astra on 200..399."""
import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import copy, numpy as np, wsp
BASE = wsp.load_npz("/Users/dhaneshneelamana/projects/wsp-replication/runs/claude-opus-5-5/asterix/attempt1/net.npz")
ASTRA = wsp.load_npz("/Users/dhaneshneelamana/lm_understand-logs/exp5_write_from_scratch/networks/asterix/hand.npz")
D0, G0 = np.tanh(-1.2), np.tanh(-1.0)
def variant(sw, gw):
    n = copy.deepcopy(BASE)
    for r in range(1, 9):
        up, dn = 3 * (r - 1) + 1, 3 * (r - 1) + 2
        if r >= 3:   # target row r-2 -> D unit r-3, G unit 16+r-3
            n["W2"][r - 3, up] += sw; n["b2"][up] -= sw * D0
            n["W2"][16 + r - 3, up] -= gw; n["b2"][up] += gw * G0
        if r <= 6:   # target row r+2 -> D unit r+1
            n["W2"][r + 1, dn] += sw; n["b2"][dn] -= sw * D0
            n["W2"][16 + r + 1, dn] -= gw; n["b2"][dn] += gw * G0
    return n
if __name__ == "__main__":
  v = variant(0.3, 0.15)
  for name, net, base_seed in [("A1+A2 seeds 0-199", v, 0), ("A1+A2 seeds 200-399", v, 200),
                                ("base seeds 200-399", BASE, 200), ("astra seeds 200-399", ASTRA, 200)]:
      r = wsp.evaluate(net, "asterix", episodes=200, base_seed=base_seed, workers=4)
      print(f"{name:24s} mean {r['mean']:.2f} se {r['se']:.2f} len {r['mean_length']:.1f}", flush=True)
