# Held-out seeds 200..399: baseline vs the rebuilt lookahead patch (w=1.25), both via wsp.evaluate.
import sys, os, copy
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vlib import *
if __name__ == "__main__":
    base = nets()["claude"]; P = copy.deepcopy(base); w = 1.25
    for y in range(1, 9):
        if y >= 3: P["W2"][13 + y, 7 + y] += w; P["W2"][5 + y, 7 + y] += w; P["b2"][7 + y] += 2 * w
        if y <= 6: P["W2"][17 + y, 15 + y] += w; P["W2"][9 + y, 15 + y] += w; P["b2"][15 + y] += 2 * w
    for nm, n in (("baseline", base), ("patched", P)):
        print(nm, "seeds 200..399:", wsp.evaluate(n, "asterix", episodes=200, base_seed=200, workers=4), flush=True)
