# Claim 9: what does a larger margin do to the score? Scale the output layer (W3, b3) by k (all logit gaps x k).
import sys
sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import numpy as np, wsp
if __name__ == "__main__":
    base = wsp.load_npz("/Users/dhaneshneelamana/projects/wsp-replication/runs/claude-opus-5-5/breakout/attempt1/net.npz")
    for k in (5.0,):
        v = {a: b.copy() for a, b in base.items()}
        v["W3"] *= k; v["b3"] *= k
        print("output layer x", k, wsp.evaluate(v, "breakout", episodes=200, workers=4))
