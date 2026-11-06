import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# check that a logging replica of wsp.play_episode reproduces its scores, and that sim_landing predicts real landings
from common import *
from play_log import run_episode
net = wsp.load_npz(CLAUDE)
for s in range(5):
    a = wsp.play_episode(net, "breakout", s)[:2]
    b = run_episode(net, s)
    print(s, "wsp", a, "replica", (b["score"], b["steps"]), "landing-pred mismatches:", b["pred_mismatch"], "of", b["n_landings"])
