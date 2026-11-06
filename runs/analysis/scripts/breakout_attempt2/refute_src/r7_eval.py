import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import wsp
if __name__ == "__main__":
    for name, path in [("claude", "/Users/dhaneshneelamana/projects/wsp-replication/runs/claude-opus-5-5/breakout/attempt2/net.npz"),
                       ("astra", "/Users/dhaneshneelamana/lm_understand-logs/exp5_write_from_scratch/networks/breakout/hand.npz"),
                       ("v_rows678", "v_rows678.npz")]:
        r = wsp.evaluate(wsp.load_npz(path), "breakout", episodes=200, base_seed=200, workers=4)
        print(name, "seeds 200-399:", {k: round(v, 2) for k, v in r.items()}, flush=True)
