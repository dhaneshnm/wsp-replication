import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import numpy as np, wsp, json

def main():
    game, N, base = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    net = wsp.load_npz(f"/Users/dhaneshneelamana/lm_understand-logs/exp5_write_from_scratch/networks/{game}/hand.npz")
    r = wsp.evaluate(net, game, episodes=N, base_seed=base)
    pub = json.load(open("/Users/dhaneshneelamana/lm_understand-logs/exp5_write_from_scratch/eval/minatar_eval.json"))[game]["hand"]
    z = (r["mean"] - pub["mean"]) / np.hypot(r["se"], pub["se"])
    print(f"{game} seeds {base}..{base+N-1}: {r}  | published mean {pub['mean']} se {pub['se']:.2f} max {pub['max']} len {pub['mean_length']}  z={z:+.2f}")

if __name__ == "__main__":
    main()
