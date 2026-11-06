import sys, time
sys.path.insert(0, "/private/tmp/claude-501/-Users-dhaneshneelamana-projects-wsp-replication/1de9272e-bb08-4c08-9f63-28011de783b7/scratchpad/analysis/breakout_attempt2/verify")
from vcommon import *
if __name__ == "__main__":
    t = time.time()
    r = wsp.evaluate(wsp.load_npz(CLAUDE), "breakout", episodes=200, base_seed=200, workers=4)
    print("wsp.evaluate claude seeds 200-399:", {k: round(v, 2) for k, v in r.items()}, f"[{time.time()-t:.0f}s]")
