import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import wsp
if __name__ == "__main__":
    for name, p in [("claude", "/Users/dhaneshneelamana/projects/wsp-replication/runs/claude-opus-5-5/asterix/attempt2/net.npz"),
                    ("astra", "/Users/dhaneshneelamana/lm_understand-logs/exp5_write_from_scratch/networks/asterix/hand.npz")]:
        print(name, wsp.evaluate(wsp.load_npz(p), "asterix", episodes=200, workers=4))
